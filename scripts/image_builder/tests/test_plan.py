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
        pytest.param(
            ["notebooks.toml"], EVERYTHING, id="manifest change, old version unknown"
        ),
        pytest.param(
            [".github/workflows/_build_image.yml"],
            EVERYTHING,
            id="build workflow change",
        ),
        pytest.param(["scripts/image_builder/plan.py"], EVERYTHING, id="script change"),
        pytest.param(
            ["notebooks/image_info/image_info.py"], EVERYTHING, id="image_info change"
        ),
        pytest.param(
            ["notebooks/image_info/tests/test_image_info.py"],
            [],
            id="image_info test change",
        ),
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


def manifest_data(images: dict | None = None, **sections) -> dict:
    """make_data(IMAGES), with entries of top-level sections added or replaced."""
    data = make_data(images or IMAGES)
    for key, entries in sections.items():
        data[key] = {**data[key], **entries}
    return data


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        pytest.param(manifest_data(), manifest_data(), [], id="no change"),
        pytest.param(
            manifest_data(),
            manifest_data({**IMAGES, "e": {"parent": "b"}}),
            ["e"],
            id="new image",
        ),
        pytest.param(
            manifest_data(),
            manifest_data({**IMAGES, "e": {"parent": "a", "e2x": True}}),
            ["e", "e-exam", "e-student"],
            id="new image with e2x variants",
        ),
        pytest.param(
            manifest_data({**IMAGES, "d": {"parent": "a", "enabled": False}}),
            manifest_data(),
            ["d"],
            id="image enabled",
        ),
        pytest.param(
            manifest_data(),
            manifest_data({**IMAGES, "c": {"parent": "d"}}),
            ["c"],
            id="parent changed",
        ),
        pytest.param(
            manifest_data(),
            manifest_data({**IMAGES, "a": {"base": "x:2", "e2x": True}}),
            EVERYTHING,
            id="base changed rebuilds the subtree",
        ),
        pytest.param(
            manifest_data(),
            manifest_data({**IMAGES, "b": {"parent": "a", "e2x": True}}),
            ["b-exam", "b-student"],
            id="e2x turned on builds only the variants",
        ),
        pytest.param(
            manifest_data(),
            manifest_data({k: v for k, v in IMAGES.items() if k != "d"}),
            [],
            id="image removed",
        ),
        pytest.param(
            manifest_data(),
            manifest_data(e2x={"modes": {"student": "student", "student_exam": "x"}}),
            ["a-x"],
            id="e2x mode renamed",
        ),
        pytest.param(
            manifest_data(),
            manifest_data(registry={"namespace": "org/other"}),
            EVERYTHING,
            id="registry changed",
        ),
        pytest.param(
            manifest_data(),
            manifest_data(tag_sets={"dev": {"tags": ["dev"], "parent_tag": "dev"}}),
            EVERYTHING,
            id="tag sets changed",
        ),
    ],
)
def test_select_manifest_change(old, new, expected):
    assert select(parse(new), ["notebooks.toml"], parse(old)) == expected


def test_select_manifest_and_folder_change():
    old = parse(manifest_data())
    new = parse(manifest_data({**IMAGES, "e": {"parent": "d"}}))
    changed = ["notebooks.toml", "notebooks/images/b/Dockerfile"]

    assert select(new, changed, old) == ["b", "c", "e"]


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
