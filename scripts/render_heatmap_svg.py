"""contributions.json → assets/contrib-heatmap.svg.

Ventana de 53 semanas: el año completo, igual que el grafo propio de GitHub que
se renderiza justo debajo en el perfil. La escala por cuantiles evita que el día
pico aplaste al resto, que es lo que haría la escala absoluta de GitHub.

Las cifras impresas salen de los datos sin transformar.

Fila de métricas: el ancho de cada etiqueta y cada valor se ESTIMA como
`len(cadena) * CHAR_W` para calcular dónde empieza el siguiente elemento
(ver `render()`). Esa estimación por sí sola no garantiza nada: si la fuente
monoespaciada real del visitante avanza más de `CHAR_W` px por carácter —y
la pila `theme.MONO` cae a fuentes distintas según el sistema operativo—, el
hueco entre métricas se estrecha sin que ningún test lo detecte, porque los
tests de no-solape usan la misma fórmula y la misma constante para medir que
para posicionar (tautológico). Por eso cada `<text>` de la fila lleva además
`textLength` fijado a ese mismo ancho estimado y
`lengthAdjust="spacingAndGlyphs"`: eso obliga al navegador a dibujar el
texto exactamente en ese ancho sea cual sea la fuente instalada, así que el
ancho estimado deja de ser una estimación y pasa a ser el ancho real
(misma técnica que `make_ascii_svg.py` y `make_header.py`).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "assets" / "contrib-heatmap.svg"

W = theme.WIDTH_FULL   # 840
H = 220
PAD = 16
GRID_X = 48
GRID_Y = 60
CELL = 12
GAP = 2
PITCH = CELL + GAP     # 14
STATS_Y = 182
LABEL_VALUE_GAP = 8    # px entre la etiqueta de una métrica y su valor
METRIC_GAP = 26        # px entre el valor de una métrica y la etiqueta siguiente
LEGEND_Y = 206
CHAR_W = 6.6           # avance aproximado por carácter a font-size 11 (MONO)
CELL_DELAY_MS = 8

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def thresholds(counts: list[int]) -> list[int]:
    """Cuantiles 20/40/60/80 sobre los días CON actividad."""
    lit = sorted(c for c in counts if c > 0)
    if not lit:
        return [1, 2, 3, 4]

    def quantile(p: float) -> int:
        idx = min(len(lit) - 1, round(p * (len(lit) - 1)))
        return lit[int(idx)]

    return [quantile(0.2), quantile(0.4), quantile(0.6), quantile(0.8)]


def level(count: int, th: list[int]) -> int:
    """0 = sin actividad; 1..5 = cuantiles crecientes."""
    if count <= 0:
        return 0
    for i, limit in enumerate(th):
        if count <= limit:
            return i + 1
    return len(theme.HEAT_LEVELS) - 1


def window(days: list[dict], weeks: int) -> list[dict]:
    """Últimos `weeks × 7` días. Si hay menos, se devuelven todos."""
    return days[-(weeks * 7):]


def render(data: dict, weeks: int) -> str:
    days = window(data["days"], weeks)
    th = thresholds([d["count"] for d in days])

    parts = [
        f'<text x="{PAD}" y="26" font-family="{theme.MONO}" font-size="13">'
        f'<tspan fill="{theme.AMBER}">&gt; </tspan>'
        f'<tspan fill="{theme.GREEN}">git log --graph </tspan>'
        f'<tspan fill="{theme.MUTED}">'
        f'{theme.esc(data["first_date"])} .. {theme.esc(data["last_date"])}</tspan>'
        "</text>"
    ]

    cells: list[str] = []
    month_labels: list[str] = []
    seen_months: set[str] = set()

    for i, day in enumerate(days):
        col, row = divmod(i, 7)
        x = GRID_X + col * PITCH
        y = GRID_Y + row * PITCH
        colour = theme.HEAT_LEVELS[level(day["count"], th)]
        delay = (col + row) * CELL_DELAY_MS
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{colour}" style="animation-delay:{delay}ms"/>'
        )
        parsed = date.fromisoformat(day["date"])
        key = f"{parsed.year}-{parsed.month}"
        if row == 0 and key not in seen_months:
            seen_months.add(key)
            month_labels.append(
                f'<text x="{x}" y="52" fill="{theme.MUTED}" '
                f'font-family="{theme.MONO}" font-size="9">'
                f"{MONTHS[parsed.month - 1]}</text>"
            )

    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(
            f'<text x="{PAD}" y="{GRID_Y + row * PITCH + 9}" fill="{theme.MUTED}" '
            f'font-family="{theme.MONO}" font-size="9">{label}</text>'
        )

    parts.extend(month_labels)
    parts.append(f'<g filter="url(#bloom)">{"".join(cells)}</g>')

    stats = [
        ("total", str(data["total"])),
        ("active days", f'{data["active_days"]} / {len(days)}'),
        ("longest", f'{data["longest_streak"]} d'),
        ("current", f'{data["current_streak"]} d'),
        ("best day", f'{data["best_day"]["count"]} · {data["best_day"]["date"][5:]}'),
    ]
    # Layout derivado del contenido: cada métrica ocupa exactamente lo que
    # necesita (etiqueta + hueco + valor) y la siguiente empieza donde
    # terminó la anterior, con el hueco entre métricas. Así el ancho de un
    # dato que crece (más días en la ventana, más dígitos en el total...)
    # nunca puede invadir a la métrica siguiente — SIEMPRE que el ancho
    # renderizado coincida con `label_w`/`value_w`. `textLength` +
    # `lengthAdjust="spacingAndGlyphs"` es lo que convierte esa estimación
    # en el ancho real (ver docstring del módulo).
    x = PAD
    for label, value in stats:
        label_w = round(len(label) * CHAR_W, 1)
        value_x = x + label_w + LABEL_VALUE_GAP
        value_w = round(len(value) * CHAR_W, 1)
        parts.append(
            f'<text x="{x}" y="{STATS_Y}" fill="{theme.MUTED}" '
            f'font-family="{theme.MONO}" font-size="11" textLength="{label_w}" '
            f'lengthAdjust="spacingAndGlyphs">{label}</text>'
        )
        parts.append(
            f'<text x="{value_x}" y="{STATS_Y}" fill="{theme.GREEN}" '
            f'font-family="{theme.MONO}" font-size="11" textLength="{value_w}" '
            f'lengthAdjust="spacingAndGlyphs">{theme.esc(value)}</text>'
        )
        x = value_x + value_w + METRIC_GAP
    assert x - METRIC_GAP <= W - PAD, "la fila de métricas se sale del lienzo"

    # Leyenda con los recuentos reales de cada tono. Mismo esquema que la fila
    # de métricas de arriba: posiciones derivadas del contenido en vez de
    # offsets fijos (el patrón que causó los dos defectos consecutivos de la
    # fila de métricas), reutilizando LABEL_VALUE_GAP/METRIC_GAP en vez de
    # inventar huecos nuevos, y textLength en cada <text> para que el ancho
    # renderizado sea el ancho real, no una estimación.
    less_label = "less"
    less_w = round(len(less_label) * CHAR_W, 1)
    parts.append(
        f'<text x="{PAD}" y="{LEGEND_Y}" fill="{theme.MUTED}" '
        f'font-family="{theme.MONO}" font-size="10" textLength="{less_w}" '
        f'lengthAdjust="spacingAndGlyphs">{less_label}</text>'
    )
    swatches_x = PAD + less_w + LABEL_VALUE_GAP
    for i, colour in enumerate(theme.HEAT_LEVELS):
        parts.append(
            f'<rect x="{swatches_x + i * 16}" y="{LEGEND_Y - 10}" width="12" height="12" '
            f'rx="2" fill="{colour}"/>'
        )
    swatches_w = (len(theme.HEAT_LEVELS) - 1) * 16 + 12
    ranges = (
        f'0, 1-{th[0]}, {th[0] + 1}-{th[1]}, {th[1] + 1}-{th[2]}, '
        f'{th[2] + 1}-{th[3]}, {th[3] + 1}+ commits/day'
    )
    ranges_label = f"more · {ranges}"
    ranges_w = round(len(ranges_label) * CHAR_W, 1)
    ranges_x = swatches_x + swatches_w + METRIC_GAP
    parts.append(
        f'<text x="{ranges_x}" y="{LEGEND_Y}" '
        f'fill="{theme.MUTED}" font-family="{theme.MONO}" font-size="10" '
        f'textLength="{ranges_w}" lengthAdjust="spacingAndGlyphs">'
        f'more · {theme.esc(ranges)}</text>'
    )

    css = "".join([
        "@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}",
        ".c{transform-box:fill-box;transform-origin:center;"
        "animation:pop 320ms ease-out both}",
        theme.FLICKER_CSS,
    ])

    return "".join([
        theme.svg_open(W, H, f"Contribuciones de GitHub: {data['total']} en el periodo"),
        theme.defs(),
        theme.style(css),
        theme.background(W, H),
        f'<g class="flick">{"".join(parts)}</g>',
        theme.scanlines(W, H),
        theme.svg_close(),
    ])


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.write_text(render(data, profile["heatmap"]["weeks"]), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)}: {data['total']} contribuciones")


if __name__ == "__main__":
    main()
