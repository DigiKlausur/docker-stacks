"""image_builder: builds, tags and publishes the tree of notebook images defined
in notebooks.toml, in dependency order, locally and in CI.

Usage:
    python scripts/image_builder <command> [options]

This file only parses arguments, gathers inputs (git, clock) and calls into the
modules next to it. Running the folder executes this file, and Python puts the
folder on sys.path, which is why the modules are imported flat (`import manifest`).
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import manifest
import plan
import repo
import tree

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "notebooks.toml"

EXAMPLES = """\
examples:
  python scripts/image_builder tree
      show which image builds on which
  python scripts/image_builder plan --tag-set dev --since origin/dev
      what CI would build for the changes on your branch
  python scripts/image_builder plan --tag-set master --all
      plan a full rebuild
  python scripts/image_builder <command> -h
      help for a single command
"""


def main(argv: list[str] | None = None) -> int:
    parser = _make_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help(sys.stderr)
        return 2  # usage error (argparse convention), so a CI step without a command fails

    try:
        loaded = manifest.load(MANIFEST_PATH)
        if args.command == "tree":
            print(tree.render(loaded))
        elif args.command == "plan":
            print(json.dumps(_plan(loaded, args), indent=2))
    except (manifest.ManifestError, repo.RepoError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


def _plan(loaded: manifest.Manifest, args: argparse.Namespace) -> dict:
    if args.tag_set not in loaded.tag_sets:
        available = ", ".join(loaded.tag_sets)
        raise manifest.ManifestError(f"unknown tag set '{args.tag_set}' (available: {available})")

    if args.all:
        images = manifest.build_order(loaded.nodes)
    else:
        images = plan.select(loaded, repo.changed_files(REPO_ROOT, args.since))

    now = datetime.now(timezone.utc)
    return plan.summary(loaded.tag_sets[args.tag_set], images, repo.short_sha(REPO_ROOT), now)


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python scripts/image_builder",
        description="Build, tag and publish the notebook images defined in notebooks.toml.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,  # keep the epilog's line breaks
    )
    commands = parser.add_subparsers(dest="command", title="commands", metavar="<command>")

    commands.add_parser(
        "tree",
        help="show the image tree and validate notebooks.toml",
        description="Show the image tree. External base images are the roots; "
        "[e2x] marks images that also get e2xgrader variants.",
    )

    plan_parser = commands.add_parser(
        "plan",
        help="list the images to build and their tags (JSON)",
        description="Decide which images need to be built and resolve the tags for this run. "
        "Prints JSON and builds nothing.",
    )
    plan_parser.add_argument("--tag-set", required=True, help="tag set from notebooks.toml, e.g. dev or master")
    scope = plan_parser.add_mutually_exclusive_group(required=True)
    scope.add_argument(
        "--since",
        metavar="REF",
        help="images changed on this branch since REF (compared against the merge base); fails if REF is unknown",
    )
    scope.add_argument("--all", action="store_true", help="every image")
    return parser


if __name__ == "__main__":
    sys.exit(main())
