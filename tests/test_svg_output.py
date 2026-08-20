import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ASSETS = sorted(Path("assets").glob("*.svg"))
MAX_BYTES = 200 * 1024


def test_all_six_assets_exist():
    assert {p.name for p in ASSETS} == {
        "header.svg", "ascii-portrait.svg", "info-card.svg",
        "stack-bars.svg", "projects.svg", "contrib-heatmap.svg",
    }


@pytest.mark.parametrize("path", ASSETS, ids=lambda p: p.name)
def test_parses_as_xml(path):
    ET.parse(path)


@pytest.mark.parametrize("path", ASSETS, ids=lambda p: p.name)
def test_declares_viewbox_and_title(path):
    root = ET.parse(path).getroot()
    assert root.get("viewBox"), f"{path.name} sin viewBox"
    assert root.get("role") == "img"
    assert root.find("{http://www.w3.org/2000/svg}title") is not None


@pytest.mark.parametrize("path", ASSETS, ids=lambda p: p.name)
def test_contains_no_script(path):
    assert "<script" not in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", ASSETS, ids=lambda p: p.name)
def test_honours_reduced_motion(path):
    assert "prefers-reduced-motion" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", ASSETS, ids=lambda p: p.name)
def test_paints_an_opaque_background(path):
    """El README se ve en tema claro y oscuro; el fondo no puede ser transparente."""
    assert "#0e0e0e" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", ASSETS, ids=lambda p: p.name)
def test_stays_within_weight_budget(path):
    size = path.stat().st_size
    assert size <= MAX_BYTES, f"{path.name} pesa {size / 1024:.1f} KB"


@pytest.mark.parametrize("path", ASSETS, ids=lambda p: p.name)
def test_every_animation_declares_a_fill_mode(path):
    """Sin `both`, una animación con delay deja la pieza invisible hasta que arranca.

    Se comprueba cada declaración `animation:` por separado: un `both` suelto
    en cualquier otra parte del archivo no debe dar el test por bueno.

    La guarda de accesibilidad obligatoria (`animation:none!important` dentro
    de `@media (prefers-reduced-motion: reduce)`) no es una animación sino un
    reset que las anula: se ignora explícitamente y no cuenta como la
    animación real que cada SVG debe declarar.
    """
    import re

    text = path.read_text(encoding="utf-8")
    declarations = re.findall(r"animation:([^;}\"]*)", text)
    assert declarations, f"{path.name} no declara ninguna animación"

    real_declarations = [
        d for d in declarations if re.fullmatch(r"\s*none\s*(!important)?\s*", d) is None
    ]
    assert real_declarations, (
        f"{path.name} solo declara el reset de prefers-reduced-motion, "
        "ninguna animación real"
    )

    for declaration in real_declarations:
        assert "both" in declaration or "infinite" in declaration, (
            f"{path.name}: 'animation:{declaration.strip()}' sin fill-mode"
        )
