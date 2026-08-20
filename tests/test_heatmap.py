import re

import pytest

from scripts import theme
from scripts.render_heatmap_svg import CHAR_W, PAD, STATS_Y, level, render, thresholds, window


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


def test_no_metric_in_the_stats_row_overflows_the_canvas():
    """Regresión: ninguna métrica de la fila puede rebasar el borde derecho.

    Cubre la clase de fallo entera, no solo `best day`: recorre TODAS las
    métricas de la fila, estima el borde derecho de cada una a partir de su
    x real en el SVG y su longitud en caracteres (a CHAR_W px/carácter,
    importado del módulo, nunca repetido como número suelto aquí), y exige
    que ninguna rebase `W - PAD`.

    Con `SLOT_W=164` y el formato largo `"{count} on {date}"` este test
    falla porque el valor de `best day` (17 caracteres) empieza demasiado a
    la derecha para caber. Tras estrechar los huecos a `SLOT_W=156` y
    compactar la fecha a `"{count} · {mm-dd}"` (10 caracteres), pasa.
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


def test_is_full_width(svg):
    assert f'width="{theme.WIDTH_FULL}"' in svg


def test_carries_reduced_motion_guard(svg):
    assert "prefers-reduced-motion" in svg


def test_has_no_script(svg):
    assert "<script" not in svg
