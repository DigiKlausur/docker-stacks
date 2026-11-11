import json
import sys

import image_info
import pytest

SHA_1 = "abc1234" + "0" * 33
SHA_2 = "def5678" + "0" * 33


@pytest.fixture
def info_file(tmp_path, monkeypatch):
    path = tmp_path / "image-info.json"
    monkeypatch.setattr(image_info, "INFO_FILE", str(path))
    return path


def run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["image_info", *argv])
    image_info.main()


def record(monkeypatch, name, parent, commit, date):
    run(
        monkeypatch,
        "record",
        "--name", name,
        "--parent", parent,
        "--git-commit", commit,
        "--build-date", date,
    )  # fmt: skip


def tokens(out):
    """Output lines split into words, so tests don't depend on column widths."""
    return [line.split() for line in out.splitlines()]


def test_record_appends_to_the_chain(info_file, monkeypatch):
    record(monkeypatch, "minimal-notebook", "jupyter/base", SHA_1, "2026-11-11T10:00")
    record(monkeypatch, "ml-notebook", "minimal-notebook", SHA_2, "2026-11-11T11:00")

    first, second = json.loads(info_file.read_text())["chain"]
    assert first["name"] == "minimal-notebook"
    assert first["parent"] == "jupyter/base"
    assert first["git_commit"] == SHA_1
    assert first["built_at"] == "2026-11-11T10:00"
    assert "python" in first
    assert second["name"] == "ml-notebook"
    assert "tag" not in first and "packages" not in first


def test_record_without_build_date_uses_now(info_file, monkeypatch):
    run(monkeypatch, "record", "--name", "a", "--parent", "base")
    entry = json.loads(info_file.read_text())["chain"][0]
    assert entry["built_at"].endswith("+00:00")


def test_show_summary_and_chain(info_file, monkeypatch, capsys):
    record(monkeypatch, "minimal-notebook", "jupyter/base", SHA_1, "2026-11-11T10:00")
    record(monkeypatch, "ml-notebook", "minimal-notebook", SHA_2, "2026-11-11T11:00")

    run(monkeypatch)
    lines = tokens(capsys.readouterr().out)

    assert ["Image:", "ml-notebook"] in lines
    assert ["Commit:", SHA_2] in lines  # full SHA in the summary
    assert ["·", "jupyter/base", "[external", "base]"] in lines
    # short SHA in the chain
    assert [
        "1", "minimal-notebook", "built", "2026-11-11T10:00", "git", "abc1234",
    ] in lines  # fmt: skip
    assert [
        "2", "ml-notebook", "built", "2026-11-11T11:00", "git", "def5678",
    ] in lines  # fmt: skip


def test_show_without_info_file_fails(info_file, monkeypatch):
    with pytest.raises(SystemExit) as error:
        run(monkeypatch)
    assert "No image info found" in str(error.value)


def test_field_prints_one_value(info_file, monkeypatch, capsys):
    record(monkeypatch, "a", "base", SHA_1, "2026-11-11T10:00")
    run(monkeypatch, "--field", "git_commit")
    assert capsys.readouterr().out == f"{SHA_1}\n"


def test_json_prints_the_whole_file(info_file, monkeypatch, capsys):
    record(monkeypatch, "a", "base", SHA_1, "2026-11-11T10:00")
    run(monkeypatch, "--json")
    assert json.loads(capsys.readouterr().out) == json.loads(info_file.read_text())
