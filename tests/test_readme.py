# tests/test_readme.py
import re
from pathlib import Path

README = Path("README.md").read_text(encoding="utf-8")


def test_site_link_appears_before_anything_else():
    """El enlace a la web debe ir arriba del todo."""
    position = README.index("https://domingoberbel.com")
    assert position < 200, "el enlace a la web no está al principio"


def test_banner_is_wrapped_in_an_anchor():
    assert re.search(
        r'<a href="https://domingoberbel\.com">\s*<img src="\./assets/header\.svg"',
        README,
    )


def test_site_is_also_a_plain_markdown_link():
    assert "[domingoberbel.com](https://domingoberbel.com)" in README


def test_every_asset_is_referenced():
    for name in [
        "header.svg", "ascii-portrait.svg", "info-card.svg",
        "stack-bars.svg", "projects.svg", "contrib-heatmap.svg",
    ]:
        assert f"./assets/{name}" in README


def test_every_image_has_alt_text():
    for tag in re.findall(r"<img [^>]+>", README):
        assert "alt=" in tag, f"sin alt: {tag}"


def test_uses_no_setext_or_atx_headings():
    """<h1>/<h2> dibujan una línea horizontal que rompe la composición."""
    assert not re.search(r"^#{1,2} ", README, re.MULTILINE)


def test_has_no_inline_style_attributes():
    """GitHub los elimina; si están, es que alguien esperaba que funcionaran."""
    assert "style=" not in README
