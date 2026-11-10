import json
from datetime import datetime, timezone

import pytest
from build import (
    BuildError,
    Run,
    ci_run,
    command,
    local_run,
    oci_labels,
    parent_tag,
    parse_build_args,
)
from helpers import make_data
from manifest import parse

# A local build of a single node: nothing else is built in the same run.
LOCAL_RUN = Run(
    names=[], tags=["local"], in_run=set(), same_run_tag="local", parent_tag="latest"
)


@pytest.fixture
def small_manifest():
    return parse(make_data())  # base-nb (base jupyter/minimal:1, e2x) ── child-nb


def build_command(small_manifest, name, build_args=None, run=LOCAL_RUN):
    node = small_manifest.nodes[name]
    return command(small_manifest, node, run, {"revision": "abc"}, build_args or {})


def test_root_image_builds_on_its_base(small_manifest):
    assert build_command(small_manifest, "base-nb") == [
        "docker", "buildx", "build", "notebooks/images/base-nb",
        "--build-arg", "IMAGE_SOURCE=jupyter/minimal:1",
        "--tag", "ghcr.io/org/stack/base-nb:local",
        "--label", "revision=abc",
        "--load",
    ]  # fmt: skip


def test_e2x_variant_builds_on_its_parent_from_the_registry(small_manifest):
    assert build_command(small_manifest, "base-nb-exam") == [
        "docker", "buildx", "build", "notebooks/e2xgrader",
        "--target", "student_exam",
        "--build-arg", "IMAGE_SOURCE=ghcr.io/org/stack/base-nb:latest",
        "--tag", "ghcr.io/org/stack/base-nb-exam:local",
        "--label", "revision=abc",
        "--load",
    ]  # fmt: skip


def test_extra_build_args_are_passed_through(small_manifest):
    cmd = build_command(small_manifest, "child-nb", {"E2XGRADER_VERSION": "0.4.0"})
    assert "E2XGRADER_VERSION=0.4.0" in cmd


def test_image_source_cannot_be_overridden(small_manifest):
    with pytest.raises(BuildError, match="IMAGE_SOURCE"):
        build_command(small_manifest, "child-nb", {"IMAGE_SOURCE": "evil:1"})


def test_parent_built_in_same_run_is_used_by_run_tag(small_manifest):
    child = small_manifest.nodes["child-nb"]
    assert parent_tag(child, {"base-nb", "child-nb"}, "local", "latest") == "local"


def test_other_parents_come_from_the_registry(small_manifest):
    child = small_manifest.nodes["child-nb"]
    assert parent_tag(child, {"child-nb"}, "local", "latest") == "latest"


def test_parse_build_args():
    assert parse_build_args(["A=1", "B=x=y", "C="]) == {"A": "1", "B": "x=y", "C": ""}


@pytest.mark.parametrize("pair", ["NOVALUE", "=1"])
def test_parse_build_args_rejects_malformed(pair):
    with pytest.raises(BuildError, match="KEY=VALUE"):
        parse_build_args([pair])


def test_oci_labels():
    now = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)
    assert oci_labels("abc", now) == {
        "org.opencontainers.image.revision": "abc",
        "org.opencontainers.image.created": "2026-11-10T12:00:00+00:00",
    }


def make_plan(**overrides) -> str:
    """Plan JSON as printed by `plan`, for a dev run that builds base-nb and its exam."""
    summary = {
        "tag_set": "dev",
        "tags": ["dev", "dev-sha-abc1234"],
        "run_tag": "dev-sha-abc1234",
        "parent_tag": "dev",
        "images": ["base-nb", "base-nb-exam"],
    }
    return json.dumps(summary | overrides)


def test_push_goes_to_every_registry_and_uses_the_run_tag(small_manifest):
    run = ci_run(small_manifest, "base-nb-exam", make_plan(), push=True)
    assert build_command(small_manifest, "base-nb-exam", run=run) == [
        "docker", "buildx", "build", "notebooks/e2xgrader",
        "--target", "student_exam",
        "--build-arg", "IMAGE_SOURCE=ghcr.io/org/stack/base-nb:dev-sha-abc1234",
        "--tag", "ghcr.io/org/stack/base-nb-exam:dev",
        "--tag", "ghcr.io/org/stack/base-nb-exam:dev-sha-abc1234",
        "--tag", "quay.io/org/stack/base-nb-exam:dev",
        "--tag", "quay.io/org/stack/base-nb-exam:dev-sha-abc1234",
        "--label", "revision=abc",
        "--push",
    ]  # fmt: skip


def test_parent_outside_the_plan_comes_by_parent_tag(small_manifest):
    plan_json = make_plan(images=["child-nb"])
    run = ci_run(small_manifest, "child-nb", plan_json, push=False)
    cmd = build_command(small_manifest, "child-nb", run=run)
    assert "IMAGE_SOURCE=ghcr.io/org/stack/base-nb:dev" in cmd


@pytest.mark.parametrize(
    ("image", "plan_json", "message"),
    [
        pytest.param("child-nb", make_plan(), "not in the plan", id="not planned"),
        pytest.param("nope", make_plan(), "unknown image", id="unknown image"),
        pytest.param("base-nb", make_plan(run_tag=None), "no {sha}", id="no run tag"),
        pytest.param("base-nb", "not json", "not valid JSON", id="invalid JSON"),
        pytest.param("base-nb", "[]", "JSON object", id="not an object"),
        pytest.param("base-nb", '{"tags": []}', "missing", id="missing keys"),
    ],
)
def test_ci_run_rejects_bad_input(small_manifest, image, plan_json, message):
    with pytest.raises(BuildError, match=message):
        ci_run(small_manifest, image, plan_json, push=True)


def test_local_run_builds_in_order_on_local_parents(small_manifest):
    tag_set = small_manifest.tag_sets["local"]
    now = datetime(2026, 11, 10, tzinfo=timezone.utc)
    run = local_run(small_manifest, {"child-nb", "base-nb"}, tag_set, "abc1234", now)

    assert run.names == ["base-nb", "child-nb"]
    assert (run.tags, run.same_run_tag, run.parent_tag) == (["local"], "local", "latest")
    assert not run.push
