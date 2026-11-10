"""Decide which nodes to build, based on the files that changed.

Rules:
- README.md files and the script's tests never trigger a build.
- notebooks.toml, the reusable build workflow and the script's .py files can
  affect every image, so changing them rebuilds everything.
- Otherwise a node is rebuilt if a file in its folder changed, and so is
  everything below it in the tree.
"""

from datetime import datetime
from pathlib import PurePosixPath

import tags
from manifest import Manifest, Node, TagSet, build_order, children

FULL_REBUILD_FILES = {"notebooks.toml", ".github/workflows/_build_image.yml"}
SCRIPT_DIR = "scripts/image_builder/"
TESTS_DIR = "scripts/image_builder/tests/"


def select(manifest: Manifest, changed_files: list[str]) -> list[str]:
    """Nodes to build, in build order: changed nodes plus their descendants."""
    relevant = [path for path in changed_files if not _is_ignored(path)]
    order = build_order(manifest.nodes)
    if any(_needs_full_rebuild(path) for path in relevant):
        return order

    changed = {name for name, node in manifest.nodes.items() if any(_is_in(path, node) for path in relevant)}
    selected = changed | descendants(manifest.nodes, changed)
    return [name for name in order if name in selected]


def descendants(nodes: dict[str, Node], names: set[str]) -> set[str]:
    """All nodes below the given ones (not including them)."""
    kids = children(nodes)
    found: set[str] = set()
    pending = list(names)
    while pending:
        for child in kids[pending.pop()]:
            found.add(child)
            pending.append(child)
    return found


def summary(tag_set: TagSet, images: list[str], sha: str, now: datetime) -> dict:
    """The plan as printed by `image_builder plan`."""
    run_tag = tags.format_tag(tag_set.run_tag, sha, now) if tag_set.run_tag else None
    return {
        "tag_set": tag_set.name,
        "tags": tags.resolve(tag_set, sha, now),
        "run_tag": run_tag,
        "parent_tag": tag_set.parent_tag,
        "images": images,
    }


def _is_ignored(path: str) -> bool:
    return PurePosixPath(path).name == "README.md" or path.startswith(TESTS_DIR)


def _needs_full_rebuild(path: str) -> bool:
    return path in FULL_REBUILD_FILES or (path.startswith(SCRIPT_DIR) and path.endswith(".py"))


def _is_in(path: str, node: Node) -> bool:
    # The trailing slash keeps "notebooks/images/b" from matching "notebooks/images/bb/...".
    return path.startswith(f"{node.folder.as_posix()}/")
