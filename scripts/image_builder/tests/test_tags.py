from datetime import datetime, timedelta, timezone

import pytest
from manifest import TagSet
from tags import format_tag, resolve, tag_regex


def test_resolve_fills_in_placeholders():
    tag_set = TagSet("dev", ("dev", "dev-{date}", "dev-sha-{sha}"), "dev")
    now = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)

    assert resolve(tag_set, "abc1234", now) == [
        "dev",
        "dev-2026-11-10",
        "dev-sha-abc1234",
    ]


def test_date_is_utc():
    late_evening_west_of_utc = datetime(
        2026, 11, 10, 23, 30, tzinfo=timezone(timedelta(hours=-2))
    )
    assert format_tag("{date}", "abc1234", late_evening_west_of_utc) == "2026-11-11"


@pytest.mark.parametrize(
    ("pattern", "tag", "matches"),
    [
        ("latest", "latest", True),
        ("latest", "latest-2", False),
        ("dev-{date}", "dev-2026-11-10", True),
        ("dev-{date}", "dev-summer", False),
        ("sha-{sha}", "sha-abc1234", True),
        ("sha-{sha}", "sha-summer", False),
        ("{date}", "2026-11-10", True),
    ],
)
def test_tag_regex_matches_what_a_pattern_produces(pattern, tag, matches):
    assert bool(tag_regex(pattern).fullmatch(tag)) is matches
