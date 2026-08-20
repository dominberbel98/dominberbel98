import json
import re
from pathlib import Path

import pytest

from scripts import theme
from scripts.make_info_card import render

PROFILE = json.loads(Path("data/profile.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def svg():
    return render(PROFILE)


def test_shows_every_info_card_entry(svg):
    for entry in PROFILE["info_card"]:
        assert theme.esc(entry["label"]) in svg
        assert theme.esc(entry["value"]) in svg


def test_header_is_tricolor_user_at_handle(svg):
    """La cabecera es un <text class="ln l0"> con tres <tspan> coloreados:
    usuario, arroba y handle, en ese orden y cada uno con un fill distinto
    (estilo neofetch real). No basta con que las tres cadenas aparezcan en
    algún sitio del SVG: tienen que vivir en tspans consecutivos de la
    cabecera, con orden y colores verificados explícitamente.
    """
    header_match = re.search(r'<text class="ln l0"[^>]*>(.*?)</text>', svg, re.DOTALL)
    assert header_match, 'no se encontró <text class="ln l0"> en el SVG'

    tspans = re.findall(r'<tspan fill="([^"]+)">([^<]*)</tspan>', header_match.group(1))
    assert len(tspans) == 3, (
        f"se esperaban 3 <tspan> (usuario, @, handle) en la cabecera, "
        f"se encontraron {len(tspans)}: la cabecera no puede fusionarse en "
        f"un solo color"
    )

    user = PROFILE["identity"]["name"].split()[0].lower()
    handle = PROFILE["identity"]["handle"]

    (fill_user, text_user), (fill_at, text_at), (fill_handle, text_handle) = tspans

    assert text_user == theme.esc(user)
    assert text_at == "@"
    assert text_handle == theme.esc(handle)

    assert len({fill_user, fill_at, fill_handle}) == 3, (
        "usuario, @ y handle deben llevar tres colores (fill) distintos"
    )


def test_headline_is_bilingual(svg):
    assert theme.esc(PROFILE["headline"]["en"]) in svg
    assert theme.esc(PROFILE["headline"]["es"]) in svg


def test_has_nine_colour_swatches(svg):
    assert svg.count('class="sw"') == 9


def test_is_half_width(svg):
    assert f'width="{theme.WIDTH_HALF}"' in svg


def test_carries_reduced_motion_guard(svg):
    assert "prefers-reduced-motion" in svg


def test_has_no_script(svg):
    assert "<script" not in svg
