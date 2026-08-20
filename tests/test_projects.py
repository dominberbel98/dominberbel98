import json
from pathlib import Path

import pytest

from scripts import theme
from scripts.make_projects import render

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
