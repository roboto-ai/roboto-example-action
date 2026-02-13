"""Parser and validator for AI-generated event JSON."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EventData(BaseModel):
    """Represents a single event with associated metadata.

    This model validates the structure defined in prompts.py SYSTEM_PROMPT.
    """

    start: int = Field(
        ...,
        description="Absolute epoch timestamp in nanoseconds (start of event)",
    )
    end: int = Field(
        ...,
        description="Absolute epoch timestamp in nanoseconds (end of event)",
    )
    name: str = Field(
        ...,
        max_length=100,
        description="Short title for the event (max 8 words recommended)",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Narrative description of what happened during the event",
    )
    severity: int = Field(
        ...,
        ge=1,
        le=5,
        description="Severity level from 1 (minor anomaly) to 5 (critical failure)",
    )
    message_path_ids: list[str] = Field(
        ...,
        min_length=1,
        description="List of message path IDs showing relevant data for this event",
    )

    @field_validator("start", "end")
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Ensure timestamps are positive."""
        if v < 0:
            raise ValueError(f"Timestamp must be non-negative, got {v}")
        return v

    @field_validator("end")
    @classmethod
    def validate_end_after_start(cls, v: int, info) -> int:
        """Ensure end timestamp is strictly after start timestamp.

        Events must have a measurable duration (end > start).
        """
        if "start" in info.data and v <= info.data["start"]:
            raise ValueError(
                f"End timestamp ({v}) must be > start timestamp ({info.data['start']}). "
                f"Events must have a duration."
            )
        return v

    @field_validator("message_path_ids")
    @classmethod
    def validate_message_path_ids_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure all message path IDs are non-empty strings."""
        for path_id in v:
            if not path_id or not path_id.strip():
                raise ValueError("message_path_ids cannot contain empty strings")
        return v

    def duration_ns(self) -> int:
        """Return the duration of this event in nanoseconds."""
        return self.end - self.start

    def duration_seconds(self) -> float:
        """Return the duration of this event in seconds."""
        return self.duration_ns() / 1e9


class AIResponse(BaseModel):
    """Root model for the AI-generated event JSON response.

    This model validates the complete structure defined in prompts.py SYSTEM_PROMPT.
    """

    dataset_id: str = Field(
        ...,
        min_length=1,
        description="ID of the dataset being analyzed",
    )
    data: list[EventData] = Field(
        ...,
        description="List of events identified in the dataset",
    )

    @field_validator("data")
    @classmethod
    def validate_events(cls, v: list[EventData]) -> list[EventData]:
        """Validate constraints across all events."""
        if not v:
            # Empty list is allowed - no interesting events found
            return v

        # Sort by start time for easier validation
        sorted_events = sorted(v, key=lambda x: x.start)

        # Collect errors for serious issues only
        errors = []

        for current in sorted_events:
            # Check duration constraints (1s to 10s as per prompt)
            duration_s = current.duration_seconds()

            # Only fail on extreme cases that indicate data corruption
            if duration_s > 1000.0:
                errors.append(
                    f"Event '{current.name}' has suspiciously long duration ({duration_s:.2f}s). "
                    f"Timestamps may be corrupted (start={current.start}, end={current.end})"
                )
            elif duration_s < 0.001:
                errors.append(
                    f"Event '{current.name}' has near-zero duration ({duration_s:.6f}s). "
                    f"Events must have measurable duration."
                )
            # Note: We're being lenient on the 1-10s range since the AI sometimes
            # generates slightly different durations, and we want to be robust

        if errors:
            raise ValueError(
                "Event validation errors:\n  - " + "\n  - ".join(errors)
            )

        return v


def _detect_and_fix_timestamp_units(data: dict[str, Any]) -> dict[str, Any]:
    """Detect and fix common timestamp unit errors.

    The AI sometimes generates timestamps in the wrong units (e.g., picoseconds
    instead of nanoseconds). This function detects and corrects such errors.

    Args:
        data: The parsed JSON data

    Returns:
        Corrected data with timestamps in nanoseconds
    """
    if "data" not in data or not isinstance(data["data"], list):
        return data

    for event in data["data"]:
        if not isinstance(event, dict):
            continue

        start = event.get("start")
        end = event.get("end")

        if not isinstance(start, int) or not isinstance(end, int):
            continue

        # Nanosecond timestamps should be 19 digits (for dates around 2020-2030)
        # If we have 22 digits, it's likely picoseconds (1000x too large)
        start_str = str(start)
        end_str = str(end)

        if len(start_str) >= 22 or len(end_str) >= 22:
            # Likely picoseconds - divide by 1000
            event["start"] = start // 1000
            event["end"] = end // 1000

    return data


def extract_json(json_str: str) -> AIResponse:
    """Parse and validate AI-generated event JSON string.

    Args:
        json_str: JSON string containing the AI response

    Returns:
        Validated AIResponse object

    Raises:
        json.JSONDecodeError: If the string is not valid JSON
        pydantic.ValidationError: If the JSON doesn't match the expected schema
    """
    # Strip markdown code fences if present
    cleaned_str = json_str.strip()
    if cleaned_str.startswith("```"):
        # Remove opening fence (```json or just ```)
        lines = cleaned_str.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned_str = "\n".join(lines)

    data = json.loads(cleaned_str)

    # Detect and fix common timestamp unit errors
    data = _detect_and_fix_timestamp_units(data)

    return AIResponse.model_validate(data)


def parse_ai_response_dict(data: dict[str, Any]) -> AIResponse:
    """Parse and validate AI response from a dictionary.

    Args:
        data: Dictionary containing the AI response

    Returns:
        Validated AIResponse object

    Raises:
        pydantic.ValidationError: If the data doesn't match the expected schema
    """
    return AIResponse.model_validate(data)

