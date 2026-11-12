"""profile.json → assets/stack-bars.svg y assets/stack-bars-m.svg.

Las barras son relativas entre sí. El entero de profile.json solo fija la
anchura; nunca se imprime como texto.

Cada barra es un medidor de LEDs: la rejilla de huecos se pinta encima con un
patrón, y un destello la recorre en bucle para que el panel siga vivo cuando
el visitante llega a él haciendo scroll.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "stack-bars.svg"
OUT_MOBILE = ROOT / "assets" / "stack-bars-m.svg"

W = theme.WIDTH_FULL   # 840
PAD = 16
FIRST_BAR_Y = 70
BAR_STEP = 30
BAR_X = 130
BAR_W = 600
BAR_H = 16
STAGGER_MS = 90
SEGMENT = 10           # ancho de cada LED, hueco incluido
SHINE_W = 90

# Móvil: mismas barras sobre un lienzo de 420.
BAR_X_MOBILE = 112
BAR_W_MOBILE = theme.WIDTH_MOBILE - BAR_X_MOBILE - PAD


def render(profile: dict, mobile: bool = False) -> str:
    identity = profile["identity"]
    items = profile["stack"]
    w = theme.WIDTH_MOBILE if mobile else W
    bar_x = BAR_X_MOBILE if mobile else BAR_X
    bar_w = BAR_W_MOBILE if mobile else BAR_W
    h = FIRST_BAR_Y + (len(items) - 1) * BAR_STEP + 26

    parts = [theme.prompt(PAD, 32, "cat stack.txt", size=15)]
    clip: list[str] = []
    top = FIRST_BAR_Y - BAR_H + 3

    for i, item in enumerate(items):
        y = FIRST_BAR_Y + i * BAR_STEP
        bar_y = y - BAR_H + 3
        fill_w = round(bar_w * item["level"] / 100, 1)
        parts.append(
            f'<text x="{PAD}" y="{y}" fill="{theme.AMBER}" font-family="{theme.MONO}" '
            f'font-size="14">{theme.esc(item["label"])}</text>'
        )
        parts.append(
            f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{BAR_H}" '
            f'fill="{theme.BG_RAISED}"/>'
        )
        parts.append(
            f'<rect class="bar" x="{bar_x}" y="{bar_y}" width="{fill_w}" '
            f'height="{BAR_H}" fill="{theme.GREEN}" style="animation-delay:{i * STAGGER_MS}ms"/>'
        )
        clip.append(f'<rect x="{bar_x}" y="{bar_y}" width="{fill_w}" height="{BAR_H}"/>')

    bars_h = (len(items) - 1) * BAR_STEP + BAR_H
    # Destello: un único rectángulo que cruza todas las barras, recortado a la
    # parte encendida de cada una.
    parts.append(
        f'<g clip-path="url(#lit)"><rect class="shine" x="{bar_x - SHINE_W}" '
        f'y="{top}" width="{SHINE_W}" height="{bars_h}" fill="url(#shineg)"/></g>'
    )
    # Huecos entre LEDs, encima de todo lo anterior.
    parts.append(
        f'<rect x="{bar_x}" y="{top}" width="{bar_w}" height="{bars_h}" '
        f'fill="url(#seg)"/>'
    )

    css = "".join([
        "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
        ".bar{transform-box:fill-box;transform-origin:left center;"
        "animation:grow 700ms cubic-bezier(.2,.8,.2,1) both}",
        f"@keyframes shine{{0%{{transform:translateX(0)}}"
        f"45%,100%{{transform:translateX({bar_w + SHINE_W}px)}}}}",
        ".shine{animation:shine 4.5s ease-in-out 1.4s infinite}",
        theme.beam_css(h, seconds=9, delay=1),
        theme.FLICKER_CSS,
    ])
    extra_defs = (
        f'<pattern id="seg" width="{SEGMENT}" height="{BAR_H}" '
        f'patternUnits="userSpaceOnUse" x="{bar_x}">'
        f'<rect x="{SEGMENT - 2}" width="2" height="{BAR_H}" fill="{theme.BG}"/>'
        "</pattern>"
        f'<clipPath id="lit">{"".join(clip)}</clipPath>'
    )

    return "".join([
        theme.svg_open(w, h, f"Stack técnico de {identity['name']}"),
        theme.defs(extra_defs),
        theme.style(css),
        theme.background(w, h),
        f'<g class="flick" filter="url(#bloom)">{"".join(parts)}</g>',
        theme.beam(w),
        theme.scanlines(w, h),
        theme.svg_close(),
    ])


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    OUT.write_text(render(profile), encoding="utf-8")
    OUT_MOBILE.write_text(render(profile, mobile=True), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)} y {OUT_MOBILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
