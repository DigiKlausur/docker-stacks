"""Assemble the `docker buildx build` commands for one call of `build`.

Pure: everything here returns data. __main__ runs the commands (or prints them
with --dry-run).

A `Run` holds what's the same for every node built in one call. It comes either
from the local tag set (`local_run`) or from the plan JSON CI passes in (`ci_run`).
"""

import json
from dataclasses import dataclass
from datetime import datetime

import tags
from manifest import IMAGE_INFO_DIR, Manifest, Node, TagSet
from plan import in_build_order

# Set by this script; overriding them would silently change the tree
# (IMAGE_SOURCE) or what `image_info` records inside the image.
RESERVED_BUILD_ARGS = {"IMAGE_SOURCE", "IMAGE_NAME", "GIT_COMMIT", "BUILD_DATE"}
PLAN_KEYS = {"tags", "run_tag", "parent_tag", "images"}


class BuildError(Exception):
    """Raised for invalid build input, e.g. an unknown image or a bad --build-arg."""


@dataclass(frozen=True)
class Run:
    """What's the same for every node built in one call."""

    names: list[str]  # nodes to build now, in build order
    tags: list[str]  # concrete tags every node gets
    in_run: set[str]  # nodes built in this run (CI: the whole plan)
    same_run_tag: str  # tag of a parent that is built in this run
    parent_tag: str  # tag of any other parent, pulled from the registry
    push: bool = False


def local_run(
    manifest: Manifest,
    selected: set[str],
    tag_set: TagSet,
    sha: str,
    now: datetime,
    parent_tag: str | None = None,
) -> Run:
    """A local build. `parent_tag` replaces the tag set's parent_tag for parents
    that aren't built in this call (e.g. `local`, or `dev-sha-abc1234` to
    reproduce a CI build)."""
    if parent_tag is not None and not tags.VALID_TAG.fullmatch(parent_tag):
        raise BuildError(f"--parent-tag '{parent_tag}' is not a valid Docker tag")
    resolved = tags.resolve(tag_set, sha, now)
    return Run(
        names=in_build_order(manifest.nodes, selected),
        tags=resolved,
        in_run=selected,
        same_run_tag=resolved[0],  # children build on their parent's fresh :local
        parent_tag=parent_tag or tag_set.parent_tag,
    )


def ci_run(manifest: Manifest, image: str, plan_json: str, push: bool) -> Run:
    """One node, with tags and parents taken from the plan job's JSON."""
    summary = parse_plan(plan_json)
    if image not in manifest.nodes:
        raise BuildError(f"unknown image '{image}'")
    if image not in summary["images"]:
        raise BuildError(f"'{image}' is not in the plan")
    return Run(
        names=[image],
        tags=summary["tags"],
        # Each node is built on its own runner. Without --push nothing of this
        # run reaches the registry, so every parent must come by parent_tag.
        in_run=set(summary["images"]) if push else set(),
        same_run_tag=summary["run_tag"],
        parent_tag=summary["parent_tag"],
        push=push,
    )


def command(
    manifest: Manifest,
    node: Node,
    run: Run,
    revision: str,
    now: datetime,
    build_args: dict[str, str],
) -> list[str]:
    reserved = sorted(RESERVED_BUILD_ARGS & build_args.keys())
    if reserved:
        raise BuildError(
            f"{', '.join(reserved)} is set by image_builder and can't be overridden"
        )

    cmd = ["docker", "buildx", "build", node.folder.as_posix()]
    if node.target is not None:
        cmd += ["--target", node.target]
    # image_info lives outside the build context (the image's folder). A named
    # context makes it available in the Dockerfile as `COPY --from=image_info`.
    cmd += ["--build-context", f"image_info={IMAGE_INFO_DIR.as_posix()}"]

    tag = parent_tag(node, run.in_run, run.same_run_tag, run.parent_tag)
    for key, value in {
        "IMAGE_SOURCE": base_image(manifest, node, tag),
        **image_info_args(node, revision, now),
        **build_args,
    }.items():
        cmd += ["--build-arg", f"{key}={value}"]

    # A push goes to every registry in one build, so all get the same digest.
    # A local build only needs the primary one.
    hosts = manifest.registry.hosts if run.push else (manifest.registry.primary,)
    for host in hosts:
        for run_tag in run.tags:
            cmd += ["--tag", image_ref(manifest, node.name, run_tag, host)]

    for key, value in oci_labels(revision, now).items():
        cmd += ["--label", f"{key}={value}"]

    # --load puts the result into `docker images` with every buildx driver
    # (the docker-container driver would otherwise keep it in its own cache).
    cmd.append("--push" if run.push else "--load")
    return cmd


def image_ref(manifest: Manifest, name: str, tag: str, host: str | None = None) -> str:
    """Full reference, e.g. ghcr.io/org/stack/ml-notebook:latest (default: primary)."""
    host = host or manifest.registry.primary
    return f"{host}/{manifest.registry.namespace}/{name}:{tag}"


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
        "org.opencontainers.image.created": timestamp(now),
    }


def image_info_args(node: Node, revision: str, now: datetime) -> dict[str, str]:
    """Build args for the `image_info record` step at the end of every Dockerfile.
    Same commit and time as the OCI labels."""
    return {
        "IMAGE_NAME": node.name,
        "GIT_COMMIT": revision,
        "BUILD_DATE": timestamp(now),
    }


def timestamp(now: datetime) -> str:
    return now.isoformat(timespec="seconds")


def parse_build_args(pairs: list[str]) -> dict[str, str]:
    """Turn ["KEY=VALUE", ...] from the command line into a dict."""
    result: dict[str, str] = {}
    for pair in pairs:
        key, separator, value = pair.partition("=")
        if not separator or not key:
            raise BuildError(f"--build-arg must look like KEY=VALUE, got '{pair}'")
        result[key] = value
    return result


def parse_plan(plan_json: str) -> dict:
    """Read the JSON printed by `plan`; only plans of tag sets that can push."""
    try:
        summary = json.loads(plan_json)
    except json.JSONDecodeError as error:
        raise BuildError(f"--plan is not valid JSON: {error}") from error
    if not isinstance(summary, dict):
        raise BuildError("--plan must be the JSON object printed by `plan`")
    missing = sorted(PLAN_KEYS - summary.keys())
    if missing:
        raise BuildError(f"--plan is missing: {', '.join(missing)}")
    if summary["run_tag"] is None:
        raise BuildError(
            f"tag set '{summary.get('tag_set')}' has no {{sha}} tag, "
            "so its plan can't be used for CI builds"
        )
    return summary


if __name__ == "__main__":
    raise SystemExit("not a script: run `python scripts/image_builder -h` instead")
