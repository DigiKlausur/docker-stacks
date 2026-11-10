from pathlib import Path

import pytest
from helpers import make_data
from manifest import E2X_DIR, IMAGES_DIR, ManifestError, build_order, load, parse

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_e2x_variants_become_nodes():
    nodes = parse(make_data()).nodes

    assert set(nodes) == {"base-nb", "base-nb-student", "base-nb-exam", "child-nb"}
    exam = nodes["base-nb-exam"]
    assert (exam.parent, exam.target, exam.folder) == (
        "base-nb",
        "student_exam",
        E2X_DIR,
    )
    assert nodes["child-nb"].folder == IMAGES_DIR / "child-nb"
    assert not nodes["child-nb"].is_e2x


def test_disabled_image_is_skipped():
    images = {
        "base-nb": {"base": "x:1"},
        "old-nb": {"parent": "base-nb", "e2x": True, "enabled": False},
    }
    assert set(parse(make_data(images)).nodes) == {"base-nb"}


def test_build_order_puts_parents_first():
    images = {"c": {"parent": "b"}, "b": {"parent": "a"}, "a": {"base": "x:1"}}
    assert build_order(parse(make_data(images)).nodes) == ["a", "b", "c"]


def test_only_tag_sets_with_sha_can_push():
    tag_sets = parse(make_data()).tag_sets

    assert not tag_sets["local"].can_push
    assert tag_sets["master"].can_push
    assert tag_sets["master"].run_tag == "sha-{sha}"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        pytest.param(
            lambda d: d["images"]["child-nb"].update(parnet="x"),
            "unknown key",
            id="typo in key",
        ),
        pytest.param(
            lambda d: d["images"]["child-nb"].update(base="x:1"),
            "exactly one",
            id="base and parent",
        ),
        pytest.param(
            lambda d: d["images"]["child-nb"].pop("parent"),
            "exactly one",
            id="neither base nor parent",
        ),
        pytest.param(
            lambda d: d["images"]["child-nb"].update(parent="nope"),
            "unknown parent",
            id="unknown parent",
        ),
        pytest.param(
            lambda d: d["images"]["base-nb"].update(enabled=False),
            "disabled",
            id="disabled parent",
        ),
        pytest.param(
            lambda d: d["images"]["base-nb"].update(e2x="true"),
            "true or false",
            id="e2x not a bool",
        ),
        pytest.param(
            lambda d: d["tag_sets"]["master"]["tags"].append("x-{sha}"),
            "at most one",
            id="two sha tags",
        ),
        pytest.param(
            lambda d: d["tag_sets"]["master"]["tags"].append("v-{dat}"),
            "unknown placeholder",
            id="placeholder typo",
        ),
        pytest.param(
            lambda d: d["tag_sets"]["master"]["tags"].append("v-{"),
            "invalid tag",
            id="broken braces",
        ),
        pytest.param(
            lambda d: d["registry"].update(primary="docker.io"),
            "primary",
            id="primary not in hosts",
        ),
        pytest.param(
            lambda d: d["images"].update({"base-nb-exam": {"parent": "base-nb"}}),
            "duplicate",
            id="name collision",
        ),
        pytest.param(
            lambda d: d["images"].update({"a": {"parent": "b"}, "b": {"parent": "a"}}),
            "cycle",
            id="cycle",
        ),
        pytest.param(lambda d: d.pop("tag_sets"), "missing key", id="missing section"),
    ],
)
def test_invalid_manifest_is_rejected(mutate, message):
    data = make_data()
    mutate(data)
    with pytest.raises(ManifestError, match=message):
        parse(data)


def test_repository_manifest_is_valid():
    """The real notebooks.toml must always load, including the folder checks."""
    nodes = load(REPO_ROOT / "notebooks.toml").nodes
    assert "minimal-notebook" in nodes
    assert "julia-notebook" not in nodes  # disabled


SMALL_TOML = """
[registry]
namespace = "org/stack"
hosts     = ["ghcr.io"]
primary   = "ghcr.io"

[e2x]
modes = { student = "student" }

[tag_sets.local]
tags       = ["local"]
parent_tag = "latest"

[images.base-nb]
base = "x:1"
"""


def make_repo(root: Path, folders: list[str]) -> Path:
    """Create a fake repo with SMALL_TOML and the given image folders."""
    (root / E2X_DIR).mkdir(parents=True)
    (root / IMAGES_DIR).mkdir(parents=True)
    for name in folders:
        (root / IMAGES_DIR / name).mkdir()
    path = root / "notebooks.toml"
    path.write_text(SMALL_TOML)
    return path


def test_load_accepts_matching_folders(tmp_path):
    assert set(load(make_repo(tmp_path, ["base-nb"])).nodes) == {"base-nb"}


def test_load_rejects_folder_without_entry(tmp_path):
    with pytest.raises(ManifestError, match="missing from notebooks.toml"):
        load(make_repo(tmp_path, ["base-nb", "stray-nb"]))


def test_load_rejects_entry_without_folder(tmp_path):
    with pytest.raises(ManifestError, match="no folder"):
        load(make_repo(tmp_path, []))
