import re
from datetime import date, timedelta

import pytest

from scripts import theme
from scripts.render_heatmap_svg import (
    CHAR_W,
    LEGEND_Y,
    PAD,
    STATS_Y,
    legend_ranges,
    level,
    render,
    thresholds,
    window,
)


def test_thresholds_are_non_decreasing():
    th = thresholds([1, 2, 3, 4, 5, 9, 12, 20])
    assert th == sorted(th)


def test_thresholds_ignore_empty_days():
    assert thresholds([0, 0, 0, 5, 5]) == thresholds([5, 5])


def test_thresholds_of_empty_input_do_not_crash():
    assert len(thresholds([])) == 4


def test_level_zero_for_no_activity():
    assert level(0, [1, 2, 3, 4]) == 0


def test_level_is_monotonic_in_count():
    th = thresholds([1, 2, 3, 4, 5, 9, 12, 20])
    levels = [level(c, th) for c in range(0, 40)]
    assert levels == sorted(levels)


def test_level_never_exceeds_palette():
    th = thresholds([1, 2, 3])
    assert level(10_000, th) == len(theme.HEAT_LEVELS) - 1


def test_an_outlier_does_not_flatten_the_rest():
    """El pico real de 47 no debe empujar los días normales al nivel más bajo."""
    counts = [1] * 40 + [2] * 30 + [3] * 20 + [5] * 8 + [11] * 2 + [47]
    th = thresholds(counts)
    assert level(3, th) >= 2, "un día de 3 commits no puede quedar en el nivel más pálido"
    assert level(47, th) == len(theme.HEAT_LEVELS) - 1


def test_window_keeps_the_last_n_weeks():
    days = [{"date": f"2026-01-{d:02d}", "count": 0} for d in range(1, 29)]
    assert len(window(days, weeks=2)) == 14


def test_window_shorter_than_requested_is_returned_whole():
    days = [{"date": "2026-01-01", "count": 1}]
    assert len(window(days, weeks=53)) == 1


DATA = {
    "days": [{"date": f"2026-08-{d:02d}", "count": d % 4} for d in range(1, 21)],
    "total": 30,
    "active_days": 15,
    "longest_streak": 3,
    "current_streak": 1,
    "best_day": {"date": "2026-08-19", "count": 3},
    "first_date": "2026-08-01",
    "last_date": "2026-08-20",
}


@pytest.fixture(scope="module")
def svg():
    return render(DATA, weeks=53)


def test_prints_the_real_total(svg):
    """Debe ir en el panel de métricas, no valer un 30 suelto de coordenadas."""
    assert f'>{DATA["total"]}</text>' in svg


def test_prints_the_real_date_range(svg):
    assert "2026-08-01" in svg and "2026-08-20" in svg


def test_grid_fits_inside_the_canvas(svg):
    """53 columnas a paso 14 terminan en x=788, dentro de los 840."""
    xs = [float(x) for x in re.findall(r'<rect class="c" x="([\d.]+)"', svg)]
    assert xs, "no se ha dibujado ninguna celda"
    assert max(xs) + 12 <= theme.WIDTH_FULL - 16


def _stat_row_texts(svg: str) -> list[tuple[float, str]]:
    """(x, contenido) de cada `<text>` de la fila de métricas (y=STATS_Y).

    Incluye tanto las etiquetas ("best day") como los valores ("47 · 08-17"):
    ambos son texto real que puede desbordar el lienzo.
    """
    pattern = rf'<text x="([\d.]+)" y="{STATS_Y}"[^>]*>([^<]*)</text>'
    return [(float(x), content) for x, content in re.findall(pattern, svg)]


def _stat_row_tags(svg: str) -> list[tuple[float, str, str]]:
    """(x, atributos completos, contenido) de cada `<text>` de la fila de métricas.

    A diferencia de `_stat_row_texts`, conserva los atributos del tag para
    poder comprobar que lleva `textLength`/`lengthAdjust`: sin ellos, la
    garantía de no-solape depende de que la fuente monoespaciada real del
    visitante avance exactamente `CHAR_W` px por carácter, algo que no está
    garantizado (medido con `getBBox()` real: 25.8 px de hueco entre
    métricas contra los 26 nominales de `METRIC_GAP`, es decir, `CHAR_W` ya
    subestima ligeramente el glifo real en el único navegador probado).
    """
    pattern = rf'<text x="([\d.]+)" y="{STATS_Y}"([^>]*)>([^<]*)</text>'
    return [(float(x), attrs, content) for x, attrs, content in re.findall(pattern, svg)]


def test_no_metric_in_the_stats_row_overflows_the_canvas():
    """Regresión: ninguna métrica de la fila puede rebasar el borde derecho.

    Cubre la clase de fallo entera, no solo `best day`: recorre TODAS las
    métricas de la fila, estima el borde derecho de cada una a partir de su
    x real en el SVG y su longitud en caracteres (a CHAR_W px/carácter,
    importado del módulo, nunca repetido como número suelto aquí), y exige
    que ninguna rebase `W - PAD`.

    Con el layout derivado del contenido (cada métrica empieza donde acaba
    la anterior más el hueco entre métricas) el valor de `best day`, con el
    formato compacto `"{count} · {mm-dd}"`, cabe sin tocar constantes de
    ancho fijo.
    """
    data = dict(DATA, best_day={"date": "2026-08-17", "count": 47})
    svg = render(data, weeks=53)
    texts = _stat_row_texts(svg)
    assert texts, "no se ha encontrado ningún texto en la fila de métricas"
    for x, content in texts:
        right_edge = x + len(content) * CHAR_W
        assert right_edge <= theme.WIDTH_FULL - PAD, (
            f"{content!r} en x={x} rebasa el lienzo "
            f"(borde estimado={right_edge:.1f}, límite={theme.WIDTH_FULL - PAD})"
        )


def test_stats_row_still_fits_with_a_three_digit_best_day_count():
    """No debe volver a romperse si algún día `best_day.count` llega a 3 cifras."""
    data = dict(DATA, best_day={"date": "2026-12-31", "count": 999})
    svg = render(data, weeks=53)
    for x, content in _stat_row_texts(svg):
        right_edge = x + len(content) * CHAR_W
        assert right_edge <= theme.WIDTH_FULL - PAD, (
            f"{content!r} en x={x} rebasa el lienzo con un best_day de 3 cifras"
        )


def test_no_metric_in_the_stats_row_overlaps_the_next_one():
    """La propiedad que de verdad importa: ninguna métrica pisa a la siguiente.

    No basta con no salirse del lienzo por la derecha (eso ya lo cubren los
    dos tests anteriores): con una rejilla de huecos de ancho fijo, un valor
    puede seguir cabiendo dentro del lienzo y aun así invadir la etiqueta de
    la métrica siguiente si esta empieza demasiado pronto. Es exactamente lo
    que le pasó a `active days` (`"149 / 369"`) contra la etiqueta `longest`
    al estrechar `SLOT_W` de 164 a 156.

    Se ejercita con valores artificialmente largos —un `total` de cinco
    cifras, una ventana de 369 días (para que `active days` imprima
    `"149 / 369"`, con tres cifras a cada lado de la barra) y un
    `best_day.count` de tres cifras— para que la propiedad se siga
    cumpliendo aunque los datos crezcan, no solo con los del fixture `DATA`
    de hoy.

    Con el layout de huecos fijos (`SLOT_W`/`VALUE_DX`) este test falla: el
    valor de `active days` termina más a la derecha de donde empieza la
    etiqueta `longest`. Con el layout derivado del contenido, cada métrica
    reserva exactamente el espacio que necesita, así que la separación con
    la siguiente es siempre positiva.
    """
    start = date(2025, 8, 17)
    days = [
        {"date": (start + timedelta(days=d)).isoformat(), "count": 0}
        for d in range(369)
    ]
    data = dict(
        DATA,
        days=days,
        total=12345,
        active_days=149,
        best_day={"date": "2026-08-17", "count": 999},
    )
    svg = render(data, weeks=53)
    texts = _stat_row_texts(svg)
    assert len(texts) == 10, "se esperan 5 pares etiqueta/valor en la fila de métricas"

    labels = texts[0::2]
    values = texts[1::2]
    for (value_x, value_content), (next_label_x, _next_label) in zip(values, labels[1:]):
        right_edge = value_x + len(value_content) * CHAR_W
        gap = next_label_x - right_edge
        assert gap > 0, (
            f"{value_content!r} (borde derecho={right_edge:.1f}) choca contra "
            f"la siguiente etiqueta en x={next_label_x} (hueco={gap:.1f})"
        )

    last_value_x, last_value_content = values[-1]
    last_right_edge = last_value_x + len(last_value_content) * CHAR_W
    assert last_right_edge <= theme.WIDTH_FULL - PAD, (
        f"la última métrica rebasa el lienzo: borde={last_right_edge:.1f}, "
        f"límite={theme.WIDTH_FULL - PAD}"
    )

    # La garantía de no-solape de arriba solo vale si el ancho renderizado
    # coincide con el estimado por CHAR_W. Sin `textLength`, eso depende de
    # que la fuente del visitante avance exactamente lo que asume CHAR_W;
    # con `textLength` + `lengthAdjust="spacingAndGlyphs"` el navegador está
    # obligado a dibujar el texto en ese ancho exacto, sea cual sea la
    # fuente instalada.
    for x, attrs, content in _stat_row_tags(svg):
        expected_length = round(len(content) * CHAR_W, 1)
        m = re.search(r'textLength="([\d.]+)"', attrs)
        assert m, f"{content!r} en x={x} no fija textLength"
        assert float(m.group(1)) == pytest.approx(expected_length, abs=0.05), (
            f"{content!r}: textLength={m.group(1)} no coincide con "
            f"len(cadena)*CHAR_W={expected_length}"
        )
        assert 'lengthAdjust="spacingAndGlyphs"' in attrs, (
            f'{content!r} en x={x} no lleva lengthAdjust="spacingAndGlyphs"'
        )


def test_legend_ranges_prints_bare_numbers_for_consecutive_thresholds():
    """Cuantiles pegados (los reales: 1, 2, 3, 4) hacen que cada tramo sea un
    único valor. Debe leerse como el número solo — "1", "2"... — nunca como
    "1-1", que lee como un error de formato aunque sea aritméticamente
    correcto.
    """
    assert legend_ranges([1, 2, 3, 4]) == "0, 1, 2, 3, 4, 5+ commits/day"


def test_legend_ranges_keeps_real_spans_as_a_range():
    """Umbrales separados sí deben seguir imprimiéndose como rango (p.ej. "2-4")."""
    assert legend_ranges([1, 4, 6, 10]) == "0, 1, 2-4, 5-6, 7-10, 11+ commits/day"


def test_legend_texts_pin_their_rendered_width_with_textLength(svg):
    """Misma garantía que la fila de métricas, aplicada a la leyenda.

    La leyenda posicionaba `less` y `more · rangos` con offsets fijos —el
    mismo patrón que ya causó dos defectos consecutivos en la fila de
    métricas (desbordamiento del lienzo y solape entre `active days` y
    `longest`)—. Debe seguir el mismo esquema: posiciones derivadas del
    contenido y `textLength` fijando el ancho renderizado, para que la
    garantía de no-solape no dependa de que la fuente del visitante avance
    exactamente lo que estima `CHAR_W`.
    """
    pattern = rf'<text x="([\d.]+)" y="{LEGEND_Y}"([^>]*)>([^<]*)</text>'
    tags = re.findall(pattern, svg)
    assert tags, "no se ha encontrado ningún texto en la leyenda"
    for x, attrs, content in tags:
        m = re.search(r'textLength="([\d.]+)"', attrs)
        assert m, f"{content!r} en x={x} no fija textLength"
        assert 'lengthAdjust="spacingAndGlyphs"' in attrs, (
            f'{content!r} en x={x} no lleva lengthAdjust="spacingAndGlyphs"'
        )


def test_is_full_width(svg):
    assert f'width="{theme.WIDTH_FULL}"' in svg


def test_carries_reduced_motion_guard(svg):
    assert "prefers-reduced-motion" in svg


def test_has_no_script(svg):
    assert "<script" not in svg
