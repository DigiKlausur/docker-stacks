from datetime import datetime, timezone

import pytest
from helpers import make_data
from manifest import parse
from plan import descendants, in_build_order, select, summary

# a (base, e2x) ─┬─ b ── c
#                └─ d
IMAGES = {
    "a": {"base": "x:1", "e2x": True},
    "b": {"parent": "a"},
    "c": {"parent": "b"},
    "d": {"parent": "a"},
}
EVERYTHING = ["a", "a-exam", "a-student", "b", "c", "d"]


@pytest.fixture
def small_manifest():
    return parse(make_data(IMAGES))


@pytest.mark.parametrize(
    ("changed", "expected"),
    [
        pytest.param(
            ["notebooks/images/b/Dockerfile"],
            ["b", "c"],
            id="image and its descendants",
        ),
        pytest.param(
            ["notebooks/images/a/Dockerfile"],
            EVERYTHING,
            id="root rebuilds its subtree",
        ),
        pytest.param(
            ["notebooks/e2xgrader/Dockerfile"],
            ["a-exam", "a-student"],
            id="e2xgrader change",
        ),
        pytest.param(["notebooks/images/b/README.md"], [], id="README is ignored"),
        pytest.param(["notebooks.toml"], EVERYTHING, id="manifest change"),
        pytest.param(
            [".github/workflows/_build_image.yml"],
            EVERYTHING,
            id="build workflow change",
        ),
        pytest.param(["scripts/image_builder/plan.py"], EVERYTHING, id="script change"),
        pytest.param(
            ["scripts/image_builder/tests/test_plan.py"], [], id="test change"
        ),
        pytest.param(
            ["scripts/image_builder/.gitignore"],
            [],
            id="non-python file in script folder",
        ),
        pytest.param(["README.md", "hub/Dockerfile"], [], id="unrelated files"),
        pytest.param(
            ["notebooks/images/bb/Dockerfile"], [], id="folder prefix is no match"
        ),
    ],
)
def test_select(small_manifest, changed, expected):
    assert select(small_manifest, changed) == expected


def test_descendants(small_manifest):
    assert descendants(small_manifest.nodes, {"b"}) == {"c"}
    assert descendants(small_manifest.nodes, {"c"}) == set()


def test_in_build_order(small_manifest):
    assert in_build_order(small_manifest.nodes, {"c", "a", "b"}) == ["a", "b", "c"]


def test_summary_resolves_tags():
    tag_set = parse(make_data()).tag_sets["main"]
    now = datetime(2026, 11, 10, tzinfo=timezone.utc)

    assert summary(tag_set, ["base-nb"], "abc1234", now) == {
        "tag_set": "main",
        "tags": ["latest", "sha-abc1234"],
        "run_tag": "sha-abc1234",
        "parent_tag": "latest",
        "images": ["base-nb"],
    }
