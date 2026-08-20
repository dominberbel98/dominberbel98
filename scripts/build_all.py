"""Regenera todos los SVG. El heatmap necesita data/contributions.json.

Uso local: python3 -m scripts.build_all
En CI solo se ejecutan fetch_contributions + render_heatmap_svg.
"""

from __future__ import annotations

from pathlib import Path

from scripts import (
    make_ascii_svg,
    make_header,
    make_info_card,
    make_projects,
    make_stack_bars,
    render_heatmap_svg,
)

ROOT = Path(__file__).resolve().parent.parent

CONTENT_STEPS = [
    ("header.svg", make_header.main),
    ("ascii-portrait.svg", make_ascii_svg.main),
    ("info-card.svg", make_info_card.main),
    ("stack-bars.svg", make_stack_bars.main),
    ("projects.svg", make_projects.main),
]


def build(skip_heatmap: bool = False) -> list[str]:
    built: list[str] = []
    for name, run in CONTENT_STEPS:
        run()
        built.append(name)

    if skip_heatmap:
        return built

    if not (ROOT / "data" / "contributions.json").exists():
        print("aviso: falta data/contributions.json — "
              "ejecuta python3 -m scripts.fetch_contributions primero")
        return built

    render_heatmap_svg.main()
    built.append("contrib-heatmap.svg")
    return built


if __name__ == "__main__":
    print(f"generados: {', '.join(build())}")
