from datetime import datetime, timezone

import pytest
from build import BuildError, command, oci_labels, parent_tag, parse_build_args
from helpers import make_data
from manifest import parse


@pytest.fixture
def small_manifest():
    return parse(make_data())  # base-nb (base jupyter/minimal:1, e2x) ── child-nb


def build_command(small_manifest, name, build_args=None):
    return command(
        small_manifest,
        small_manifest.nodes[name],
        tags=["local"],
        parent_tag="latest",
        labels={"revision": "abc"},
        build_args=build_args or {},
    )


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
