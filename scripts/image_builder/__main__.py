"""image_builder: builds, tags and publishes the tree of notebook images defined
in notebooks.toml, in dependency order, locally and in CI.

Usage:
    python scripts/image_builder <command> [options]

This file only parses arguments and calls into the modules next to it.
Running the folder executes this file, and Python puts the folder on sys.path,
which is why the modules are imported flat (`import manifest`).
"""

import argparse
import sys
from pathlib import Path

import manifest
import tree

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "notebooks.toml"

EXAMPLES = """\
examples:
  python scripts/image_builder tree       show which image builds on which
  python scripts/image_builder tree -h    help for a single command
"""


def main(argv: list[str] | None = None) -> int:
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
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help(sys.stderr)
        return 2  # usage error (argparse convention), so a CI step without a command fails

    try:
        loaded = manifest.load(MANIFEST_PATH)
    except manifest.ManifestError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.command == "tree":
        print(tree.render(loaded))
    return 0


if __name__ == "__main__":
    sys.exit(main())
