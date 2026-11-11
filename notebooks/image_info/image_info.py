#!/usr/bin/env python3
"""Record and show the build lineage of this image.

  image_info                  summary and build chain
  image_info --json           raw JSON
  image_info --field NAME     one field of the current image (for scripts)
  image_info record ...       build time: append this image to the chain

Runs inside the image with the image's own Python (3.10+), standard library only.
Tags are deliberately not recorded: they are assigned (and moved) in the registry
after the build, so the image can't know them.

Installed packages are not recorded either: the package managers know them best
(`mamba list`, `pip list`, `dpkg -l`). The README shows how to diff two images.
"""

import argparse
import json
import os
import platform
import sys
import tempfile
from datetime import datetime, timezone

INFO_FILE = os.environ.get("IMAGE_INFO_FILE", "/etc/image-info.json")


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


def print_table(rows, indent=""):
    """Print rows as left-aligned columns; rows may have different lengths."""
    columns = max(len(row) for row in rows)
    rows = [row + [""] * (columns - len(row)) for row in rows]
    widths = [max(len(row[i]) for row in rows) for i in range(columns)]
    for row in rows:
        line = "  ".join(cell.ljust(width) for cell, width in zip(row, widths))
        print((indent + line).rstrip())


def record(args):
    data = load()
    entry = {
        "name": args.name,
        "parent": args.parent,
        "git_commit": args.git_commit,
        "built_at": args.build_date
        or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "os": os_release(),
        "python": platform.python_version(),
    }
    data["chain"].append({key: value for key, value in entry.items() if value})
    save(data)


def show(args):
    data = load()
    if args.json:
        print(json.dumps(data, indent=2))
        return
    chain = data["chain"]
    if not chain:
        sys.exit(f"No image info found ({INFO_FILE}).")

    current = chain[-1]
    if args.field:
        print(current.get(args.field, ""))
        return

    rows = [
        ["Image:", current.get("name", "?")],
        ["Built:", current.get("built_at", "?")],
    ]
    for label, key in [("Commit:", "git_commit"), ("OS:", "os"), ("Python:", "python")]:
        if current.get(key):
            rows.append([label, current[key]])
    print_table(rows)

    print("\nBuild chain (base -> current):")
    rows = [["·", chain[0].get("parent", "?"), "[external base]"]]
    for number, entry in enumerate(chain, 1):
        commit = entry.get("git_commit", "")
        rows.append(
            [
                str(number),
                entry.get("name", "?"),
                f"built {entry.get('built_at', '?')}",
                f"git {commit[:7]}" if commit else "",
            ]
        )
    print_table(rows, indent="  ")


def main():
    p = argparse.ArgumentParser(description="Show the build lineage of this image.")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--field", help="print one field of the current image")
    sub = p.add_subparsers(dest="cmd")

    r = sub.add_parser("record", help="append this build to the chain (build time)")
    r.add_argument("--name", required=True)
    r.add_argument("--parent", required=True)
    r.add_argument("--git-commit")
    r.add_argument("--build-date")

    args = p.parse_args()
    record(args) if args.cmd == "record" else show(args)


if __name__ == "__main__":
    main()
