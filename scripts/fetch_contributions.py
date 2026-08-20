"""Raspa el calendario público de contribuciones → data/contributions.json.

Es el único script que sale a la red, y el único que corre en CI junto al
renderizador del heatmap.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "data" / "contributions.json"

URL = "https://github.com/users/{handle}/contributions"
LEADING_INT = re.compile(r"\s*([\d,]+)")

# El calendario de GitHub cubre siempre en torno a 365 días. Un resultado muy
# por debajo indica que el parseo se ha roto (p. ej. GitHub cambió el markup
# y devolvió un 200 OK con contenido inservible), no que el usuario esté
# inactivo: la inactividad se refleja en `total`/`active_days`, no en cuántos
# días se parsearon. 300 deja margen para variaciones de la ventana sin
# tragarse un parseo roto.
MIN_EXPECTED_DAYS = 300


def parse_calendar(html: str) -> list[dict]:
    """Extrae [{"date", "count"}] del HTML del calendario, ordenado por fecha."""
    soup = BeautifulSoup(html, "html.parser")

    tooltips: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        match = LEADING_INT.match(tip.get_text(strip=True))
        tooltips[target] = int(match.group(1).replace(",", "")) if match else 0

    days: list[dict] = []
    for cell in soup.select("td[data-date]"):
        if cell.has_attr("data-count"):
            count = int(str(cell["data-count"]).replace(",", ""))
        else:
            count = tooltips.get(cell.get("id", ""), 0)
        days.append({"date": cell["data-date"], "count": count})

    days.sort(key=lambda day: day["date"])
    return days


def summarise(days: list[dict]) -> dict:
    """Métricas derivadas. Todas salen de `days`; ninguna se inventa."""
    counts = [day["count"] for day in days]
    total = sum(counts)
    active = sum(1 for c in counts if c > 0)

    longest = running = 0
    for count in counts:
        running = running + 1 if count > 0 else 0
        longest = max(longest, running)

    current = 0
    for count in reversed(counts):
        if count <= 0:
            break
        current += 1

    best = max(days, key=lambda day: day["count"]) if days else None
    best_day = (
        {"date": best["date"], "count": best["count"]}
        if best else {"date": "", "count": 0}
    )

    return {
        "total": total,
        "active_days": active,
        "longest_streak": longest,
        "current_streak": current,
        "best_day": best_day,
        "first_date": days[0]["date"] if days else "",
        "last_date": days[-1]["date"] if days else "",
    }


def _check_calendar_is_complete(days: list[dict]) -> None:
    """Aborta si se han parseado muy pocos días.

    Cubre el caso de fallo parcial silencioso: un 200 OK cuyo contenido ya
    no coincide con el markup que espera `parse_calendar` (GitHub cambió el
    HTML, devolvió una página vacía, etc.) no lanza ninguna excepción de
    red, pero produce una lista de días casi vacía. Sin esta comprobación,
    ese resultado se escribiría igualmente, machacando el último dato bueno.
    """
    if len(days) < MIN_EXPECTED_DAYS:
        raise SystemExit(
            f"fetch_contributions: solo se parsearon {len(days)} días "
            f"(se esperaban al menos {MIN_EXPECTED_DAYS}, de un calendario "
            f"de ~365). El markup de GitHub puede haber cambiado. "
            f"No se ha sobrescrito {OUT.relative_to(ROOT)}."
        )


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    handle = profile["identity"]["handle"]

    response = requests.get(
        URL.format(handle=handle),
        headers={"User-Agent": f"{handle}-profile-art"},
        timeout=30,
    )
    response.raise_for_status()

    days = parse_calendar(response.text)
    _check_calendar_is_complete(days)

    payload = {
        "handle": handle,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "days": days,
        **summarise(days),
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)}: {payload['total']} contribuciones")


if __name__ == "__main__":
    main()
