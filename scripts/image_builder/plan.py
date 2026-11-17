"""Decide which nodes to build, based on the files that changed.

Rules:
- README.md files and the script's tests never trigger a build.
- The reusable build workflow, the script's .py files and image_info.py (copied
  into every image) can affect every image, so changing them rebuilds everything.
- A node is rebuilt if a file in its folder changed, and so is everything below
  it in the tree.
- notebooks.toml is compared with its version where the branch split off: a node
  is rebuilt if it is new (or newly enabled) or its entry changed, again with
  everything below it. Removed nodes need no build. A change to [registry] or
  [tag_sets] rebuilds everything, and so does an unknown or unreadable old version.
"""

from datetime import datetime
from pathlib import PurePosixPath

import tags
from manifest import IMAGE_INFO_DIR, Manifest, Node, TagSet, build_order, children

MANIFEST_FILE = "notebooks.toml"
FULL_REBUILD_FILES = {
    ".github/workflows/_build_image.yml",
    f"{IMAGE_INFO_DIR.as_posix()}/image_info.py",
}
SCRIPT_DIR = "scripts/image_builder/"
TESTS_DIR = "scripts/image_builder/tests/"


def select(
    manifest: Manifest, changed_files: list[str], old_manifest: Manifest | None = None
) -> list[str]:
    """Nodes to build, in build order: changed nodes plus their descendants.

    `old_manifest` is notebooks.toml where the branch split off, None if unknown.
    """
    relevant = [path for path in changed_files if not _is_ignored(path)]
    if any(_needs_full_rebuild(path) for path in relevant):
        return build_order(manifest.nodes)

    changed = {
        name
        for name, node in manifest.nodes.items()
        if any(_is_in(path, node) for path in relevant)
    }
    if MANIFEST_FILE in relevant:
        if old_manifest is None or _affects_all_nodes(old_manifest, manifest):
            return build_order(manifest.nodes)
        changed |= changed_nodes(old_manifest, manifest)

    return in_build_order(
        manifest.nodes, changed | descendants(manifest.nodes, changed)
    )


def changed_nodes(old: Manifest, new: Manifest) -> set[str]:
    """Nodes of `new` that are missing in `old` or differ from it."""
    return {name for name, node in new.nodes.items() if old.nodes.get(name) != node}


def in_build_order(nodes: dict[str, Node], names: set[str]) -> list[str]:
    """The given names, sorted so that every parent comes before its children."""
    return [name for name in build_order(nodes) if name in names]


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


def _affects_all_nodes(old: Manifest, new: Manifest) -> bool:
    # Registry and tag sets decide where and under which tags every image is pushed.
    return old.registry != new.registry or old.tag_sets != new.tag_sets


def _needs_full_rebuild(path: str) -> bool:
    return path in FULL_REBUILD_FILES or (
        path.startswith(SCRIPT_DIR) and path.endswith(".py")
    )


def _is_in(path: str, node: Node) -> bool:
    # The trailing slash keeps "notebooks/images/b" from matching "notebooks/images/bb/...".
    return path.startswith(f"{node.folder.as_posix()}/")


if __name__ == "__main__":
    raise SystemExit("not a script: run `python scripts/image_builder -h` instead")
