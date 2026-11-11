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
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import build
import generate
import manifest
import plan
import registry
import repo
import retag
import tree

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "notebooks.toml"
WORKFLOW_PATH = REPO_ROOT / ".github/workflows/build_all_images.yml"  # generated
README_PATH = REPO_ROOT / "README.md"  # its image tree is generated
LOCAL_TAG_SET = "local"  # tag set used by `build` on your machine

EXAMPLES = """\
examples:
  python scripts/image_builder tree
      show which image builds on which
  python scripts/image_builder build ml-notebook-student
      build one image locally (parent comes from the registry)
  python scripts/image_builder build datascience-notebook --with-dependents
      build an image and everything below it, each on its local parent
  python scripts/image_builder build minimal-notebook-exam --parent-tag local
      build on your locally built parent instead of the registry's 'latest'
  python scripts/image_builder build ml-notebook-exam --parent-tag dev-sha-a10dab6
      reproduce a CI build exactly (parent from that run)
  python scripts/image_builder build --all --dry-run
      print the commands for building every image
  python scripts/image_builder build ml-notebook --dry-run
      only print the docker command
  python scripts/image_builder plan --tag-set dev --since origin/dev
      what CI would build for the changes on your branch
  python scripts/image_builder plan --tag-set main --all
      plan a full rebuild
  python scripts/image_builder build ml-notebook --dry-run \\
      --plan "$(python scripts/image_builder plan --tag-set dev --all)"
      what CI would run for one image
  python scripts/image_builder generate
      update build_all_images.yml and the README tree after changing notebooks.toml
  python scripts/image_builder retag --from latest --to summer-2026
      give every image a fixed tag for a semester or an exam
  python scripts/image_builder <command> -h
      help for a single command
"""


def main(argv: list[str] | None = None) -> int:
    parser = _make_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help(sys.stderr)
        return (
            2  # usage error (argparse convention), so a CI step without a command fails
        )

    try:
        loaded = manifest.load(MANIFEST_PATH)
        if args.command == "tree":
            print(tree.render(loaded))
        elif args.command == "plan":
            # --compact: one line, as $GITHUB_OUTPUT expects name=value per line
            print(json.dumps(_plan(loaded, args), indent=None if args.compact else 2))
        elif args.command == "build":
            return _build(loaded, args)
        elif args.command == "generate":
            return _generate(loaded, check=args.check)
        elif args.command == "retag":
            return _retag(loaded, args)
        elif args.command == "complete-tags":
            return _complete_tags(loaded, args)
    except (
        manifest.ManifestError,
        repo.RepoError,
        build.BuildError,
        generate.GenerateError,
        retag.RetagError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


def _plan(loaded: manifest.Manifest, args: argparse.Namespace) -> dict:
    if args.tag_set not in loaded.tag_sets:
        available = ", ".join(loaded.tag_sets)
        raise manifest.ManifestError(
            f"unknown tag set '{args.tag_set}' (available: {available})"
        )

    if args.all:
        images = manifest.build_order(loaded.nodes)
    else:
        images = plan.select(loaded, repo.changed_files(REPO_ROOT, args.since))

    now = datetime.now(UTC)
    return plan.summary(
        loaded.tag_sets[args.tag_set], images, repo.short_sha(REPO_ROOT), now
    )


def _generate(loaded: manifest.Manifest, check: bool) -> int:
    expected = {
        WORKFLOW_PATH: generate.workflow(loaded),
        README_PATH: generate.readme_with_tree(
            README_PATH.read_text(), tree.render(loaded)
        ),
    }
    stale = [
        path
        for path, content in expected.items()
        if not path.exists() or path.read_text() != content
    ]

    if check:
        for path in stale:
            print(
                f"error: {path.relative_to(REPO_ROOT)} is out of date; "
                "run `python scripts/image_builder generate`",
                file=sys.stderr,
            )
        return 1 if stale else 0

    for path in stale:
        path.write_text(expected[path])
        print(f"updated {path.relative_to(REPO_ROOT)}")
    if not stale:
        print("everything is up to date")
    return 0


def _retag(loaded: manifest.Manifest, args: argparse.Namespace) -> int:
    retag.check_tags(loaded, args.from_tag, args.to_tags)
    pairs = retag.pairs(loaded, args.from_tag, args.to_tags)
    return _write_tags(
        pairs,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        rerun_hint="fix it and rerun with --overwrite",
    )


def _complete_tags(loaded: manifest.Manifest, args: argparse.Namespace) -> int:
    summary = build.parse_plan(args.plan)
    if not summary["images"]:
        print("nothing was built in this run, so no tags to complete", file=sys.stderr)
        return 0
    pairs = retag.completion_pairs(loaded, summary)
    if not pairs:
        print("every image was rebuilt, so no tags to complete", file=sys.stderr)
        return 0
    # Overwriting is expected here: a later run on the same day moves the date tag.
    return _write_tags(
        pairs, overwrite=True, dry_run=args.dry_run, rerun_hint="rerun the workflow"
    )


def _write_tags(
    pairs: list[tuple[str, list[str]]], overwrite: bool, dry_run: bool, rerun_hint: str
) -> int:
    if dry_run:
        for source, targets in pairs:
            print(shlex.join(retag.create_command(source, targets)))
        return 0

    # All or nothing: find every problem before writing a single tag.
    problems = _preflight(pairs, overwrite=overwrite)
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        print(f"error: {len(problems)} problem(s), no tag was written", file=sys.stderr)
        return 1

    for index, (source, targets) in enumerate(pairs, start=1):
        print(f"==> {index}/{len(pairs)} {source}", file=sys.stderr)
        cmd = retag.create_command(source, targets)
        returncode = subprocess.run(cmd, check=False).returncode
        if returncode != 0:
            print(
                f"error: tagging {source} failed after {index - 1} of {len(pairs)} "
                f"images; {rerun_hint}",
                file=sys.stderr,
            )
            return returncode
    return 0


def _preflight(pairs: list[tuple[str, list[str]]], overwrite: bool) -> list[str]:
    """Every source must exist; without --overwrite no target may exist yet."""
    target_count = 0 if overwrite else sum(len(targets) for _, targets in pairs)
    refs = len(pairs) + target_count
    print(f"checking {refs} image references in the registry ...", file=sys.stderr)
    problems = []
    for source, targets in pairs:
        if not registry.exists(source):
            problems.append(f"source missing: {source}")
        if not overwrite:
            problems += [
                f"target exists (use --overwrite to replace it): {target}"
                for target in targets
                if registry.exists(target)
            ]
    return problems


def _build_selection(loaded: manifest.Manifest, args: argparse.Namespace) -> set[str]:
    """The nodes `build` should build: everything, or one image (plus what's below it)."""
    if args.all:
        return set(loaded.nodes)
    if args.image not in loaded.nodes:
        raise build.BuildError(
            f"unknown image '{args.image}' (see `python scripts/image_builder tree`)"
        )
    selected = {args.image}
    if args.with_dependents:
        selected |= plan.descendants(loaded.nodes, selected)
    return selected


def _local_tag_set(loaded: manifest.Manifest) -> manifest.TagSet:
    tag_set = loaded.tag_sets.get(LOCAL_TAG_SET)
    if tag_set is None:
        raise build.BuildError(
            f"notebooks.toml needs a [tag_sets.{LOCAL_TAG_SET}] for local builds"
        )
    return tag_set


def _build(loaded: manifest.Manifest, args: argparse.Namespace) -> int:
    now = datetime.now(UTC)
    if args.plan is not None:
        if args.image is None or args.with_dependents:
            raise build.BuildError(
                "--plan builds exactly one image (no --all or --with-dependents)"
            )
        if args.parent_tag is not None:
            raise build.BuildError(
                "--parent-tag is for local builds; with --plan the plan sets parents"
            )
        run = build.ci_run(loaded, args.image, args.plan, push=args.push)
    else:
        if args.push:
            raise build.BuildError("--push needs --plan: pushing only happens in CI")
        run = build.local_run(
            loaded,
            _build_selection(loaded, args),
            _local_tag_set(loaded),
            repo.short_sha(REPO_ROOT),
            now,
            parent_tag=args.parent_tag,
        )

    labels = build.oci_labels(repo.full_sha(REPO_ROOT), now)
    build_args = build.parse_build_args(args.build_arg)
    commands = {
        name: build.command(loaded, loaded.nodes[name], run, labels, build_args)
        for name in run.names
    }

    if args.dry_run:
        for name, cmd in commands.items():
            print(f"# {name}\n{shlex.join(cmd)}")
        return 0

    for index, (name, cmd) in enumerate(commands.items(), start=1):
        print(f"==> {index}/{len(commands)} {name}", file=sys.stderr)
        # Folders in notebooks.toml are relative to the repo root.
        returncode = subprocess.run(cmd, check=False, cwd=REPO_ROOT).returncode
        if returncode != 0:
            remaining = len(commands) - index
            skipped = f"; {remaining} remaining image(s) not built" if remaining else ""
            print(f"error: building {name} failed{skipped}", file=sys.stderr)
            return returncode
    return 0


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python scripts/image_builder",
        description="Build, tag and publish the notebook images defined in notebooks.toml.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,  # keep the epilog's line breaks
    )
    commands = parser.add_subparsers(
        dest="command", title="commands", metavar="<command>"
    )

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
    plan_parser.add_argument(
        "--tag-set",
        required=True,
        help="tag set from notebooks.toml, e.g. dev or main",
    )
    scope = plan_parser.add_mutually_exclusive_group(required=True)
    scope.add_argument(
        "--since",
        metavar="REF",
        help="images changed on this branch since REF (compared against the merge base); fails if REF is unknown",
    )
    scope.add_argument("--all", action="store_true", help="every image")
    plan_parser.add_argument(
        "--compact", action="store_true", help="print the JSON on one line (for CI)"
    )

    generate_parser = commands.add_parser(
        "generate",
        help="write the files derived from notebooks.toml",
        description="Write .github/workflows/build_all_images.yml and the image tree "
        "in README.md from notebooks.toml.",
    )
    generate_parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; fail if a generated file is out of date (for CI)",
    )

    build_parser = commands.add_parser(
        "build",
        help="build images (locally, or in CI with --plan)",
        description="Build an image on your machine, optionally with everything below it. "
        "A parent built in the same call is used as ':local'; any other parent is pulled from "
        "the registry (tag 'latest'). Results are tagged ':local' and never pushed. "
        "In CI, --plan takes the JSON printed by `plan`: one image, with the plan's tags, "
        "pushed to every registry with --push.",
    )
    what = build_parser.add_mutually_exclusive_group(required=True)
    what.add_argument(
        "image",
        nargs="?",
        help="image name, e.g. ml-notebook or ml-notebook-student (see `tree`)",
    )
    what.add_argument(
        "--all", action="store_true", help="build every image, in build order"
    )
    build_parser.add_argument(
        "--with-dependents",
        action="store_true",
        help="also build every image below it (incl. e2x variants), each on its fresh :local parent",
    )
    build_parser.add_argument(
        "--parent-tag",
        metavar="TAG",
        help="tag of the parent to build on, instead of 'latest': e.g. 'local' for your "
        "own build, or 'dev-sha-abc1234' to reproduce a CI build",
    )
    build_parser.add_argument(
        "--build-arg",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="extra Docker build arg, e.g. E2XGRADER_VERSION=0.4.0 (repeatable)",
    )
    build_parser.add_argument(
        "--dry-run", action="store_true", help="only print the docker command"
    )
    build_parser.add_argument(
        "--plan",
        metavar="JSON",
        help="CI: the JSON printed by `plan`; tags and parents come from it",
    )
    build_parser.add_argument(
        "--push",
        action="store_true",
        help="CI: push to every registry instead of loading locally (needs --plan)",
    )

    retag_parser = commands.add_parser(
        "retag",
        help="give every image another tag in the registry (e.g. latest → summer-2026)",
        description="Tag every enabled image in every registry, without pulling or "
        "pushing layers. Checks first that every source exists and no target exists "
        "yet, so either all tags are written or none. Needs `docker login`.",
    )
    retag_parser.add_argument(
        "--from", dest="from_tag", required=True, metavar="TAG", help="existing tag"
    )
    retag_parser.add_argument(
        "--to",
        dest="to_tags",
        action="append",
        required=True,
        metavar="TAG",
        help="new tag, e.g. summer-2026 (repeatable); not a tag from a tag set",
    )
    retag_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow replacing a target tag that already exists",
    )
    retag_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only print the commands (no registry access)",
    )

    complete_parser = commands.add_parser(
        "complete-tags",
        help="CI: give the images a run didn't rebuild that run's tags",
        description="After a pushing CI run, tag every image that wasn't rebuilt "
        "(still at the tag set's parent_tag, e.g. dev) with the run's other tags "
        "(e.g. dev-2026-11-10, dev-sha-abc1234), so they cover the whole image set. "
        "Does nothing if the run built nothing.",
    )
    complete_parser.add_argument(
        "--plan", required=True, metavar="JSON", help="the JSON printed by `plan`"
    )
    complete_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only print the commands (no registry access)",
    )
    return parser


if __name__ == "__main__":
    sys.exit(main())
