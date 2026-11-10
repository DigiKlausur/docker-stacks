"""Assemble the `docker buildx build` command for one node.

Pure: everything here returns data. __main__ runs the command (or prints it
with --dry-run).
"""

from datetime import datetime

from manifest import Manifest, Node

# Set by this script from notebooks.toml; overriding it would silently change the tree.
RESERVED_BUILD_ARGS = {"IMAGE_SOURCE"}


class BuildError(Exception):
    """Raised for invalid build input, e.g. an unknown image or a bad --build-arg."""


def command(
    manifest: Manifest,
    node: Node,
    tags: list[str],
    parent_tag: str,
    labels: dict[str, str],
    build_args: dict[str, str],
) -> list[str]:
    reserved = sorted(RESERVED_BUILD_ARGS & build_args.keys())
    if reserved:
        raise BuildError(
            f"{', '.join(reserved)} is set from notebooks.toml and can't be overridden"
        )

    cmd = ["docker", "buildx", "build", node.folder.as_posix()]
    if node.target is not None:
        cmd += ["--target", node.target]
    for key, value in {
        "IMAGE_SOURCE": base_image(manifest, node, parent_tag),
        **build_args,
    }.items():
        cmd += ["--build-arg", f"{key}={value}"]
    for tag in tags:
        cmd += ["--tag", image_ref(manifest, node.name, tag)]
    for key, value in labels.items():
        cmd += ["--label", f"{key}={value}"]
    # --load puts the result into `docker images` with every buildx driver
    # (the docker-container driver would otherwise keep it in its own cache).
    cmd.append("--load")
    return cmd


def image_ref(manifest: Manifest, name: str, tag: str) -> str:
    """Full reference in the primary registry, e.g. ghcr.io/org/stack/ml-notebook:latest."""
    return f"{manifest.registry.primary}/{manifest.registry.namespace}/{name}:{tag}"


def parent_tag(
    node: Node, built_in_this_run: set[str], same_run_tag: str, fallback_tag: str
) -> str:
    """Which tag of the parent to build on.

    A parent built in the same run is used by that run's tag (local: `local`,
    CI: the run tag). Any other parent is taken from the registry by
    `fallback_tag` (the tag set's parent_tag).
    """
    return same_run_tag if node.parent in built_in_this_run else fallback_tag


def base_image(manifest: Manifest, node: Node, parent_tag: str) -> str:
    """What the node builds FROM: its external base, or its parent from the registry."""
    if node.base is not None:
        return node.base
    return image_ref(manifest, node.parent, parent_tag)


def oci_labels(revision: str, now: datetime) -> dict[str, str]:
    return {
        "org.opencontainers.image.revision": revision,
        "org.opencontainers.image.created": now.isoformat(timespec="seconds"),
    }


def parse_build_args(pairs: list[str]) -> dict[str, str]:
    """Turn ["KEY=VALUE", ...] from the command line into a dict."""
    result: dict[str, str] = {}
    for pair in pairs:
        key, separator, value = pair.partition("=")
        if not separator or not key:
            raise BuildError(f"--build-arg must look like KEY=VALUE, got '{pair}'")
        result[key] = value
    return result
