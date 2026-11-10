import pytest
from helpers import make_data
from manifest import parse
from retag import RetagError, check_tags, completion_pairs, create_command, pairs


@pytest.fixture
def small_manifest():
    # base-nb (e2x: student, exam) ── child-nb; tag sets: local, master (latest, sha-{sha})
    return parse(make_data())


def test_pairs_cover_every_node_in_every_registry(small_manifest):
    result = pairs(small_manifest, "latest", ["summer-2026", "exam-1"])

    assert len(result) == 4 * 2  # 4 nodes × ghcr.io, quay.io
    assert result[0] == (
        "ghcr.io/org/stack/base-nb:latest",
        ["ghcr.io/org/stack/base-nb:summer-2026", "ghcr.io/org/stack/base-nb:exam-1"],
    )
    assert result[1][0] == "quay.io/org/stack/base-nb:latest"


def test_create_command():
    assert create_command("r/a:latest", ["r/a:x", "r/a:y"]) == [
        "docker", "buildx", "imagetools", "create",
        "--tag", "r/a:x", "--tag", "r/a:y",
        "r/a:latest",
    ]  # fmt: skip


def test_fixed_names_are_allowed(small_manifest):
    check_tags(small_manifest, "latest", ["summer-2026", "exam_2026.07"])


@pytest.mark.parametrize(
    ("to_tag", "message"),
    [
        pytest.param("latest", "managed by", id="moving tag"),
        pytest.param("local", "managed by", id="local tag"),
        pytest.param("sha-abc1234", "managed by", id="per-commit tag"),
        pytest.param("summer 2026", "not a valid", id="space"),
        pytest.param("-summer", "not a valid", id="leading dash"),
        pytest.param("x" * 129, "not a valid", id="too long"),
    ],
)
def test_forbidden_or_invalid_targets_are_rejected(small_manifest, to_tag, message):
    with pytest.raises(RetagError, match=message):
        check_tags(small_manifest, "latest", [to_tag])


def test_invalid_source_is_rejected(small_manifest):
    with pytest.raises(RetagError, match="not a valid"):
        check_tags(small_manifest, "lat est", ["summer-2026"])


def test_pairs_can_be_limited_to_some_nodes(small_manifest):
    result = pairs(small_manifest, "x", ["y"], only=["child-nb"])
    sources = [source for source, _ in result]
    assert sources == ["ghcr.io/org/stack/child-nb:x", "quay.io/org/stack/child-nb:x"]


def summary(images: list[str]) -> dict:
    """A master run's plan (as parsed JSON) that rebuilt `images`."""
    return {
        "tags": ["latest", "sha-abc1234"],
        "parent_tag": "latest",
        "images": images,
    }


def test_images_not_rebuilt_get_the_runs_other_tags(small_manifest):
    result = completion_pairs(small_manifest, summary(["base-nb", "base-nb-exam"]))

    sources = [source for source, _ in result]
    assert sources == [
        "ghcr.io/org/stack/base-nb-student:latest",
        "quay.io/org/stack/base-nb-student:latest",
        "ghcr.io/org/stack/child-nb:latest",
        "quay.io/org/stack/child-nb:latest",
    ]
    assert result[0][1] == ["ghcr.io/org/stack/base-nb-student:sha-abc1234"]


def test_a_run_that_built_nothing_adds_no_tags(small_manifest):
    assert completion_pairs(small_manifest, summary([])) == []


def test_a_run_that_rebuilt_everything_adds_no_tags(small_manifest):
    everything = list(small_manifest.nodes)
    assert completion_pairs(small_manifest, summary(everything)) == []
