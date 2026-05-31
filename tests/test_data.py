"""Tests unitaires pour le preprocessing"""
from src.data.preprocessing import (
    clean_html,
    parse_json_string,
    extract_label_fr,
    select_fields,
    is_valid,
    deduplicate,
    transform,
    process,
    FIELDS_TO_KEEP,
)


# --- Tests clean_html ---

def test_clean_html_removes_tags():
    assert clean_html("<p>Bonjour</p>") == "Bonjour"


def test_clean_html_normalizes_whitespace():
    assert clean_html("<p>Bonjour</p>\n<p>monde</p>") == "Bonjour monde"


def test_clean_html_handles_none():
    assert clean_html(None) is None


def test_clean_html_handles_empty():
    assert clean_html("") == ""


# --- Tests parse_json_string ---

def test_parse_json_string_valid():
    raw = '{"id": 1, "label": {"fr": "Programme"}}'
    assert parse_json_string(raw) == {"id": 1, "label": {"fr": "Programme"}}


def test_parse_json_string_invalid():
    assert parse_json_string("not json") is None


def test_parse_json_string_already_dict():
    d = {"a": 1}
    assert parse_json_string(d) == d


# --- Tests extract_label_fr ---

def test_extract_label_fr():
    parsed = {"id": 1, "label": {"fr": "Programme", "en": "Scheduled"}}
    assert extract_label_fr(parsed) == "Programme"


def test_extract_label_fr_missing():
    assert extract_label_fr(None) is None
    assert extract_label_fr({}) is None


# --- Tests select_fields ---

def test_select_fields_keeps_only_expected():
    event = {f: f"value_{f}" for f in FIELDS_TO_KEEP}
    event["extra_field"] = "noise"
    result = select_fields(event)
    assert set(result.keys()) == set(FIELDS_TO_KEEP)
    assert "extra_field" not in result


# --- Tests is_valid ---

def test_is_valid_complete_event():
    event = {
        "title_fr": "Concert",
        "description_fr": "Un super concert",
        "firstdate_begin": "2025-06-01T20:00:00+00:00",
    }
    assert is_valid(event) is True


def test_is_valid_missing_title():
    event = {
        "title_fr": None,
        "description_fr": "Une description",
        "firstdate_begin": "2025-06-01T20:00:00+00:00",
    }
    assert is_valid(event) is False


def test_is_valid_accepts_longdescription_only():
    event = {
        "title_fr": "Concert",
        "description_fr": None,
        "longdescription_fr": "Une description longue",
        "firstdate_begin": "2025-06-01T20:00:00+00:00",
    }
    assert is_valid(event) is True


def test_is_valid_missing_date():
    event = {
        "title_fr": "Concert",
        "description_fr": "Une description",
        "firstdate_begin": None,
    }
    assert is_valid(event) is False


# --- Tests deduplicate ---

def test_deduplicate_removes_duplicates():
    events = [
        {"uid": "1", "title_fr": "A"},
        {"uid": "2", "title_fr": "B"},
        {"uid": "1", "title_fr": "A bis"},
    ]
    result = deduplicate(events)
    assert len(result) == 2
    assert result[0]["uid"] == "1"
    assert result[1]["uid"] == "2"


# --- Test bout en bout ---

def test_process_pipeline():
    raw = [
        {
            "uid": "1",
            "title_fr": "Concert jazz",
            "description_fr": "<p>Super soiree</p>",
            "longdescription_fr": "<p>Description longue</p>",
            "firstdate_begin": "2025-06-01T20:00:00+00:00",
            "status": '{"id": 1, "label": {"fr": "Programme"}}',
            "attendancemode": '{"id": 1, "label": {"fr": "Sur place"}}',
        },
        {
            "uid": "2",
            "title_fr": None,  # invalide
            "description_fr": "Description",
            "firstdate_begin": "2025-06-01T20:00:00+00:00",
        },
        {
            "uid": "1",  # doublon
            "title_fr": "Concert jazz",
            "description_fr": "Doublon",
            "firstdate_begin": "2025-06-01T20:00:00+00:00",
        },
    ]
    result = process(raw)
    assert len(result) == 1
    assert result[0]["uid"] == "1"
    assert result[0]["description_fr"] == "Super soiree"
    assert result[0]["status_label"] == "Programme"
    assert result[0]["attendancemode_label"] == "Sur place"
    assert "status" not in result[0]
    assert "attendancemode" not in result[0]