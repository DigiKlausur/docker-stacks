"""The only module that asks a registry about images (needs `docker login`)."""

import subprocess


def exists(ref: str) -> bool:
    """Whether the image `ref` (e.g. ghcr.io/org/stack/ml-notebook:latest) exists."""
    result = subprocess.run(
        ["docker", "buildx", "imagetools", "inspect", ref],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0
