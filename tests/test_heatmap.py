import pytest

from scripts import theme
from scripts.render_heatmap_svg import level, render, thresholds, window


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
    import re

    xs = [float(x) for x in re.findall(r'<rect class="c" x="([\d.]+)"', svg)]
    assert xs, "no se ha dibujado ninguna celda"
    assert max(xs) + 12 <= theme.WIDTH_FULL - 16


def test_is_full_width(svg):
    assert f'width="{theme.WIDTH_FULL}"' in svg


def test_carries_reduced_motion_guard(svg):
    assert "prefers-reduced-motion" in svg


def test_has_no_script(svg):
    assert "<script" not in svg
