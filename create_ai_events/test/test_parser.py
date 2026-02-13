"""Tests for the AI event parser and validator."""

import json

import pytest
from pydantic import ValidationError

from create_ai_events.parser import (
    AIResponse,
    EventData,
    extract_json,
    parse_ai_response_dict,
)


def test_valid_event_data():
    """Test that valid event data is parsed correctly."""
    data = {
        "start": 1000000000,
        "end": 2000000000,
        "name": "Test Event",
        "description": "This is a test description of what happened.",
        "severity": 3,
        "message_path_ids": ["mp_topic_one", "mp_topic_two"],
    }

    event = EventData.model_validate(data)

    assert event.start == 1000000000
    assert event.end == 2000000000
    assert event.name == "Test Event"
    assert event.severity == 3
    assert len(event.message_path_ids) == 2
    assert event.duration_ns() == 1000000000
    assert event.duration_seconds() == 1.0


def test_event_negative_timestamp():
    """Test that negative timestamps are rejected."""
    data = {
        "start": -1000000000,
        "end": 2000000000,
        "name": "Test",
        "description": "Test description",
        "severity": 1,
        "message_path_ids": ["mp_topic"],
    }

    with pytest.raises(ValidationError) as exc_info:
        EventData.model_validate(data)

    assert "Timestamp must be non-negative" in str(exc_info.value)


def test_event_end_before_start():
    """Test that end timestamp before start is rejected."""
    data = {
        "start": 2000000000,
        "end": 1000000000,
        "name": "Test",
        "description": "Test description",
        "severity": 1,
        "message_path_ids": ["mp_topic"],
    }

    with pytest.raises(ValidationError) as exc_info:
        EventData.model_validate(data)

    assert "must be > start timestamp" in str(exc_info.value)


def test_event_invalid_severity():
    """Test that severity outside 1-5 range is rejected."""
    data = {
        "start": 1000000000,
        "end": 2000000000,
        "name": "Test",
        "description": "Test description",
        "severity": 6,
        "message_path_ids": ["mp_topic"],
    }

    with pytest.raises(ValidationError) as exc_info:
        EventData.model_validate(data)

    assert "less than or equal to 5" in str(exc_info.value)


def test_event_empty_message_path_ids():
    """Test that empty message_path_ids list is rejected."""
    data = {
        "start": 1000000000,
        "end": 2000000000,
        "name": "Test",
        "description": "Test description",
        "severity": 1,
        "message_path_ids": [],
    }

    with pytest.raises(ValidationError):
        EventData.model_validate(data)


def test_valid_ai_response():
    """Test that a valid AI response is parsed correctly."""
    data = {
        "dataset_id": "ds_test123",
        "data": [
            {
                "start": 1000000000,
                "end": 2000000000,
                "name": "First Event",
                "description": "First test description.",
                "severity": 2,
                "message_path_ids": ["mp_topic_one"],
            },
            {
                "start": 3000000000,
                "end": 5000000000,
                "name": "Second Event",
                "description": "Second test description.",
                "severity": 4,
                "message_path_ids": ["mp_topic_two", "mp_topic_three"],
            },
        ]
    }

    response = AIResponse.model_validate(data)

    assert len(response.data) == 2
    assert response.data[0].name == "First Event"
    assert response.data[1].name == "Second Event"


def test_ai_response_empty_data():
    """Test that empty data list is allowed."""
    data = {"dataset_id": "ds_test123", "data": []}

    response = AIResponse.model_validate(data)

    assert len(response.data) == 0


def test_ai_response_event_too_short():
    """Test that events with near-zero duration are rejected."""
    data = {
        "dataset_id": "ds_test123",
        "data": [
            {
                "start": 1000000000,
                "end": 1000000100,  # 0.0000001 seconds (100 nanoseconds)
                "name": "Too Short",
                "description": "This event is too short.",
                "severity": 1,
                "message_path_ids": ["mp_topic"],
            }
        ]
    }

    with pytest.raises(ValidationError) as exc_info:
        AIResponse.model_validate(data)

    assert "near-zero duration" in str(exc_info.value)


def test_ai_response_event_too_long():
    """Test that events with extremely long duration are rejected."""
    data = {
        "dataset_id": "ds_test123",
        "data": [
            {
                "start": 1000000000,
                "end": 2000000000000,  # 1999 seconds - extremely long
                "name": "Too Long",
                "description": "This event is too long.",
                "severity": 1,
                "message_path_ids": ["mp_topic"],
            }
        ]
    }

    with pytest.raises(ValidationError) as exc_info:
        AIResponse.model_validate(data)

    assert "suspiciously long duration" in str(exc_info.value)


def test_parse_ai_response_from_json_string():
    """Test parsing from JSON string."""
    json_str = json.dumps({
        "dataset_id": "ds_test123",
        "data": [
            {
                "start": 1000000000,
                "end": 2000000000,
                "name": "Test",
                "description": "Test description.",
                "severity": 1,
                "message_path_ids": ["mp_topic"],
            }
        ]
    })

    response = extract_json(json_str)

    assert len(response.data) == 1
    assert response.data[0].name == "Test"


def test_parse_ai_response_from_dict():
    """Test parsing from dictionary."""
    data = {
        "dataset_id": "ds_test123",
        "data": [
            {
                "start": 1000000000,
                "end": 2000000000,
                "name": "Test",
                "description": "Test description.",
                "severity": 1,
                "message_path_ids": ["mp_topic"],
            }
        ]
    }

    response = parse_ai_response_dict(data)

    assert len(response.data) == 1
    assert response.data[0].name == "Test"


def test_parse_ai_response_invalid_json():
    """Test that invalid JSON raises appropriate error."""
    with pytest.raises(json.JSONDecodeError):
        extract_json("not valid json")


def test_parse_ai_response_with_markdown_fences():
    """Test parsing JSON wrapped in markdown code fences."""
    json_with_fences = """```json
{
  "dataset_id": "ds_test123",
  "data": [
    {
      "start": 1000000000,
      "end": 2000000000,
      "name": "Test",
      "description": "Test description.",
      "severity": 1,
      "message_path_ids": ["mp_topic"]
    }
  ]
}
```"""

    response = extract_json(json_with_fences)

    assert len(response.data) == 1
    assert response.data[0].name == "Test"


def test_parse_ai_response_with_plain_markdown_fences():
    """Test parsing JSON wrapped in plain markdown fences (no language specifier)."""
    json_with_fences = """```
{
  "dataset_id": "ds_test123",
  "data": [
    {
      "start": 1000000000,
      "end": 2000000000,
      "name": "Test",
      "description": "Test description.",
      "severity": 1,
      "message_path_ids": ["mp_topic"]
    }
  ]
}
```"""

    response = extract_json(json_with_fences)

    assert len(response.data) == 1
    assert response.data[0].name == "Test"


def test_parse_example_fixture():
    """Test parsing the example AI response fixture."""
    import pathlib

    fixture_path = pathlib.Path(__file__).parent / "fixtures" / "example_ai_response.json"

    with open(fixture_path, "r") as f:
        json_str = f.read()

    response = extract_json(json_str)

    assert len(response.data) == 2
    assert response.data[0].name == "Executive Operation Failed"
    assert response.data[0].severity == 4
    assert response.data[0].duration_seconds() == 3.0
    assert len(response.data[0].message_path_ids) == 3

    assert response.data[1].name == "Recovery Attempt Initiated"
    assert response.data[1].severity == 3
    assert response.data[1].duration_seconds() == 5.0


def test_ai_response_accepts_slightly_out_of_range_durations():
    """Test that events slightly outside 1-10s range are accepted (lenient validation)."""
    data = {
        "dataset_id": "ds_test123",
        "data": [
            {
                "start": 1000000000,
                "end": 1500000000,  # 0.5 seconds - less than 1s but should be accepted
                "name": "Slightly Short",
                "description": "This event is slightly short but acceptable.",
                "severity": 1,
                "message_path_ids": ["mp_topic"],
            },
            {
                "start": 2000000000,
                "end": 14000000000,  # 12 seconds - more than 10s but should be accepted
                "name": "Slightly Long",
                "description": "This event is slightly long but acceptable.",
                "severity": 2,
                "message_path_ids": ["mp_topic"],
            },
        ]
    }

    # Should not raise an error
    response = AIResponse.model_validate(data)
    assert len(response.data) == 2


def test_parse_ai_response_with_picosecond_timestamps():
    """Test that timestamps in picoseconds (wrong unit) are auto-corrected."""
    # These timestamps are 1000x too large (picoseconds instead of nanoseconds)
    json_str = json.dumps({
        "dataset_id": "ds_test123",
        "data": [
            {
                "start": 1769641146670000000000,  # 22 digits - picoseconds
                "end": 1769641147050000000000,    # Should be divided by 1000
                "name": "Test with wrong units",
                "description": "This has timestamps in picoseconds instead of nanoseconds.",
                "severity": 3,
                "message_path_ids": ["mp_topic"],
            }
        ]
    })

    response = extract_json(json_str)

    assert len(response.data) == 1
    # After correction, duration should be 0.38 seconds (not 380 seconds)
    assert 0.3 < response.data[0].duration_seconds() < 0.5
    # Verify the timestamps were corrected
    assert response.data[0].start == 1769641146670000000
    assert response.data[0].end == 1769641147050000000

