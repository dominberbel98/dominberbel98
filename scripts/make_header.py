"""profile.json → assets/header.svg y assets/header-m.svg.

Cabecera del perfil: prompt tecleado con el enlace a la web, el nombre en
píxeles de fósforo recorrido por una onda de brillo, y el titular bilingüe.
En el README va envuelta en un <a>, así que la pieza entera es clicable.

El nombre se dibuja con rectángulos (fuente bitmap 5×7 propia) y no con
<text>: es la única forma de que se vea igual en cualquier sistema, porque un
SVG cargado como <img> no puede traer fuentes externas.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "header.svg"
OUT_MOBILE = ROOT / "assets" / "header-m.svg"

W = theme.WIDTH_FULL
PAD = 16

# Ancho asumido por carácter con la pila monoespaciada del sistema. No hace
# falta que sea exacto: solo fija el textLength que se le impone al <text> del
# prompt, así que el ancho renderizado coincide siempre con este valor sea
# cual sea la fuente del visitante (misma técnica que make_ascii_svg.py).
CHAR_W = 9.6          # a font-size 16 (escritorio)
CHAR_W_MOBILE = 9.0   # a font-size 15 (móvil)

MAX_PITCH = 9.6       # px por píxel del nombre
WAVE_STEP_MS = 45     # desfase de la onda entre columnas
WAVE_S = 5.2

GLYPHS = {
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
}
GLYPH_W = 5
GLYPH_H = 7
GLYPH_ADVANCE = GLYPH_W + 1


def line_cols(line: str) -> int:
    return len(line) * GLYPH_ADVANCE - 1


def pixel_name(lines: list[str], x0: float, y0: float, pitch: float,
               line_gap: float) -> tuple[str, float, int]:
    """Devuelve (rects, y final, nº de columnas) del nombre en píxeles."""
    cell = round(pitch - 1.6, 1)
    rects: list[str] = []
    y = y0
    for line in lines:
        for ci, ch in enumerate(line):
            rows = GLYPHS.get(ch)
            if rows is None:   # espacio o letra fuera de la fuente
                continue
            for r, bits in enumerate(rows):
                for c, bit in enumerate(bits):
                    if bit != "1":
                        continue
                    col = ci * GLYPH_ADVANCE + c
                    rects.append(
                        f'<rect class="px k{col}" x="{x0 + col * pitch:.1f}" '
                        f'y="{y + r * pitch:.1f}" width="{cell}" height="{cell}"/>'
                    )
        y += GLYPH_H * pitch + line_gap
    return "".join(rects), y - line_gap, max(line_cols(l) for l in lines)


def render(profile: dict, mobile: bool = False) -> str:
    identity = profile["identity"]
    name = identity["name"]
    site = identity["site"]
    url = f"https://{site}"
    command = f"open {url}"
    w = theme.WIDTH_MOBILE if mobile else W
    inner = w - 2 * PAD

    # Caracteres visibles del prompt completo: el prefijo "> " (2) más el
    # comando. Determina tanto los steps() del tecleo como el textLength.
    prompt_chars = len("> ") + len(command)
    prompt_size = 15 if mobile else 16
    text_length = round(prompt_chars * (CHAR_W_MOBILE if mobile else CHAR_W), 1)

    prompt_line = (
        f'<text class="type" x="{PAD}" y="34" font-family="{theme.MONO}" '
        f'font-size="{prompt_size}" textLength="{text_length}" '
        f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{theme.AMBER}">&gt; </tspan>'
        f'<tspan fill="{theme.GREEN}">open </tspan>'
        f'<tspan fill="{theme.CYAN}">{theme.esc(url)}</tspan>'
        "</text>"
    )
    body = [prompt_line, theme.cursor(PAD + text_length + 6, 21, w=9, h=17)]

    lines = name.upper().split() if mobile else [name.upper()]
    widest = max(line_cols(l) for l in lines)
    pitch = min(MAX_PITCH, math.floor(inner / widest * 10) / 10)
    pixels, name_bottom, cols = pixel_name(lines, PAD, 58, pitch, line_gap=14)
    body.append(f"<g>{pixels}</g>")

    role = f'{identity["role"]} @ {identity["company"]}'
    y = name_bottom + (34 if mobile else 36)
    size = 14 if mobile else 15
    if mobile:
        body.append(theme.led(PAD + 5, y - 5, delay_ms=0))
        body.append(theme.text(PAD + 18, y, role, fill=theme.AMBER, size=size,
                               cls="ln l0"))
        y += 30
    else:
        # En escritorio el cargo va a la derecha, en la línea del prompt.
        body.append(theme.led(w - PAD - 5, 29))
        body.append(theme.text(w - PAD - 18, 34, role, fill=theme.AMBER, size=14,
                               extra='text-anchor="end"'))

    limit = theme.max_chars(inner, size)
    for i, (lang, fill) in enumerate((("en", theme.GREEN), ("es", theme.MUTED))):
        for chunk in theme.wrap(profile["headline"][lang], limit):
            body.append(theme.text(PAD, y, chunk, fill=fill, size=size,
                                   cls=f"ln l{i + 1}"))
            y += 20 if mobile else 22
        y += 6 if mobile else 0
    h = round(y - (4 if mobile else 2))

    css = "".join([
        "@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}",
        f".type{{animation:type 1.1s steps({prompt_chars}, end) both}}",
        "@keyframes enter{from{opacity:0;transform:translateX(-6px)}"
        "to{opacity:1;transform:translateX(0)}}",
        ".ln{animation:enter 420ms cubic-bezier(.2,.8,.2,1) both}",
        ".l0{animation-delay:1150ms}.l1{animation-delay:1270ms}"
        ".l2{animation-delay:1390ms}",
        # Onda de brillo que cruza el nombre de izquierda a derecha.
        f"@keyframes wave{{0%,22%,100%{{fill:{theme.GREEN_DIM}}}"
        f"6%{{fill:#f2fff0}}12%{{fill:{theme.GREEN}}}}}",
        f".px{{fill:{theme.GREEN_DIM};animation:wave {WAVE_S}s linear infinite}}",
        *(f".k{c}{{animation-delay:{c * WAVE_STEP_MS}ms}}" for c in range(cols)),
        theme.CURSOR_CSS,
        theme.LED_CSS,
        theme.beam_css(h, seconds=8, delay=2),
        theme.FLICKER_CSS,
    ])

    return "".join([
        theme.svg_open(w, h, f"{name} — {site}"),
        theme.defs(),
        theme.style(css),
        theme.background(w, h),
        f'<rect x="0" y="{h - 1}" width="{w}" height="1" fill="{theme.OUTLINE}"/>',
        f'<g class="flick" filter="url(#bloom)">{"".join(body)}</g>',
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
