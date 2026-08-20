import json
import re
from pathlib import Path

import pytest

from scripts import theme
from scripts.make_projects import H, PAD, render

PROFILE = json.loads(Path("data/profile.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def svg():
    return render(PROFILE)


def test_lists_every_project(svg):
    for item in PROFILE["projects"]:
        assert theme.esc(item["name"]) in svg


def test_each_project_is_bilingual(svg):
    for item in PROFILE["projects"]:
        assert theme.esc(item["en"]) in svg
        assert theme.esc(item["es"]) in svg


def test_tfm_reports_third_place(svg):
    assert "3ª posición en becas UCM" in svg
    assert "1ª posición" not in svg


def test_ends_with_a_blinking_cursor(svg):
    assert 'class="cur"' in svg
    assert "@keyframes blink" in svg


def test_is_full_width(svg):
    assert f'width="{theme.WIDTH_FULL}"' in svg


def test_carries_reduced_motion_guard(svg):
    assert "prefers-reduced-motion" in svg


def test_has_no_script(svg):
    assert "<script" not in svg


def test_footer_cursor_keeps_bottom_margin(svg):
    """El cursor del pie no puede llegar al borde del lienzo: a diferencia
    de header.svg, projects.svg no tiene línea de borde inferior que lo
    contenga, así que el único margen posible es el hueco entre el cursor
    y H. Debe quedar al menos PAD px por encima del borde inferior.

    Se mide sobre el <rect class="cur"> ya renderizado (no se reimplementa
    la aritmética de render()), así que sigue protegiendo aunque cambie el
    número de proyectos en data/profile.json.
    """
    cursor_match = re.search(r'<rect[^>]*class="cur"[^>]*/>', svg)
    assert cursor_match, "no se encontró el cursor del pie"
    cursor_tag = cursor_match.group(0)

    y_match = re.search(r'\by="([\d.]+)"', cursor_tag)
    height_match = re.search(r'\bheight="([\d.]+)"', cursor_tag)
    assert y_match and height_match, "el cursor debe declarar y y height"

    cursor_bottom = float(y_match.group(1)) + float(height_match.group(1))
    margin = H - cursor_bottom

    assert margin >= PAD, (
        f"el cursor termina en {cursor_bottom}px dentro de un lienzo de "
        f"{H}px (margen {margin}px); se requieren al menos {PAD}px"
    )
