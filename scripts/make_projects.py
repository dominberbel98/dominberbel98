"""profile.json → assets/projects.svg y assets/projects-m.svg.

Escritorio: salida falsa de `ls -la`, una fila por proyecto.
Móvil: una ficha por proyecto, con la descripción partida en líneas, porque
una fila de 70 caracteres no cabe legible en 330 px.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "projects.svg"
OUT_MOBILE = ROOT / "assets" / "projects-m.svg"

W = theme.WIDTH_FULL   # 840
PAD = 16
FIRST_Y = 70
STEP = 46
LED_X = PAD + 5
MODE_X = 34
NAME_X = 132
DESC_X = 320
STAGGER_MS = 120
MODE = "drwxr-xr-x"
N_PROJECTS_DESKTOP_H = 4
H = FIRST_Y + (N_PROJECTS_DESKTOP_H - 1) * STEP + 16 + 26 + PAD + 4

CSS = "".join([
    "@keyframes enter{from{opacity:0;transform:translateY(4px)}"
    "to{opacity:1;transform:translateY(0)}}",
    ".ln{animation:enter 360ms ease-out both}",
    theme.CURSOR_CSS,
    theme.LED_CSS,
    theme.FLICKER_CSS,
])


def _wrap_svg(w: int, h: int, name: str, parts: list[str]) -> str:
    return "".join([
        theme.svg_open(w, h, f"Proyectos destacados de {name}"),
        theme.defs(),
        theme.style(CSS + theme.beam_css(h, seconds=10, delay=3)),
        theme.background(w, h),
        f'<g class="flick" filter="url(#bloom)">{"".join(parts)}</g>',
        theme.beam(w),
        theme.scanlines(w, h),
        theme.svg_close(),
    ])


def render(profile: dict, mobile: bool = False) -> str:
    if mobile:
        return render_mobile(profile)
    identity = profile["identity"]
    items = profile["projects"]
    parts = [theme.prompt(PAD, 32, "ls -la projects/", size=15)]

    for i, item in enumerate(items):
        y = FIRST_Y + i * STEP
        delay = f"animation-delay:{i * STAGGER_MS}ms"
        parts.append(
            f'<g class="ln" style="{delay}">'
            f'{theme.led(LED_X, y - 4, delay_ms=i * 450)}'
            f'<text x="{MODE_X}" y="{y}" fill="{theme.OUTLINE}" font-family="{theme.MONO}" '
            f'font-size="12">{MODE}</text>'
            f'<text x="{NAME_X}" y="{y}" fill="{theme.GREEN_BRIGHT}" font-weight="700" '
            f'font-family="{theme.MONO}" font-size="14">{theme.esc(item["name"])}</text>'
            f'<text x="{DESC_X}" y="{y}" fill="{theme.GREEN}" font-family="{theme.MONO}" '
            f'font-size="13">{theme.esc(item["en"])}</text>'
            f'<text x="{DESC_X}" y="{y + 16}" fill="{theme.MUTED}" '
            f'font-family="{theme.MONO}" font-size="12">{theme.esc(item["es"])}</text>'
            "</g>"
        )

    last_y = FIRST_Y + (len(items) - 1) * STEP + 16
    parts.append(theme.prompt(PAD, last_y + 26, "", size=15))
    parts.append(theme.cursor(PAD + 18, last_y + 13))
    h = max(H, last_y + 26 + PAD + 4)
    return _wrap_svg(W, h, identity["name"], parts)


def render_mobile(profile: dict) -> str:
    identity = profile["identity"]
    items = profile["projects"]
    w = theme.WIDTH_MOBILE
    text_x = PAD + 14
    limit = theme.max_chars(w - text_x - PAD, 13)
    parts = [theme.prompt(PAD, 32, "ls projects/", size=15)]

    y = 68
    for i, item in enumerate(items):
        top = y - 16
        block = [
            theme.led(text_x + 5, y - 5, delay_ms=i * 450),
            f'<text x="{text_x + 18}" y="{y}" fill="{theme.GREEN_BRIGHT}" font-weight="700" '
            f'font-family="{theme.MONO}" font-size="16">{theme.esc(item["name"])}</text>',
        ]
        y += 24
        for chunk in theme.wrap(item["en"], limit):
            block.append(theme.text(text_x, y, chunk, fill=theme.GREEN, size=13))
            y += 18
        y += 2
        for chunk in theme.wrap(item["es"], limit):
            block.append(theme.text(text_x, y, chunk, fill=theme.MUTED, size=13))
            y += 18
        # Filete lateral: marca dónde empieza y acaba cada proyecto.
        block.append(
            f'<rect x="{PAD}" y="{top}" width="2" height="{y - 14 - top}" '
            f'fill="{theme.GREEN_DEEP}"/>'
        )
        parts.append(
            f'<g class="ln" style="animation-delay:{i * STAGGER_MS}ms">{"".join(block)}</g>'
        )
        y += 22

    parts.append(theme.prompt(PAD, y + 4, "", size=15))
    parts.append(theme.cursor(PAD + 18, y - 9))
    return _wrap_svg(w, y + 4 + PAD + 4, identity["name"], parts)


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    OUT.write_text(render(profile), encoding="utf-8")
    OUT_MOBILE.write_text(render(profile, mobile=True), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)} y {OUT_MOBILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
