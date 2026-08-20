# tests/test_contributions.py
from pathlib import Path

import pytest

from scripts.fetch_contributions import parse_calendar, summarise

FIXTURE = Path("tests/fixtures/contributions.html").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def days():
    return parse_calendar(FIXTURE)


def test_parses_every_day(days):
    assert len(days) == 5


def test_reads_counts_from_tooltips(days):
    assert [d["count"] for d in days] == [0, 3, 9, 1, 0]


def test_days_are_sorted_by_date(days):
    assert [d["date"] for d in days] == sorted(d["date"] for d in days)


def test_no_contributions_becomes_zero(days):
    assert days[0]["count"] == 0


def test_falls_back_to_data_count_attribute():
    html = '<td data-date="2026-01-01" data-count="7" id="x"></td>'
    assert parse_calendar(html)[0]["count"] == 7


def test_summary_totals(days):
    summary = summarise(days)
    assert summary["total"] == 13
    assert summary["active_days"] == 3


def test_summary_streaks(days):
    summary = summarise(days)
    assert summary["longest_streak"] == 3
    assert summary["current_streak"] == 0, "el último día está vacío"


def test_summary_best_day(days):
    summary = summarise(days)
    assert summary["best_day"] == {"date": "2026-08-18", "count": 9}


def test_summary_of_empty_calendar_does_not_crash():
    summary = summarise([])
    assert summary["total"] == 0
    assert summary["best_day"]["count"] == 0
