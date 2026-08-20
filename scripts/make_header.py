"""profile.json → assets/header.svg.

Banner de cabecera con el enlace a la web personal. En el README va envuelto
en un <a>, así que la pieza entera es clicable.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "header.svg"

W = theme.WIDTH_FULL
H = 96
PAD = 16


def render(profile: dict) -> str:
    site = profile["identity"]["site"]
    url = f"https://{site}"
    command = f"open {url}"

    css = "".join([
        "@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}",
        f".type{{animation:type 1.1s steps({len(command) + 2}, end) both}}",
        "@keyframes enter{from{opacity:0;transform:translateX(-6px)}"
        "to{opacity:1;transform:translateX(0)}}",
        ".ln{animation:enter 420ms cubic-bezier(.2,.8,.2,1) both}",
        ".l0{animation-delay:1150ms}.l1{animation-delay:1270ms}",
        theme.CURSOR_CSS,
        theme.FLICKER_CSS,
    ])

    prompt_line = (
        f'<text class="type" x="{PAD}" y="34" font-family="{theme.MONO}" '
        f'font-size="16" xml:space="preserve">'
        f'<tspan fill="{theme.AMBER}">&gt; </tspan>'
        f'<tspan fill="{theme.GREEN}">open </tspan>'
        f'<tspan fill="{theme.CYAN}">{theme.esc(url)}</tspan>'
        "</text>"
    )

    body = "".join([
        prompt_line,
        theme.cursor(PAD + 10 * len(command) + 6, 21, w=9, h=17),
        f'<text class="ln l0" x="{PAD}" y="62" fill="{theme.GREEN}" '
        f'font-family="{theme.MONO}" font-size="13">'
        f'{theme.esc(profile["headline"]["en"])}</text>',
        f'<text class="ln l1" x="{PAD}" y="80" fill="{theme.MUTED}" '
        f'font-family="{theme.MONO}" font-size="13">'
        f'{theme.esc(profile["headline"]["es"])}</text>',
    ])

    return "".join([
        theme.svg_open(W, H, f"Domingo Berbel — {site}"),
        theme.defs(),
        theme.style(css),
        theme.background(W, H),
        f'<rect x="0" y="{H - 1}" width="{W}" height="1" fill="{theme.OUTLINE}"/>',
        f'<g class="flick" filter="url(#bloom)">{body}</g>',
        theme.scanlines(W, H),
        theme.svg_close(),
    ])


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    OUT.write_text(render(profile), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
