"""ascii-matrix.json → assets/ascii-portrait.svg.

Sin dependencias pesadas: prep_photo.py ya dejó la matriz de tinta en JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
MATRIX = ROOT / "data" / "ascii-matrix.json"
OUT = ROOT / "assets" / "ascii-portrait.svg"

SIZE = theme.WIDTH_HALF   # 420
PAD_X = 10
GRID_W = 400
FONT = 10
LINE_H = 10.3
FIRST_BASELINE = 18
ROW_DELAY_MS = 40
WIPE_MS = 520

# Más tinta, más brillo: los trazos del avatar quedan en verde vivo.
BUCKETS = [theme.GREEN_DEEP, "#00752a", theme.GREEN_DIM, theme.GREEN_BRIGHT, theme.GREEN]


def glyph(ink: float) -> str:
    """Mapea tinta 0..1 a un carácter de la rampa de densidad."""
    return theme.RAMP[min(len(theme.RAMP) - 1, int(ink * len(theme.RAMP)))]


def bucket(ink: float) -> int:
    """Mapea tinta 0..1 a uno de los cinco buckets de color."""
    return min(len(BUCKETS) - 1, int(ink * len(BUCKETS)))


def row_runs(row: list[float]) -> list[tuple[int, str]]:
    """Agrupa caracteres consecutivos del mismo bucket en un solo tspan."""
    runs: list[tuple[int, str]] = []
    for ink in row:
        b, g = bucket(ink), glyph(ink)
        if runs and runs[-1][0] == b:
            runs[-1] = (b, runs[-1][1] + g)
        else:
            runs.append((b, g))
    return runs


def render(matrix: dict) -> str:
    rows = matrix["ink"]

    css = "".join([
        "@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}",
        f".row{{animation:wipe {WIPE_MS}ms cubic-bezier(.2,.8,.2,1) both}}",
        theme.FLICKER_CSS,
        *(f".r{i}{{animation-delay:{i * ROW_DELAY_MS}ms}}" for i in range(len(rows))),
    ])

    body = []
    for i, row in enumerate(rows):
        spans = "".join(
            f'<tspan fill="{BUCKETS[b]}">{theme.esc(chunk)}</tspan>'
            for b, chunk in row_runs(row)
        )
        body.append(
            f'<text class="row r{i}" x="{PAD_X}" y="{FIRST_BASELINE + i * LINE_H:.1f}" '
            f'font-family="{theme.MONO}" font-size="{FONT}" textLength="{GRID_W}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{spans}</text>'
        )

    return "".join([
        theme.svg_open(SIZE, SIZE, "Retrato ASCII de Domingo Berbel"),
        theme.defs(),
        theme.style(css),
        theme.background(SIZE, SIZE),
        f'<g class="flick" filter="url(#bloom)">{"".join(body)}</g>',
        theme.scanlines(SIZE, SIZE),
        theme.svg_close(),
    ])


def main() -> None:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    OUT.write_text(render(matrix), encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"escrito {OUT.relative_to(ROOT)} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
