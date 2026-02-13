import json
from datetime import datetime, UTC

import roboto
from pydantic import ValidationError
from roboto import Dataset, File
from roboto.domain import actions
from roboto.domain.events import Event

from .ai_chat import ChatInterface
from .logger import logger
from .parser import AIResponse, EventData, extract_json

# Map severity level to display color
SEVERITY_COLORS = {
    1: "#90EE90",  # Light green - minor anomaly
    2: "#FFD700",  # Gold - notable deviation
    3: "#FFA500",  # Orange - recoverable failure
    4: "#FF6347",  # Tomato red - operation failed
    5: "#DC143C",  # Crimson - critical failure
}


def determine_dataset(context: roboto.InvocationContext) -> Dataset | None:
    """Return the dataset to analyze, if it can be inferred from the invocation."""
    if context.dataset_id != actions.InvocationDataSource.unspecified().data_source_id:
        return context.dataset

    files = context.get_input().files
    if not files:
        return None

    first_file, _ = next(iter(files))
    return Dataset.from_id(first_file.dataset_id, roboto_client=context.roboto_client)


def list_files(dataset: Dataset) -> list[File]:
    return list(dataset.list_files())


def create_event(
    event_data: EventData,
    dataset: Dataset,
    context: roboto.InvocationContext,
) -> Event:
    """Create a Roboto Event from parsed AI event data.

    Args:
        event_data: Parsed event data from AI response
        dataset: Dataset to associate the event with
        context: Invocation context for accessing roboto_client

    Returns:
        Created Event instance
    """
    color = SEVERITY_COLORS.get(event_data.severity, "#808080")  # Default to gray

    metadata = {
        "severity": event_data.severity,
        "ai_generated": True,
    }

    tags = [f"severity-{event_data.severity}", "ai-generated", "create-ai-events-action"]

    logger.info(
        "Creating event '%s' (severity %d) from %d to %d with %d message path(s)",
        event_data.name,
        event_data.severity,
        event_data.start,
        event_data.end,
        len(event_data.message_path_ids),
    )

    event = Event.create(
        name=event_data.name,
        start_time=event_data.start,
        end_time=event_data.end,
        description=event_data.description,
        dataset_ids=[dataset.dataset_id],
        message_path_ids=event_data.message_path_ids,
        metadata=metadata,
        tags=tags,
        display_options={"color": color},
        roboto_client=context.roboto_client,
    )

    logger.info("Created event %s: '%s'", event.event_id, event_data.name)

    return event


def create_events_from_response(
    parsed_response: AIResponse,
    dataset: Dataset,
    context: roboto.InvocationContext,
) -> list[Event]:
    """Create Roboto Events from all events in the parsed AI response.

    Args:
        parsed_response: Parsed and validated AI response
        dataset: Dataset to associate events with
        context: Invocation context

    Returns:
        List of created Event instances
    """
    events = []

    for idx, event_data in enumerate(parsed_response.data, 1):
        try:
            event = create_event(event_data, dataset, context)
            events.append(event)
        except Exception as e:
            logger.error(
                "Failed to create event %d/%d ('%s'): %s",
                idx,
                len(parsed_response.data),
                event_data.name,
                e,
            )
            # Continue creating other events even if one fails
            continue

    logger.info(
        "Successfully created %d/%d events",
        len(events),
        len(parsed_response.data),
    )

    return events


def main(context: roboto.InvocationContext) -> None:
    logger.setLevel(context.log_level)

    logger.info(
        "Running event creation in org %s at %s.",
        context.org_id,
        datetime.now(UTC).isoformat(timespec="seconds"),
    )

    dataset = determine_dataset(context)
    if dataset is None:
        logger.warning("Could not determine which dataset to process. Exiting.")
        return

    ds_id = dataset.dataset_id

    # Use explicitly provided input files if available; otherwise discover all files
    input_files = list(context.get_input().files)
    if input_files:
        file_names = [file for file, _ in input_files]
        logger.info("Processing %d specified input file(s) in dataset %s.", len(file_names), ds_id)
    else:
        file_names = list_files(dataset)
        logger.info("No input files specified; found %d file(s) in dataset %s.", len(file_names), ds_id)

    chat = ChatInterface.from_invocation_context(context)

    # Retry logic for AI response generation and parsing
    max_retries = 3
    extracted_event_specs = None
    ai_response = ""

    for attempt in range(1, max_retries + 1):
        logger.info("Generating AI response for dataset %s (attempt %d/%d)...", ds_id, attempt, max_retries)

        try:
            ai_response = chat.prompt_with(dataset, file_names)
            extracted_event_specs = extract_json(ai_response)

            logger.info(
                "Successfully parsed and validated AI response with %d events(s)",
                len(extracted_event_specs.data),
            )

            # Log details about each event_spec
            for idx, event_spec in enumerate(extracted_event_specs.data, 1):
                logger.info(
                    "Event %d: '%s' - duration: %.2fs, severity: %d, message_path_ids: %d",
                    idx,
                    event_spec.name,
                    event_spec.duration_seconds(),
                    event_spec.severity,
                    len(event_spec.message_path_ids),
                )
                logger.debug("  Description: %s", event_spec.description)
                logger.debug("  Message path IDs: %s", ", ".join(event_spec.message_path_ids))

            # Success! Break out of retry loop
            break

        except json.JSONDecodeError as e:
            logger.warning("Attempt %d/%d: AI response is not valid JSON: %s", attempt, max_retries, e)
            if attempt < max_retries:
                logger.info("Retrying...")
            else:
                logger.error("All %d attempts failed. Last AI response: %s", max_retries, ai_response)
                raise ValueError(f"AI response returned invalid JSON after {max_retries} attempts: {e}") from e

        except ValidationError as e:
            logger.warning("Attempt %d/%d: AI response validation failed: %s", attempt, max_retries, e)
            if attempt < max_retries:
                logger.info("Retrying...")
            else:
                logger.error("All %d attempts failed. Last AI response: %s", max_retries, ai_response)
                raise ValueError(f"AI response failed validation after {max_retries} attempts: {e}") from e

    if extracted_event_specs is None:
        raise ValueError(f"Failed to generate valid AI response after {max_retries} attempts")

    if context.is_dry_run:
        logger.info("[dry run] Skipping event creation for dataset %s.", ds_id)
        logger.info(ai_response)
        return

    # Create events from the parsed response
    if extracted_event_specs.data:
        logger.info("Creating events from %d event_spec(s)...", len(extracted_event_specs.data))
        events = create_events_from_response(extracted_event_specs, dataset, context)
        logger.info("Created %d event(s) successfully", len(events))
    else:
        logger.info("No events found in AI response - nothing to create")

