import subprocess

import pytest
from repo import RepoError, changed_files


def git(root, *args):
    identity = ["-c", "user.name=test", "-c", "user.email=test@example.com"]
    subprocess.run(["git", *identity, *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo_dir(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / "a.txt").write_text("1")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "first")
    return tmp_path


def test_only_committed_changes_count(repo_dir):
    (repo_dir / "b.txt").write_text("2")
    git(repo_dir, "add", ".")
    git(repo_dir, "commit", "-q", "-m", "second")
    (repo_dir / "a.txt").write_text("changed, not committed")

    assert changed_files(repo_dir, "HEAD~1") == ["b.txt"]


def test_unknown_ref_fails(repo_dir):
    with pytest.raises(RepoError, match="unknown ref 'nope'"):
        changed_files(repo_dir, "nope")
