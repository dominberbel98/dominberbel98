"""profile.json → assets/projects.svg. Salida falsa de `ls -la`."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "projects.svg"

W = theme.WIDTH_FULL   # 840
H = 236
PAD = 16
FIRST_Y = 64
STEP = 38
NAME_X = 116
DESC_X = 320
STAGGER_MS = 120
MODE = "drwxr-xr-x"


def render(profile: dict) -> str:
    items = profile["projects"]
    parts = [theme.prompt(PAD, 30, "ls -la projects/", size=14)]

    for i, item in enumerate(items):
        y = FIRST_Y + i * STEP
        delay = f"animation-delay:{i * STAGGER_MS}ms"
        parts.append(
            f'<g class="ln" style="{delay}">'
            f'<text x="{PAD}" y="{y}" fill="{theme.MUTED}" font-family="{theme.MONO}" '
            f'font-size="11">{MODE}</text>'
            f'<text x="{NAME_X}" y="{y}" fill="{theme.GREEN_BRIGHT}" '
            f'font-family="{theme.MONO}" font-size="12">{theme.esc(item["name"])}</text>'
            f'<text x="{DESC_X}" y="{y}" fill="{theme.GREEN}" font-family="{theme.MONO}" '
            f'font-size="11">{theme.esc(item["en"])}</text>'
            f'<text x="{DESC_X}" y="{y + 13}" fill="{theme.MUTED}" '
            f'font-family="{theme.MONO}" font-size="10">{theme.esc(item["es"])}</text>'
            "</g>"
        )

    last_y = FIRST_Y + (len(items) - 1) * STEP + 13
    parts.append(theme.prompt(PAD, last_y + 26, "", size=14))
    parts.append(theme.cursor(PAD + 16, last_y + 14))

    css = "".join([
        "@keyframes enter{from{opacity:0;transform:translateY(4px)}"
        "to{opacity:1;transform:translateY(0)}}",
        ".ln{animation:enter 360ms ease-out both}",
        theme.CURSOR_CSS,
        theme.FLICKER_CSS,
    ])

    return "".join([
        theme.svg_open(W, H, "Proyectos destacados de Domingo Berbel"),
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
