from datetime import datetime, timedelta, timezone

from manifest import TagSet
from tags import format_tag, resolve


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
