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
# Variante estrecha para móvil. En un teléfono el README mide ~330 px: un SVG
# de 840 se reduce al 40 % y un texto de 12 px queda en 5 px. Las piezas "-m"
# se dibujan sobre 420 con cuerpo >= 13, así que en pantalla nunca bajan de
# ~10 px. El README elige una u otra con <picture> + media query.
WIDTH_MOBILE = 420
MIN_MOBILE_FONT = 13


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
        '<linearGradient id="beamg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{GREEN_BRIGHT}" stop-opacity="0"/>'
        f'<stop offset=".85" stop-color="{GREEN_BRIGHT}" stop-opacity=".09"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity=".22"/>'
        "</linearGradient>"
        '<linearGradient id="shineg" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".75"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        "</linearGradient>"
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


# ── Movimiento ambiente ────────────────────────────────────────────────────
# Las entradas de una sola vez se pierden: el SVG arranca al cargar la página
# y, cuando el visitante hace scroll hasta la pieza, ya han terminado. Por eso
# cada panel lleva además un bucle discreto que sigue vivo al llegar a él.

BEAM_H = 70


def beam_css(height: int, *, seconds: float = 7, delay: float = 0) -> str:
    """Haz de barrido de tubo CRT que recorre el panel de arriba abajo."""
    return (
        f"@keyframes beam{{from{{transform:translateY(-{BEAM_H}px)}}"
        f"to{{transform:translateY({height}px)}}}}"
        f".beam{{animation:beam {seconds}s linear {delay}s infinite}}"
    )


def beam(width: int) -> str:
    return (
        f'<rect class="beam" y="-{BEAM_H}" width="{width}" height="{BEAM_H}" '
        f'fill="url(#beamg)" pointer-events="none"/>'
    )


LED_CSS = (
    "@keyframes led{0%,100%{opacity:1}50%{opacity:.25}}"
    ".led{animation:led 1.8s ease-in-out infinite}"
)


def led(cx: float, cy: float, *, r: float = 4, fill: str = GREEN_BRIGHT,
        delay_ms: int = 0) -> str:
    """Piloto de estado que late."""
    return (
        f'<circle class="led" cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
        f'style="animation-delay:{delay_ms}ms"/>'
    )


def wrap(content: str, max_chars: int) -> list[str]:
    """Parte un texto en líneas de como mucho `max_chars` caracteres."""
    import textwrap

    return textwrap.wrap(content, max_chars, break_long_words=False) or [""]


def max_chars(width_px: float, size: float) -> int:
    """Caracteres que caben en `width_px` con la monoespaciada más ancha de la
    pila (0,62 em de avance; Menlo y DejaVu rondan 0,60)."""
    return int(width_px / (size * 0.62))
