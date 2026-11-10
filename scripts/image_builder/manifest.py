"""Load and validate notebooks.toml.

The manifest describes a tree of images. Loading turns it into a flat dict of
*nodes*: every enabled image is a node, and every image with `e2x = true` adds
one more node per e2xgrader mode (e.g. `ml-notebook-student`). After loading,
no other module needs to know about e2x.

`parse` is pure (dict in, Manifest out), so it is easy to test.
`load` adds the parts that touch the file system.
"""

import string
import tomllib
from dataclasses import dataclass
from pathlib import Path

IMAGES_DIR = Path("notebooks/images")
E2X_DIR = Path("notebooks/e2xgrader")
SHA_PLACEHOLDER = "{sha}"
PLACEHOLDERS = {"date", "sha"}  # allowed in tags, filled in by tags.py

TOP_LEVEL_KEYS = {"registry", "e2x", "tag_sets", "images"}
REGISTRY_KEYS = {"namespace", "hosts", "primary"}
TAG_SET_KEYS = {"tags", "parent_tag"}
IMAGE_KEYS = {"base", "parent", "e2x", "enabled"}


class ManifestError(Exception):
    """Raised when notebooks.toml is invalid."""


@dataclass(frozen=True)
class Registry:
    namespace: str
    hosts: tuple[str, ...]
    primary: str


@dataclass(frozen=True)
class TagSet:
    name: str
    tags: tuple[str, ...]
    parent_tag: str

    @property
    def run_tag(self) -> str | None:
        """The tag that identifies one run (the one containing {sha}), if any."""
        return next((tag for tag in self.tags if SHA_PLACEHOLDER in tag), None)

    @property
    def can_push(self) -> bool:
        """Only sets with a run tag may push: children need it to find their parent."""
        return self.run_tag is not None


@dataclass(frozen=True)
class Node:
    name: str
    folder: Path  # build context, relative to the repo root
    parent: str | None = None  # node in this manifest ...
    base: str | None = None  # ... or an external image (exactly one of the two)
    target: str | None = None  # Dockerfile target, only set for e2x variants

    @property
    def is_e2x(self) -> bool:
        return self.target is not None


@dataclass(frozen=True)
class Manifest:
    registry: Registry
    tag_sets: dict[str, TagSet]
    nodes: dict[str, Node]  # enabled nodes only, e2x variants included


def load(path: Path) -> Manifest:
    """Read notebooks.toml, validate it and check that the image folders match."""
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except tomllib.TOMLDecodeError as error:
        raise ManifestError(f"{path}: {error}") from error

    manifest = parse(data)
    _check_folders(data["images"], root=path.parent)
    return manifest


def parse(data: dict) -> Manifest:
    """Validate the raw TOML data and expand it into nodes."""
    _check_keys("top level", data, allowed=TOP_LEVEL_KEYS, required=TOP_LEVEL_KEYS)
    registry = _parse_registry(data["registry"])
    tag_sets = {name: _parse_tag_set(name, raw) for name, raw in data["tag_sets"].items()}
    modes = _parse_e2x_modes(data["e2x"])

    images = data["images"]
    for name, raw in images.items():
        _check_image(name, raw, images)

    nodes = _expand(images, modes)
    build_order(nodes)  # raises on cycles
    return Manifest(registry, tag_sets, nodes)


def children(nodes: dict[str, Node]) -> dict[str, list[str]]:
    """Map every node to its direct children, sorted by name."""
    result: dict[str, list[str]] = {name: [] for name in nodes}
    for name in sorted(nodes):
        parent = nodes[name].parent
        if parent is not None:
            result[parent].append(name)
    return result


def build_order(nodes: dict[str, Node]) -> list[str]:
    """Return all node names with every parent before its children.

    Walks the tree depth-first from the roots (nodes with an external base),
    so the order is deterministic and reads like the tree itself.
    """
    kids = children(nodes)
    order: list[str] = []

    def visit(name: str) -> None:
        order.append(name)
        for child in kids[name]:
            visit(child)

    for root in sorted(name for name, node in nodes.items() if node.parent is None):
        visit(root)

    # Every node has exactly one parent or a base, so a node that can't be
    # reached from a root must be part of (or below) a cycle.
    unreachable = sorted(nodes.keys() - set(order))
    if unreachable:
        raise ManifestError(f"parents form a cycle: {', '.join(unreachable)}")
    return order


def _expand(images: dict, modes: dict[str, str]) -> dict[str, Node]:
    """Turn enabled images into nodes, adding one node per e2x mode."""
    nodes: dict[str, Node] = {}
    for name, raw in images.items():
        if not raw.get("enabled", True):
            continue
        image = Node(name, IMAGES_DIR / name, parent=raw.get("parent"), base=raw.get("base"))
        _add(nodes, image)
        if raw.get("e2x", False):
            for target, suffix in modes.items():
                _add(nodes, Node(f"{name}-{suffix}", E2X_DIR, parent=name, target=target))
    return nodes


def _add(nodes: dict[str, Node], node: Node) -> None:
    if node.name in nodes:
        raise ManifestError(f"duplicate image name '{node.name}' (an image and an e2x variant share it)")
    nodes[node.name] = node


def _check_image(name: str, raw: dict, images: dict) -> None:
    where = f"[images.{name}]"
    _check_keys(where, raw, allowed=IMAGE_KEYS)

    for key in ("e2x", "enabled"):
        if not isinstance(raw.get(key, False), bool):
            raise ManifestError(f"{where}: '{key}' must be true or false")

    if ("base" in raw) == ("parent" in raw):
        raise ManifestError(f"{where}: needs exactly one of 'base' or 'parent'")

    parent = raw.get("parent")
    if parent is None:
        return
    if parent not in images:
        raise ManifestError(f"{where}: unknown parent '{parent}'")
    if raw.get("enabled", True) and not images[parent].get("enabled", True):
        raise ManifestError(f"{where}: parent '{parent}' is disabled")


def _parse_registry(raw: dict) -> Registry:
    _check_keys("[registry]", raw, allowed=REGISTRY_KEYS, required=REGISTRY_KEYS)
    if raw["primary"] not in raw["hosts"]:
        raise ManifestError("[registry]: 'primary' must be one of 'hosts'")
    return Registry(raw["namespace"], tuple(raw["hosts"]), raw["primary"])


def _parse_tag_set(name: str, raw: dict) -> TagSet:
    where = f"[tag_sets.{name}]"
    _check_keys(where, raw, allowed=TAG_SET_KEYS, required=TAG_SET_KEYS)
    for tag in raw["tags"]:
        _check_placeholders(where, tag)
    sha_tags = [tag for tag in raw["tags"] if SHA_PLACEHOLDER in tag]
    if len(sha_tags) > 1:
        raise ManifestError(f"{where}: at most one tag may contain {SHA_PLACEHOLDER}")
    return TagSet(name, tuple(raw["tags"]), raw["parent_tag"])


def _check_placeholders(where: str, tag: str) -> None:
    try:
        fields = {field for _, field, _, _ in string.Formatter().parse(tag) if field is not None}
    except ValueError as error:
        raise ManifestError(f"{where}: invalid tag '{tag}' ({error})") from error
    unknown = sorted(fields - PLACEHOLDERS)
    if unknown:
        raise ManifestError(f"{where}: unknown placeholder(s) in '{tag}': {', '.join(unknown)}")


def _parse_e2x_modes(raw: dict) -> dict[str, str]:
    _check_keys("[e2x]", raw, allowed={"modes"}, required={"modes"})
    return dict(raw["modes"])


def _check_keys(where: str, raw: dict, allowed: set[str], required: set[str] = frozenset()) -> None:
    unknown = sorted(raw.keys() - allowed)
    if unknown:
        raise ManifestError(f"{where}: unknown key(s) {', '.join(unknown)}")
    missing = sorted(required - raw.keys())
    if missing:
        raise ManifestError(f"{where}: missing key(s) {', '.join(missing)}")


def _check_folders(images: dict, root: Path) -> None:
    """Every [images.*] entry (disabled ones too) must have a folder, and vice versa."""
    images_dir = root / IMAGES_DIR
    if not images_dir.is_dir():
        raise ManifestError(f"missing folder {IMAGES_DIR}")
    if not (root / E2X_DIR).is_dir():
        raise ManifestError(f"missing folder {E2X_DIR}")

    on_disk = {path.name for path in images_dir.iterdir() if path.is_dir()}
    missing = sorted(images.keys() - on_disk)
    if missing:
        raise ManifestError(f"no folder in {IMAGES_DIR} for: {', '.join(missing)}")
    unlisted = sorted(on_disk - images.keys())
    if unlisted:
        raise ManifestError(f"folders in {IMAGES_DIR} missing from notebooks.toml: {', '.join(unlisted)}")
