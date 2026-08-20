"""profile.json → assets/stack-bars.svg.

Las barras son relativas entre sí. El entero de profile.json solo fija la
anchura; nunca se imprime como texto.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "stack-bars.svg"

W = theme.WIDTH_FULL   # 840
H = 260
PAD = 16
FIRST_BAR_Y = 64
BAR_STEP = 24
BAR_X = 130
BAR_W = 600
BAR_H = 12
STAGGER_MS = 90


def render(profile: dict) -> str:
    items = profile["stack"]
    parts = [theme.prompt(PAD, 30, "cat stack.txt", size=14)]

    for i, item in enumerate(items):
        y = FIRST_BAR_Y + i * BAR_STEP
        fill_w = round(BAR_W * item["level"] / 100, 1)
        parts.append(
            f'<text x="{PAD}" y="{y}" fill="{theme.AMBER}" font-family="{theme.MONO}" '
            f'font-size="12">{theme.esc(item["label"])}</text>'
        )
        parts.append(
            f'<rect x="{BAR_X}" y="{y - 10}" width="{BAR_W}" height="{BAR_H}" '
            f'fill="{theme.BG_RAISED}"/>'
        )
        parts.append(
            f'<rect class="bar" x="{BAR_X}" y="{y - 10}" width="{fill_w}" '
            f'height="{BAR_H}" fill="{theme.GREEN}" style="animation-delay:{i * STAGGER_MS}ms"/>'
        )

    css = "".join([
        "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
        ".bar{transform-box:fill-box;transform-origin:left center;"
        "animation:grow 700ms cubic-bezier(.2,.8,.2,1) both}",
        theme.FLICKER_CSS,
    ])

    return "".join([
        theme.svg_open(W, H, "Stack técnico de Domingo Berbel"),
        theme.defs(),
        theme.style(css),
        theme.background(W, H),
        f'<g class="flick" filter="url(#bloom)">{"".join(parts)}</g>',
        theme.scanlines(W, H),
        theme.svg_close(),
    ])


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    OUT.write_text(render(profile), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
