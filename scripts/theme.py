"""Paleta, tipografía y helpers de SVG compartidos por los seis generadores.

La paleta sale de portfolio-chatbot/frontend/tailwind.config.js y src/styles.css.
Cambiar un color aquí lo cambia en los seis SVG a la vez.

Convención de animación: el estado FINAL es el valor natural del elemento y la
animación va del estado inicial a él con `animation-fill-mode: both`. Si el
visitante pide movimiento reducido, `style()` anula las animaciones y se ve la
pieza terminada en lugar de un hueco vacío.
"""

from __future__ import annotations

# ── Paleta (portfolio-chatbot) ─────────────────────────────────────────────
BG = "#0e0e0e"            # background / surface
BG_PANEL = "#131313"      # surface-container-low
BG_RAISED = "#1a1919"     # surface-container
GREEN = "#9cff93"         # primary
GREEN_BRIGHT = "#00ff41"  # verde matrix de styles.css
GREEN_DIM = "#00ec3b"     # primary-dim
GREEN_DEEP = "#006f16"    # inverse-primary
AMBER = "#fcaf00"         # secondary
CYAN = "#81ecff"          # tertiary
MUTED = "#adaaaa"         # on-surface-variant
OUTLINE = "#484847"       # outline-variant
FG = "#ffffff"            # on-surface

PALETTE = {
    "BG": BG, "BG_PANEL": BG_PANEL, "BG_RAISED": BG_RAISED,
    "GREEN": GREEN, "GREEN_BRIGHT": GREEN_BRIGHT, "GREEN_DIM": GREEN_DIM,
    "GREEN_DEEP": GREEN_DEEP, "AMBER": AMBER, "CYAN": CYAN,
    "MUTED": MUTED, "OUTLINE": OUTLINE, "FG": FG,
}

# Heatmap: índice 0 = sin actividad, 1..5 = cuantiles crecientes.
# El nivel 0 lleva verde tenue en vez de casi-negro para que la rejilla lea
# como superficie con relieve y no como vacío con puntos.
HEAT_LEVELS = ["#10251a", "#0e4429", "#006d32", "#00b83a", "#00ec3b", "#9cff93"]

# Rampa de brillo a densidad de glifo. Índice 0 = sin tinta.
RAMP = " .`:-=+*cs#%@"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

WIDTH_FULL = 840
WIDTH_HALF = 420


def esc(value: object) -> str:
    """Escapa texto para insertarlo en XML."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_open(width: int, height: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
        f'aria-labelledby="svg-title">'
        f'<title id="svg-title">{esc(title)}</title>'
    )


def svg_close() -> str:
    return "</svg>"


def defs(extra: str = "") -> str:
    """Scanlines a 2 px y filtro bloom, compartidos por todos los SVG."""
    return (
        "<defs>"
        '<pattern id="scan" width="1" height="2" patternUnits="userSpaceOnUse">'
        '<rect width="1" height="1" fill="#000" opacity="0.18"/>'
        "</pattern>"
        '<filter id="bloom" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="1.8" result="blur"/>'
        "<feMerge>"
        '<feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/>'
        "</feMerge>"
        "</filter>"
        f"{extra}"
        "</defs>"
    )


def style(css: str) -> str:
    """Envuelve CSS y añade la guarda de prefers-reduced-motion.

    Nunca escribas un <style> a mano: esta guarda es obligatoria en todos los SVG.
    """
    return (
        "<style>"
        f"{css}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
        "</style>"
    )


def background(width: int, height: int, fill: str = BG) -> str:
    return f'<rect width="{width}" height="{height}" fill="{fill}"/>'


def scanlines(width: int, height: int) -> str:
    return (
        f'<rect width="{width}" height="{height}" fill="url(#scan)" '
        f'pointer-events="none"/>'
    )


def text(
    x: float,
    y: float,
    content: str,
    *,
    fill: str = GREEN,
    size: float = 13,
    weight: int = 400,
    cls: str | None = None,
    extra: str = "",
) -> str:
    class_attr = f' class="{cls}"' if cls else ""
    extra_attr = f" {extra}" if extra else ""
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{MONO}" '
        f'font-size="{size}" font-weight="{weight}"{class_attr}{extra_attr}>'
        f"{esc(content)}</text>"
    )


def prompt(x: float, y: float, command: str, *, size: float = 13) -> str:
    """Prompt falso '> comando', con el chevron en ámbar."""
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}">'
        f'<tspan fill="{AMBER}">&gt;&#160;</tspan>'
        f'<tspan fill="{GREEN}">{esc(command)}</tspan>'
        "</text>"
    )


def cursor(x: float, y: float, *, w: float = 8, h: float = 15, cls: str = "cur") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{GREEN}" class="{cls}"/>'


CURSOR_CSS = (
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
    ".cur{animation:blink 1s step-end infinite}"
)

FLICKER_CSS = (
    "@keyframes flick{0%{opacity:.985}50%{opacity:1}100%{opacity:.99}}"
    ".flick{animation:flick .12s infinite}"
)
