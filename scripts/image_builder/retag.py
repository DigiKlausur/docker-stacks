"""Give every enabled image another tag in the registry, e.g. latest → summer-2026.

`docker buildx imagetools create` writes a new tag for an existing manifest
directly in the registry: no pull, no push of layers, the digest stays the same.

Pure: functions check names and return commands. __main__ runs the preflight
(via registry.py) and then the commands.
"""

import re

import tags
from build import image_ref
from manifest import Manifest, build_order

# Docker's rule for a tag name.
VALID_TAG = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}")


class RetagError(Exception):
    """Raised for an invalid or forbidden tag."""


def check_tags(manifest: Manifest, from_tag: str, to_tags: list[str]) -> None:
    """Fail before touching the registry if a tag name is invalid or forbidden."""
    for tag in [from_tag, *to_tags]:
        if not VALID_TAG.fullmatch(tag):
            raise RetagError(f"'{tag}' is not a valid Docker tag")
    for tag in to_tags:
        owner = _managing_tag_set(manifest, tag)
        if owner is not None:
            raise RetagError(
                f"'{tag}' is managed by [tag_sets.{owner}] in notebooks.toml; "
                "retag only to fixed names like summer-2026"
            )


def pairs(
    manifest: Manifest,
    from_tag: str,
    to_tags: list[str],
    only: list[str] | None = None,
) -> list[tuple[str, list[str]]]:
    """(source, targets) for every enabled node (or `only` these) × registry."""
    names = build_order(manifest.nodes) if only is None else only
    result = []
    for name in names:
        for host in manifest.registry.hosts:
            source = image_ref(manifest, name, from_tag, host)
            targets = [image_ref(manifest, name, tag, host) for tag in to_tags]
            result.append((source, targets))
    return result


def completion_pairs(manifest: Manifest, summary: dict) -> list[tuple[str, list[str]]]:
    """After a pushing run: give every image that wasn't rebuilt the run's new tags.

    Images that weren't rebuilt still carry the tag set's parent_tag (e.g. `dev`).
    They get every other tag of the run (`dev-2026-11-10`, `dev-sha-abc1234`), so
    those tags cover the whole image set. A run that built nothing adds no tags.
    """
    if not summary["images"]:
        return []
    rebuilt = set(summary["images"])
    not_rebuilt = [name for name in build_order(manifest.nodes) if name not in rebuilt]
    new_tags = [tag for tag in summary["tags"] if tag != summary["parent_tag"]]
    if not new_tags:
        return []
    return pairs(manifest, summary["parent_tag"], new_tags, only=not_rebuilt)


def create_command(source: str, targets: list[str]) -> list[str]:
    cmd = ["docker", "buildx", "imagetools", "create"]
    for target in targets:
        cmd += ["--tag", target]
    return [*cmd, source]


def _managing_tag_set(manifest: Manifest, tag: str) -> str | None:
    """The tag set whose tags (e.g. `latest`, `dev-{date}`) include `tag`, if any."""
    for tag_set in manifest.tag_sets.values():
        if any(tags.tag_regex(pattern).fullmatch(tag) for pattern in tag_set.tags):
            return tag_set.name
    return None
