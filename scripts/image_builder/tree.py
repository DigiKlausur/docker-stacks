"""Render the image tree shown by `image_builder tree`.

External base images are the roots. e2x variants don't get their own line;
instead their parent is marked with [e2x].
"""

from manifest import Manifest, children


def render(manifest: Manifest) -> str:
    nodes = manifest.nodes
    kids = children(nodes)
    lines: list[str] = []

    def add_level(names: list[str], prefix: str) -> None:
        shown = [name for name in names if not nodes[name].is_e2x]
        for index, name in enumerate(shown):
            is_last = index == len(shown) - 1
            marker = " [e2x]" if any(nodes[child].is_e2x for child in kids[name]) else ""
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{name}{marker}")
            add_level(kids[name], prefix + ("    " if is_last else "│   "))

    bases = sorted({node.base for node in nodes.values() if node.base is not None})
    for base in bases:
        lines.append(base)
        add_level(sorted(name for name, node in nodes.items() if node.base == base), prefix="")
    return "\n".join(lines)
