#!/usr/bin/env python3
"""Record and show the build lineage and installed packages of this image.

  image_info                  summary and build chain
  image_info --json           raw JSON
  image_info --field NAME     one field of the current image (for scripts)
  image_info packages         installed packages: source, name, version (tab-separated)
  image_info baseline ...     build time: snapshot the external base image
  image_info record ...       build time: append this image to the chain

Runs inside the image with the image's own Python (3.10+), standard library only.
Tags are deliberately not recorded: they are assigned (and moved) in the registry
after the build, so the image can't know them.
"""

import argparse
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

INFO_FILE = os.environ.get("IMAGE_INFO_FILE", "/etc/image-info.json")


# --------------------------------------------------------------------------- #
#   Installed packages                                                         #
# --------------------------------------------------------------------------- #


def normalize(name):
    """PyPI name normalization (PEP 503): `Foo_Bar` and `foo.bar` -> `foo-bar`."""
    return re.sub(r"[-_.]+", "-", name).lower()


def python_packages():
    """Python packages grouped by the tool that installed them (pip, uv, ...).

    Packages installed by conda are skipped: they are listed under conda already.
    """
    groups = {}
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        if not name:
            continue
        installer = (dist.read_text("INSTALLER") or "").strip() or "unknown"
        if installer == "conda":
            continue
        # The first match on sys.path wins, same as for `import`.
        groups.setdefault(installer, {}).setdefault(normalize(name), dist.version)
    return groups


def conda_packages(prefix=sys.prefix):
    """conda/mamba packages, read from the environment's conda-meta/ records."""
    packages = {}
    for path in sorted(Path(prefix, "conda-meta").glob("*.json")):
        record = json.loads(path.read_text())
        packages[record["name"]] = record["version"]
    return packages


def apt_packages():
    """Installed Debian packages; empty if the image has no dpkg.

    Names without architecture (`libc6`, not `libc6:amd64`), so images built
    for different platforms can be diffed.
    """
    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f", "${db:Status-Abbrev}\t${Package}\t${Version}\n"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        return {}
    packages = {}
    for line in result.stdout.splitlines():
        status, name, version = line.split("\t")
        if status.startswith("ii"):  # skip removed packages that left config behind
            packages[name] = version
    return packages


def collect_packages():
    """All installed packages as {source: {name: version}}, empty sources left out."""
    sources = {"conda": conda_packages(), "apt": apt_packages(), **python_packages()}
    return {source: packages for source, packages in sources.items() if packages}


# --------------------------------------------------------------------------- #
#   The info file                                                              #
# --------------------------------------------------------------------------- #


def load():
    try:
        with open(INFO_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"chain": []}


def save(data):
    # atomic write so a failed build step never leaves a half-written file
    directory = os.path.dirname(INFO_FILE) or "."
    fd, tmp = tempfile.mkstemp(dir=directory)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.chmod(tmp, 0o644)
    os.replace(tmp, INFO_FILE)


def os_release():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return None


def snapshot():
    """What the image looks like right now; part of every chain entry."""
    return {
        "os": os_release(),
        "python": platform.python_version(),
        "packages": collect_packages(),
    }


def drop_empty(entry):
    return {key: value for key, value in entry.items() if value}


# --------------------------------------------------------------------------- #
#   Commands                                                                   #
# --------------------------------------------------------------------------- #


def baseline(args):
    data = load()
    if data["chain"]:
        sys.exit(
            f"image_info: {INFO_FILE} already has a chain; "
            "`baseline` only belongs right after FROM <external base>"
        )
    data["chain"].append(
        drop_empty({"name": args.name, "external": True, **snapshot()})
    )
    save(data)


def record(args):
    data = load()
    entry = {
        "name": args.name,
        "parent": args.parent,
        "git_commit": args.git_commit,
        "built_at": args.build_date
        or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **snapshot(),
    }
    data["chain"].append(drop_empty(entry))
    save(data)


def list_packages(args):
    for source, packages in sorted(collect_packages().items()):
        for name, version in sorted(packages.items()):
            print(f"{source}\t{name}\t{version}")


def show(args):
    data = load()
    chain = data["chain"]
    if args.json:
        print(json.dumps(data, indent=2))
        return
    if not chain:
        print(f"No image info found ({INFO_FILE}).")
        sys.exit(1)

    current = chain[-1]
    if args.field:
        print(current.get(args.field, ""))
        return

    rows = [
        ("Image", current.get("name", "?")),
        ("Built", current.get("built_at", "?")),
    ]
    for label, key in [("Commit", "git_commit"), ("OS", "os"), ("Python", "python")]:
        if current.get(key):
            rows.append((label, current[key]))
    packages = current.get("packages", {})
    if packages:
        rows.append(
            (
                "Packages",
                ", ".join(
                    f"{len(pkgs)} {source}" for source, pkgs in sorted(packages.items())
                ),
            )
        )

    width = max(len(label) for label, _ in rows) + 2
    for label, value in rows:
        print(f"{label + ':':<{width}}{value}")

    print("\nBuild chain (base -> current):")
    first = chain[0]
    base = first["name"] if first.get("external") else first.get("parent", "?")
    print(f"  ·  {base}  [external base]")
    own = [entry for entry in chain if not entry.get("external")]
    width = max((len(entry.get("name", "?")) for entry in own), default=0)
    for i, entry in enumerate(own, 1):
        commit = f"  git {entry['git_commit']}" if entry.get("git_commit") else ""
        print(
            f"  {i}  {entry.get('name', '?'):<{width}}  "
            f"built {entry.get('built_at', '?')}{commit}"
        )


def main():
    p = argparse.ArgumentParser(description="Show the build lineage of this image.")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--field", help="print one field of the current image")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("packages", help="list installed packages (diff-friendly)")

    b = sub.add_parser("baseline", help="snapshot the external base (build time)")
    b.add_argument("--name", required=True, help="the external base image")

    r = sub.add_parser("record", help="append this build to the chain (build time)")
    r.add_argument("--name", required=True)
    r.add_argument("--parent", required=True)
    r.add_argument("--git-commit")
    r.add_argument("--build-date")

    args = p.parse_args()
    commands = {"packages": list_packages, "baseline": baseline, "record": record}
    commands.get(args.cmd, show)(args)


if __name__ == "__main__":
    main()
