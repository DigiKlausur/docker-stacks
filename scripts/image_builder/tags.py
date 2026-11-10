"""Turn a tag set into the concrete tags of one run.

Placeholders: {date} = build date in UTC (YYYY-MM-DD), {sha} = short commit SHA.
`now` is passed in (not read from the clock here), so the result is testable
and every image of one run gets the same date.
"""

import re
from datetime import datetime, timezone

from manifest import TagSet

# Docker's rule for a tag name.
VALID_TAG = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}")

# What each placeholder turns into, as a regex (must match format_tag below).
PLACEHOLDER_REGEX = {"date": r"\d{4}-\d{2}-\d{2}", "sha": r"[0-9a-f]{7,40}"}


def format_tag(tag: str, sha: str, now: datetime) -> str:
    return tag.format(date=now.astimezone(timezone.utc).strftime("%Y-%m-%d"), sha=sha)


def resolve(tag_set: TagSet, sha: str, now: datetime) -> list[str]:
    return [format_tag(tag, sha, now) for tag in tag_set.tags]


def tag_regex(tag: str) -> re.Pattern:
    """A regex matching every tag `tag` can produce, e.g. dev-{date} → dev-2026-11-10."""
    regex = re.escape(tag)
    for name, part in PLACEHOLDER_REGEX.items():
        regex = regex.replace(re.escape(f"{{{name}}}"), part)
    return re.compile(regex)


if __name__ == "__main__":
    raise SystemExit("not a script: run `python scripts/image_builder -h` instead")
