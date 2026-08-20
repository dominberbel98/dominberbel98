import json
from pathlib import Path

from scripts import theme
from scripts.make_ascii_svg import bucket, glyph, render, row_runs

PROFILE = json.loads(Path("data/profile.json").read_text(encoding="utf-8"))


def test_no_ink_is_a_space():
    assert glyph(0.0) == " "


def test_full_ink_is_the_densest_glyph():
    assert glyph(1.0) == theme.RAMP[-1]


def test_glyph_density_is_monotonic():
    indices = [theme.RAMP.index(glyph(v / 100)) for v in range(101)]
    assert indices == sorted(indices)


def test_bucket_stays_in_range():
    assert bucket(0.0) == 0
    assert bucket(1.0) == 4
    assert all(0 <= bucket(v / 100) <= 4 for v in range(101))


def test_row_runs_collapse_identical_buckets():
    runs = row_runs([0.0] * 10)
    assert len(runs) == 1
    assert runs[0][1] == " " * 10


def test_row_runs_split_on_bucket_change():
    runs = row_runs([0.0, 0.0, 1.0, 1.0])
    assert len(runs) == 2


def test_render_emits_one_text_element_per_row():
    svg = render({"cols": 4, "rows": 3, "ink": [[0.0] * 4 for _ in range(3)]}, PROFILE)
    assert svg.count('class="row') == 3


def test_every_row_forces_its_width():
    svg = render({"cols": 4, "rows": 3, "ink": [[0.5] * 4 for _ in range(3)]}, PROFILE)
    assert svg.count("textLength=") == 3
    assert svg.count('lengthAdjust="spacingAndGlyphs"') == 3
    assert svg.count('xml:space="preserve"') == 3


def test_render_has_no_script():
    svg = render({"cols": 4, "rows": 2, "ink": [[0.3] * 4 for _ in range(2)]}, PROFILE)
    assert "<script" not in svg


def test_render_title_uses_the_profile_name():
    svg = render({"cols": 1, "rows": 1, "ink": [[0.0]]}, PROFILE)
    assert f"Retrato ASCII de {PROFILE['identity']['name']}" in svg
