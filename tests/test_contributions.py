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


def test_current_streak_counts_multiple_active_days_at_the_end():
    days = [
        {"date": "2026-08-01", "count": 0},
        {"date": "2026-08-02", "count": 2},
        {"date": "2026-08-03", "count": 5},
        {"date": "2026-08-04", "count": 1},
    ]
    summary = summarise(days)
    assert summary["current_streak"] == 3


def test_current_streak_of_exactly_one():
    days = [
        {"date": "2026-08-01", "count": 4},
        {"date": "2026-08-02", "count": 0},
        {"date": "2026-08-03", "count": 3},
    ]
    summary = summarise(days)
    assert summary["current_streak"] == 1


def test_current_streak_equals_length_when_every_day_is_active():
    days = [
        {"date": "2026-08-01", "count": 1},
        {"date": "2026-08-02", "count": 2},
        {"date": "2026-08-03", "count": 3},
    ]
    summary = summarise(days)
    assert summary["current_streak"] == len(days)


def test_best_day_ties_pick_the_earliest_date():
    # days llega siempre ordenado cronológicamente (parse_calendar ordena
    # por fecha); max() se queda con el primer máximo que encuentra, así
    # que en un empate gana la fecha más temprana. Fijamos ese
    # comportamiento explícitamente: hoy es determinista pero no estaba
    # protegido por ningún test.
    days = [
        {"date": "2026-08-01", "count": 5},
        {"date": "2026-08-02", "count": 9},
        {"date": "2026-08-03", "count": 9},
        {"date": "2026-08-04", "count": 2},
    ]
    summary = summarise(days)
    assert summary["best_day"] == {"date": "2026-08-02", "count": 9}


def test_summary_of_empty_calendar_does_not_crash():
    summary = summarise([])
    assert summary["total"] == 0
    assert summary["best_day"]["count"] == 0


def test_aborts_when_parsed_calendar_is_incomplete():
    from scripts.fetch_contributions import _check_calendar_is_complete

    html = """
    <table class="ContributionCalendar-grid">
      <tbody>
        <tr>
          <td class="ContributionCalendar-day" data-date="2026-08-19" data-level="1" id="c-1"></td>
          <td class="ContributionCalendar-day" data-date="2026-08-20" data-level="0" id="c-2"></td>
        </tr>
      </tbody>
    </table>
    <tool-tip for="c-1">1 contribution on August 19th.</tool-tip>
    <tool-tip for="c-2">No contributions on August 20th.</tool-tip>
    """
    few_days = parse_calendar(html)
    assert len(few_days) == 2  # muy por debajo de un año de calendario

    with pytest.raises(SystemExit):
        _check_calendar_is_complete(few_days)
