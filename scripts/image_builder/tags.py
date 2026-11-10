"""Turn a tag set into the concrete tags of one run.

Placeholders: {date} = build date in UTC (YYYY-MM-DD), {sha} = short commit SHA.
`now` is passed in (not read from the clock here), so the result is testable
and every image of one run gets the same date.
"""

from datetime import datetime, timezone

from manifest import TagSet


def format_tag(tag: str, sha: str, now: datetime) -> str:
    return tag.format(date=now.astimezone(timezone.utc).strftime("%Y-%m-%d"), sha=sha)


def resolve(tag_set: TagSet, sha: str, now: datetime) -> list[str]:
    return [format_tag(tag, sha, now) for tag in tag_set.tags]
