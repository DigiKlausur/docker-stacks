"""Shared test data."""


def make_data(images: dict | None = None) -> dict:
    """A small, valid manifest as parsed TOML. `images` replaces the [images] table."""
    return {
        "registry": {"namespace": "org/stack", "hosts": ["ghcr.io", "quay.io"], "primary": "ghcr.io"},
        "e2x": {"modes": {"student": "student", "student_exam": "exam"}},
        "tag_sets": {
            "local": {"tags": ["local"], "parent_tag": "latest"},
            "master": {"tags": ["latest", "sha-{sha}"], "parent_tag": "latest"},
        },
        "images": images
        or {
            "base-nb": {"base": "jupyter/minimal:1", "e2x": True},
            "child-nb": {"parent": "base-nb"},
        },
    }
