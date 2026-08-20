"""profile.json → assets/info-card.svg. Panel estilo neofetch."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import theme

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "info-card.svg"

SIZE = theme.WIDTH_HALF   # 420
PAD = 16
FIRST_ENTRY_Y = 68
ENTRY_H = 26
LABEL_X = PAD
VALUE_X = 104
STAGGER_MS = 80

SWATCHES = [
    theme.GREEN_DEEP, theme.GREEN_DIM, theme.GREEN, theme.GREEN_BRIGHT,
    theme.AMBER, theme.CYAN, theme.MUTED, theme.OUTLINE, theme.FG,
]


def render(profile: dict) -> str:
    identity = profile["identity"]
    entries = profile["info_card"]
    handle = identity["handle"]
    user = identity["name"].split()[0].lower()

    lines: list[str] = []
    parts: list[str] = []

    parts.append(
        f'<text class="ln l0" x="{PAD}" y="30" fill="{theme.GREEN_BRIGHT}" '
        f'font-family="{theme.MONO}" font-size="13">'
        f'{theme.esc(user)}@{theme.esc(handle)}</text>'
    )
    parts.append(
        f'<rect class="ln l1" x="{PAD}" y="40" width="{SIZE - 2 * PAD}" height="1" '
        f'fill="{theme.OUTLINE}"/>'
    )

    for i, entry in enumerate(entries):
        y = FIRST_ENTRY_Y + i * ENTRY_H
        idx = i + 2
        parts.append(
            f'<text class="ln l{idx}" x="{LABEL_X}" y="{y}" fill="{theme.AMBER}" '
            f'font-family="{theme.MONO}" font-size="12">{theme.esc(entry["label"])}</text>'
        )
        parts.append(
            f'<text class="ln l{idx}" x="{VALUE_X}" y="{y}" fill="{theme.GREEN}" '
            f'font-family="{theme.MONO}" font-size="12">{theme.esc(entry["value"])}</text>'
        )

    head_idx = len(entries) + 2
    parts.append(
        f'<text class="ln l{head_idx}" x="{PAD}" y="316" fill="{theme.GREEN}" '
        f'font-family="{theme.MONO}" font-size="10">'
        f'{theme.esc(profile["headline"]["en"])}</text>'
    )
    parts.append(
        f'<text class="ln l{head_idx + 1}" x="{PAD}" y="333" fill="{theme.MUTED}" '
        f'font-family="{theme.MONO}" font-size="10">'
        f'{theme.esc(profile["headline"]["es"])}</text>'
    )

    parts.append(f'<g class="ln l{head_idx + 2}">')
    for i, colour in enumerate(SWATCHES):
        parts.append(
            f'<rect class="sw" x="{PAD + i * 24}" y="352" '
            f'width="18" height="18" fill="{colour}"/>'
        )
    parts.append("</g>")

    total_lines = head_idx + 3
    css = "".join([
        "@keyframes enter{from{opacity:0;transform:translateX(-8px)}"
        "to{opacity:1;transform:translateX(0)}}",
        ".ln{animation:enter 420ms cubic-bezier(.2,.8,.2,1) both}",
        *(f".l{i}{{animation-delay:{i * STAGGER_MS}ms}}" for i in range(total_lines)),
        theme.FLICKER_CSS,
    ])

    return "".join([
        theme.svg_open(SIZE, SIZE, f"Ficha de perfil de {identity['name']}"),
        theme.defs(),
        theme.style(css),
        theme.background(SIZE, SIZE),
        f'<g class="flick" filter="url(#bloom)">{"".join(parts)}</g>',
        theme.scanlines(SIZE, SIZE),
        theme.svg_close(),
    ])


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    OUT.write_text(render(profile), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
