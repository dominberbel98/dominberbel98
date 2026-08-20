"""Avatar PNG → matriz de tinta normalizada en data/ascii-matrix.json.

Encierra la dependencia de Pillow/numpy: se ejecuta a mano cuando cambia el
avatar y deja un JSON que make_ascii_svg.py consume sin dependencias pesadas.
Por eso el retrato no se regenera en CI.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "avatar-source.png"
OUT = ROOT / "data" / "ascii-matrix.json"

COLS = 64
ROWS = 38


def build_matrix(
    src: Path,
    cols: int = COLS,
    rows: int = ROWS,
    bg_tolerance: float = 52.0,
) -> dict:
    """Devuelve {"cols", "rows", "ink"} con tinta 0..1 y el fondo recortado.

    El fondo del avatar es un azul grisáceo plano, así que basta con una
    máscara por distancia de color a la mediana de las cuatro esquinas.
    No hace falta rembg.
    """
    image = Image.open(src).convert("RGB")
    pixels = np.asarray(image, dtype=np.float64)
    height, width, _ = pixels.shape

    corners = np.array([
        pixels[0, 0], pixels[0, width - 1],
        pixels[height - 1, 0], pixels[height - 1, width - 1],
    ])
    bg = np.median(corners, axis=0)

    distance = np.linalg.norm(pixels - bg, axis=2)
    is_bg = distance <= bg_tolerance

    # Luminancia perceptual; tinta = oscuridad.
    luminance = pixels @ np.array([0.2126, 0.7152, 0.0722])
    ink = 1.0 - luminance / 255.0
    ink[is_bg] = 0.0

    # Promedia cada celda de la rejilla. La celda es más alta que ancha
    # porque el carácter monoespaciado también lo es.
    grid = np.zeros((rows, cols), dtype=np.float64)
    y_edges = np.linspace(0, height, rows + 1).astype(int)
    x_edges = np.linspace(0, width, cols + 1).astype(int)
    for r in range(rows):
        for c in range(cols):
            cell = ink[y_edges[r]:y_edges[r + 1], x_edges[c]:x_edges[c + 1]]
            grid[r, c] = float(cell.mean()) if cell.size else 0.0

    # Estira el contraste sobre las celdas con tinta, dejando el fondo en 0.
    lit = grid[grid > 0.0]
    if lit.size:
        low, high = float(lit.min()), float(lit.max())
        if high > low:
            stretched = (grid - low) / (high - low)
            grid = np.where(grid > 0.0, np.clip(stretched, 0.0, 1.0), 0.0)

    return {"cols": cols, "rows": rows, "ink": grid.round(4).tolist()}


def main() -> None:
    matrix = build_matrix(SRC)
    OUT.write_text(json.dumps(matrix), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)} ({matrix['cols']}x{matrix['rows']})")


if __name__ == "__main__":
    main()
