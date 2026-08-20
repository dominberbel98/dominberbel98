import json
from pathlib import Path

import pytest

from scripts import theme
from scripts.make_header import render

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
