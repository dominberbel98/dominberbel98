import re

from scripts import theme

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_palette_tokens_are_six_digit_hex():
    for name, value in theme.PALETTE.items():
        assert HEX.match(value), f"{name} no es hex de 6 dígitos: {value}"


def test_heat_levels_has_six_entries_all_hex():
    assert len(theme.HEAT_LEVELS) == 6
    for color in theme.HEAT_LEVELS:
        assert HEX.match(color), f"nivel de heatmap inválido: {color}"


def test_mono_stack_ends_in_generic_family():
    assert theme.MONO.strip().endswith("monospace")


def test_style_injects_reduced_motion_guard():
    out = theme.style(".x{opacity:1}")
    assert "prefers-reduced-motion" in out
    assert "animation:none!important" in out


def test_esc_escapes_markup():
    assert theme.esc('<a href="x">&') == "&lt;a href=&quot;x&quot;&gt;&amp;"


def test_svg_open_declares_viewbox_and_title():
    out = theme.svg_open(840, 200, "Prueba")
    assert 'viewBox="0 0 840 200"' in out
    assert "<title" in out
    assert 'role="img"' in out


def test_canonical_widths():
    assert theme.WIDTH_FULL == 840
    assert theme.WIDTH_HALF == 420
    assert theme.WIDTH_HALF * 2 == theme.WIDTH_FULL
