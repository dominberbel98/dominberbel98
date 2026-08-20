import json
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


def test_header_is_user_at_handle(svg):
    assert "domingo@dominberbel98" in svg


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
