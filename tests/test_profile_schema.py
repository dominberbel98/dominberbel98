import json
import re
from pathlib import Path

import pytest

PROFILE = Path("data/profile.json")
PLACEHOLDERS = re.compile(r"\b(TODO|TBD|FIXME|lorem ipsum|xxx)\b", re.IGNORECASE)


@pytest.fixture(scope="module")
def profile():
    return json.loads(PROFILE.read_text(encoding="utf-8"))


def test_top_level_keys(profile):
    assert set(profile) == {
        "identity", "headline", "info_card", "stack", "projects", "heatmap"
    }


def test_identity_is_complete(profile):
    required = {
        "name", "handle", "role", "company", "since",
        "location", "site", "email", "linkedin",
    }
    assert required <= set(profile["identity"])
    for key, value in profile["identity"].items():
        assert isinstance(value, str) and value.strip(), f"identity.{key} vacío"


def test_headline_is_bilingual(profile):
    assert set(profile["headline"]) == {"en", "es"}
    for lang, line in profile["headline"].items():
        assert line.strip(), f"headline.{lang} vacío"


def test_info_card_entries_are_label_value_pairs(profile):
    assert profile["info_card"], "info_card vacío"
    for entry in profile["info_card"]:
        assert set(entry) == {"label", "value"}
        assert entry["label"].strip() and entry["value"].strip()


def test_stack_levels_are_percentages(profile):
    assert profile["stack"], "stack vacío"
    for item in profile["stack"]:
        assert set(item) == {"label", "level"}
        assert item["label"].strip()
        assert isinstance(item["level"], int)
        assert 0 <= item["level"] <= 100


def test_projects_are_bilingual_with_valid_urls(profile):
    assert profile["projects"], "projects vacío"
    for item in profile["projects"]:
        assert set(item) == {"name", "en", "es", "url"}
        assert item["name"].strip() and item["en"].strip() and item["es"].strip()
        assert item["url"] == "" or item["url"].startswith("https://")


def test_heatmap_window_is_sane(profile):
    weeks = profile["heatmap"]["weeks"]
    assert isinstance(weeks, int) and 1 <= weeks <= 53


def test_no_placeholder_text_anywhere():
    raw = PROFILE.read_text(encoding="utf-8")
    assert not PLACEHOLDERS.search(raw), "quedan placeholders en profile.json"


def test_tfm_says_third_place_not_first(profile):
    """Regresión: cv.md se contradice; profile.yml dice 3ª. Fijamos 3ª."""
    tfm = next(p for p in profile["projects"] if p["name"] == "tfm-ucm-rag")
    assert "3ª" in tfm["es"] and "3rd" in tfm["en"]
    assert "1ª" not in tfm["es"] and "1st" not in tfm["en"]
