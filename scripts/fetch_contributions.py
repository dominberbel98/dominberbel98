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
