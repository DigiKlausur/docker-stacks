import json
import subprocess
import sys

import image_info
import pytest


@pytest.fixture
def info_file(tmp_path, monkeypatch):
    path = tmp_path / "image-info.json"
    monkeypatch.setattr(image_info, "INFO_FILE", str(path))
    return path


@pytest.fixture
def fake_packages(monkeypatch):
    packages = {"conda": {"numpy": "1.26.4"}, "pip": {"requests": "2.32.0"}}
    monkeypatch.setattr(image_info, "collect_packages", lambda: packages)
    return packages


def run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["image_info", *argv])
    image_info.main()


def make_dist(site, name, version, installer=None):
    dist_info = site / f"{name}-{version}.dist-info"
    dist_info.mkdir(parents=True)
    (dist_info / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n"
    )
    if installer is not None:
        (dist_info / "INSTALLER").write_text(f"{installer}\n")


# --------------------------------------------------------------------------- #
#   Package collection                                                         #
# --------------------------------------------------------------------------- #


def test_python_packages_grouped_by_installer_without_conda(tmp_path, monkeypatch):
    make_dist(tmp_path, "Foo_Bar", "1.0", installer="pip")
    make_dist(tmp_path, "fast", "2.0", installer="uv")
    make_dist(tmp_path, "numpy", "1.26.4", installer="conda")
    make_dist(tmp_path, "legacy", "0.1")  # no INSTALLER file
    monkeypatch.setattr(sys, "path", [str(tmp_path)])

    assert image_info.python_packages() == {
        "pip": {"foo-bar": "1.0"},
        "uv": {"fast": "2.0"},
        "unknown": {"legacy": "0.1"},
    }


def test_conda_packages_read_from_conda_meta(tmp_path):
    meta = tmp_path / "conda-meta"
    meta.mkdir()
    (meta / "numpy-1.26.4-py311_0.json").write_text(
        json.dumps({"name": "numpy", "version": "1.26.4"})
    )
    (meta / "history").write_text("not json")

    assert image_info.conda_packages(tmp_path) == {"numpy": "1.26.4"}


def test_conda_packages_empty_without_conda(tmp_path):
    assert image_info.conda_packages(tmp_path) == {}


def test_apt_packages_only_installed(monkeypatch):
    output = "ii \tvim\t2:8.2\nrc \told-lib\t1.0\nii \tlibc6\t2.35\n"
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(a, 0, stdout=output),
    )
    assert image_info.apt_packages() == {"vim": "2:8.2", "libc6": "2.35"}


def test_apt_packages_empty_without_dpkg(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError("dpkg-query")

    monkeypatch.setattr(subprocess, "run", missing)
    assert image_info.apt_packages() == {}


def test_collect_packages_leaves_out_empty_sources(monkeypatch):
    monkeypatch.setattr(image_info, "conda_packages", dict)
    monkeypatch.setattr(image_info, "apt_packages", lambda: {"vim": "2:8.2"})
    monkeypatch.setattr(image_info, "python_packages", lambda: {"pip": {"x": "1"}})

    assert image_info.collect_packages() == {"apt": {"vim": "2:8.2"}, "pip": {"x": "1"}}


# --------------------------------------------------------------------------- #
#   Commands                                                                   #
# --------------------------------------------------------------------------- #


def test_baseline_then_record_builds_the_chain(info_file, fake_packages, monkeypatch):
    run(monkeypatch, "baseline", "--name", "jupyter/minimal-notebook:6.5.4")
    run(
        monkeypatch,
        "record",
        "--name",
        "minimal-notebook",
        "--parent",
        "jupyter/minimal-notebook:6.5.4",
        "--git-commit",
        "abc1234",
        "--build-date",
        "2026-11-11T10:00:00+00:00",
    )

    base, own = json.loads(info_file.read_text())["chain"]
    assert base["name"] == "jupyter/minimal-notebook:6.5.4"
    assert base["external"] is True
    assert base["packages"] == fake_packages
    assert own["name"] == "minimal-notebook"
    assert own["git_commit"] == "abc1234"
    assert own["built_at"] == "2026-11-11T10:00:00+00:00"
    assert own["packages"] == fake_packages
    assert "tag" not in own


def test_baseline_fails_if_chain_exists(info_file, fake_packages, monkeypatch):
    run(monkeypatch, "record", "--name", "a", "--parent", "base")
    with pytest.raises(SystemExit) as error:
        run(monkeypatch, "baseline", "--name", "base")
    assert "already has a chain" in str(error.value)


def test_record_without_build_date_uses_now(info_file, fake_packages, monkeypatch):
    run(monkeypatch, "record", "--name", "a", "--parent", "base")
    entry = json.loads(info_file.read_text())["chain"][0]
    assert entry["built_at"].endswith("+00:00")


def test_packages_output_sorted_and_tab_separated(fake_packages, monkeypatch, capsys):
    run(monkeypatch, "packages")
    assert capsys.readouterr().out == "conda\tnumpy\t1.26.4\npip\trequests\t2.32.0\n"


def test_show_summary_and_chain(info_file, fake_packages, monkeypatch, capsys):
    run(monkeypatch, "baseline", "--name", "jupyter/base")
    run(
        monkeypatch,
        "record",
        "--name",
        "minimal-notebook",
        "--parent",
        "jupyter/base",
        "--git-commit",
        "abc1234",
        "--build-date",
        "2026-11-11T10:00:00+00:00",
    )
    run(
        monkeypatch,
        "record",
        "--name",
        "ml-notebook",
        "--parent",
        "minimal-notebook",
        "--git-commit",
        "def5678",
        "--build-date",
        "2026-11-11T11:00:00+00:00",
    )
    capsys.readouterr()

    run(monkeypatch)
    lines = tokens(capsys.readouterr().out)

    assert ["Image:", "ml-notebook"] in lines
    assert ["Packages:", "1", "conda,", "1", "pip"] in lines
    assert ["·", "jupyter/base", "[external", "base]"] in lines
    assert [
        "1", "minimal-notebook", "built", "2026-11-11T10:00:00+00:00",
        "git", "abc1234", "+0", "~0", "-0",
    ] in lines  # fmt: skip
    assert [
        "2", "ml-notebook", "built", "2026-11-11T11:00:00+00:00",
        "git", "def5678", "+0", "~0", "-0",
    ] in lines  # fmt: skip


# --------------------------------------------------------------------------- #
#   Package history                                                            #
# --------------------------------------------------------------------------- #


def tokens(out):
    """Output lines split into words, so tests don't depend on column widths."""
    return [line.split() for line in out.splitlines()]


def write_chain(info_file, *entries):
    info_file.write_text(json.dumps({"chain": list(entries)}))


BASE = {
    "name": "jupyter/base",
    "external": True,
    "packages": {"conda": {"numpy": "1.26.4"}, "pip": {"requests": "2.31.0"}},
}
MINIMAL = {
    "name": "minimal-notebook",
    "packages": {
        "conda": {"numpy": "1.26.4"},
        "pip": {"requests": "2.31.0", "foo-bar": "1.0"},
    },
}
ML = {
    "name": "ml-notebook",
    "packages": {
        "conda": {"numpy": "2.0.1"},
        "pip": {"numpy": "2.0.1", "foo-bar": "1.0"},
    },
}


def test_why_reports_each_layer_and_source(info_file, monkeypatch, capsys):
    write_chain(info_file, BASE, MINIMAL, ML)
    run(monkeypatch, "why", "numpy")

    assert tokens(capsys.readouterr().out) == [
        ["conda", "numpy", "1.26.4", "present", "in", "jupyter/base"],
        ["conda", "numpy", "2.0.1", "changed", "in", "ml-notebook", "(was", "1.26.4)"],
        ["pip", "numpy", "2.0.1", "added", "in", "ml-notebook"],
    ]


def test_why_reports_removal(info_file, monkeypatch, capsys):
    write_chain(info_file, BASE, MINIMAL, ML)
    run(monkeypatch, "why", "requests")

    assert tokens(capsys.readouterr().out) == [
        ["pip", "requests", "2.31.0", "present", "in", "jupyter/base"],
        ["pip", "requests", "-", "removed", "in", "ml-notebook"],
    ]


def test_why_matches_normalized_name(info_file, monkeypatch, capsys):
    write_chain(info_file, BASE, MINIMAL, ML)
    run(monkeypatch, "why", "Foo_Bar")

    assert tokens(capsys.readouterr().out) == [
        ["pip", "foo-bar", "1.0", "added", "in", "minimal-notebook"],
    ]


def test_why_unknown_package_fails(info_file, monkeypatch):
    write_chain(info_file, BASE, MINIMAL)
    with pytest.raises(SystemExit) as error:
        run(monkeypatch, "why", "pandas")
    assert "not in any layer" in str(error.value)


def test_chain_shows_package_changes_per_layer(info_file, monkeypatch, capsys):
    write_chain(info_file, BASE, MINIMAL, ML)
    run(monkeypatch)
    lines = tokens(capsys.readouterr().out)

    # minimal: foo-bar added; ml: numpy (pip) added, numpy (conda) changed,
    # requests removed
    assert ["1", "minimal-notebook", "built", "?", "+1", "~0", "-0"] in lines
    assert ["2", "ml-notebook", "built", "?", "+1", "~1", "-1"] in lines


def test_show_without_info_file_fails(info_file, monkeypatch):
    with pytest.raises(SystemExit):
        run(monkeypatch)


def test_field_prints_one_value(info_file, fake_packages, monkeypatch, capsys):
    run(monkeypatch, "record", "--name", "a", "--parent", "base", "--git-commit", "abc")
    capsys.readouterr()
    run(monkeypatch, "--field", "git_commit")
    assert capsys.readouterr().out == "abc\n"
