import json
import re
from pathlib import Path

import pytest

from scripts import theme
from scripts.make_header import PAD, render

PROFILE = json.loads(Path("data/profile.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def svg():
    return render(PROFILE)


def test_header_shows_the_site_url(svg):
    assert "domingoberbel.com" in svg


def test_site_url_is_painted_as_a_link(svg):
    assert theme.CYAN in svg, "la URL debe ir en CYAN para leerse como enlace"


def test_header_is_bilingual(svg):
    assert theme.esc(PROFILE["headline"]["en"]) in svg
    assert theme.esc(PROFILE["headline"]["es"]) in svg


def test_header_has_canonical_width(svg):
    assert f'width="{theme.WIDTH_FULL}"' in svg


def test_header_carries_reduced_motion_guard(svg):
    assert "prefers-reduced-motion" in svg


def test_header_has_no_script(svg):
    assert "<script" not in svg


def test_cursor_never_overlaps_the_prompt_text(svg):
    """El ancho del prompt no puede depender de una constante px/carácter:
    la fuente monoespaciada del visitante puede ser más ancha que lo asumido,
    y entonces el cursor cae encima del texto en vez de después de él.

    La técnica correcta (la misma que usa make_ascii_svg.py) es fijar el
    ancho renderizado del <text> con textLength + lengthAdjust, para que sea
    exacto sin importar la fuente instalada, y calcular el cursor a partir de
    ese ancho — nunca con una constante mágica propia.
    """
    text_match = re.search(r'<text class="type"[^>]*>', svg)
    assert text_match, "no se encontró el <text> del prompt"
    text_tag = text_match.group(0)

    length_match = re.search(r'textLength="([\d.]+)"', text_tag)
    assert length_match, (
        "el <text> del prompt debe fijar textLength para que su ancho "
        "renderizado sea determinista"
    )
    assert 'lengthAdjust="spacingAndGlyphs"' in text_tag, (
        "textLength sin lengthAdjust=\"spacingAndGlyphs\" no fuerza el ancho "
        "real de los glifos"
    )

    text_length = float(length_match.group(1))

    cursor_match = re.search(r'<rect x="([\d.]+)"[^>]*class="cur"', svg)
    assert cursor_match, "no se encontró el cursor del prompt"
    cursor_x = float(cursor_match.group(1))

    assert cursor_x >= PAD + text_length, (
        "el cursor debe posicionarse en PAD + textLength (o más allá), "
        "nunca con una constante de px por carácter"
    )
