from PIL import Image

from scripts.prep_photo import build_matrix

BG = (125, 159, 174)  # azul grisáceo plano del avatar


def _synthetic(tmp_path):
    """Mitad izquierda = fondo plano, mitad derecha = negro puro."""
    img = Image.new("RGB", (128, 128), BG)
    for x in range(64, 128):
        for y in range(128):
            img.putpixel((x, y), (0, 0, 0))
    path = tmp_path / "synthetic.png"
    img.save(path)
    return path


def test_matrix_has_requested_dimensions(tmp_path):
    matrix = build_matrix(_synthetic(tmp_path), cols=64, rows=38)
    assert matrix["cols"] == 64
    assert matrix["rows"] == 38
    assert len(matrix["ink"]) == 38
    assert all(len(row) == 64 for row in matrix["ink"])


def test_background_becomes_zero_ink(tmp_path):
    matrix = build_matrix(_synthetic(tmp_path), cols=64, rows=38)
    left = [row[4] for row in matrix["ink"]]
    assert max(left) == 0.0, "el fondo plano debería recortarse a tinta 0"


def test_dark_pixels_become_full_ink(tmp_path):
    matrix = build_matrix(_synthetic(tmp_path), cols=64, rows=38)
    right = [row[60] for row in matrix["ink"]]
    assert min(right) > 0.9, "el negro puro debería ser tinta máxima"


def test_ink_stays_in_unit_range(tmp_path):
    matrix = build_matrix(_synthetic(tmp_path), cols=64, rows=38)
    flat = [v for row in matrix["ink"] for v in row]
    assert all(0.0 <= v <= 1.0 for v in flat)
