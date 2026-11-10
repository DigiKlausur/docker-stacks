"""The only module that talks to git."""

import subprocess
from pathlib import Path


class RepoError(Exception):
    """Raised when a git command fails, e.g. for an unknown ref."""


def changed_files(root: Path, since: str) -> list[str]:
    """Files changed on this branch since `since`; committed changes only.

    Uses `since...HEAD` (three dots): compares against the merge base, so
    commits made on `since` in the meantime don't count. Never guesses:
    an unknown ref is an error.
    """
    _git(
        root,
        "rev-parse",
        "--verify",
        "--quiet",
        f"{since}^{{commit}}",
        error=f"unknown ref '{since}'",
    )
    return _git(root, "diff", "--name-only", f"{since}...HEAD").splitlines()


def short_sha(root: Path) -> str:
    return _git(root, "rev-parse", "--short=7", "HEAD")


def full_sha(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD")


def _git(root: Path, *args: str, error: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], check=False, cwd=root, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RepoError(
            error or f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()


if __name__ == "__main__":
    raise SystemExit("not a script: run `python scripts/image_builder -h` instead")
