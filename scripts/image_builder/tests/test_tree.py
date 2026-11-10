from helpers import make_data
from manifest import parse
from tree import render


def test_render_shows_compact_tree():
    images = {
        "minimal": {"base": "jupyter/minimal:2", "e2x": True},
        "ds": {"parent": "minimal", "e2x": True},
        "ml": {"parent": "ds"},
        "sql": {"parent": "ds", "e2x": True},
        "desktop": {"parent": "minimal"},
        "bi": {"base": "jupyter/minimal:1", "e2x": True},
    }
    expected = """\
jupyter/minimal:1
└── bi [e2x]
jupyter/minimal:2
└── minimal [e2x]
    ├── desktop
    └── ds [e2x]
        ├── ml
        └── sql [e2x]"""

    assert render(parse(make_data(images))) == expected
