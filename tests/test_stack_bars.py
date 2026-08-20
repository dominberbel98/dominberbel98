import json
import re
from pathlib import Path

import pytest

from scripts import theme
from scripts.make_stack_bars import BAR_W, render

PROFILE = json.loads(Path("data/profile.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def svg():
    return render(PROFILE)


def test_shows_every_stack_label(svg):
    for item in PROFILE["stack"]:
        assert theme.esc(item["label"]) in svg


def test_never_prints_the_numeric_level(svg):
    """Una cifra autoevaluada invita a que te la discutan. Solo va la barra."""
    for item in PROFILE["stack"]:
        assert f">{item['level']}%<" not in svg
        assert f">{item['level']}<" not in svg


def test_bar_width_is_proportional_to_level(svg):
    widths = [float(w) for w in re.findall(r'class="bar" x="130" y="[\d.]+" width="([\d.]+)"', svg)]
    expected = [round(BAR_W * item["level"] / 100, 1) for item in PROFILE["stack"]]
    assert widths == expected


def test_scale_animation_sets_fill_box(svg):
    assert "transform-box:fill-box" in svg
    assert "transform-origin:left center" in svg


def test_is_full_width(svg):
    assert f'width="{theme.WIDTH_FULL}"' in svg


def test_carries_reduced_motion_guard(svg):
    assert "prefers-reduced-motion" in svg


def test_has_no_script(svg):
    assert "<script" not in svg
