import roboto
import whenever
from roboto import Dataset, File
from roboto.domain import actions

from .ai_summarizer import CustomDatasetSummarizer
from .logger import logger

MCAP_GLOB = "**/*.mcap"


def determine_dataset(context: roboto.InvocationContext) -> Dataset | None:
    """Return the dataset to summarize, if it can be inferred from the invocation."""
    if context.dataset_id != actions.InvocationDataSource.unspecified().data_source_id:
        return context.dataset

    files = context.get_input().files
    if not files:
        return None

    first_file, _ = next(iter(files))
    return Dataset.from_id(first_file.dataset_id, roboto_client=context.roboto_client)


def list_mcap_files(dataset: Dataset) -> list[File]:
    return list(dataset.list_files(include_patterns=[MCAP_GLOB]))


def main(context: roboto.InvocationContext) -> None:
    logger.setLevel(context.log_level)

    logger.info(
        "Running dataset summarization in org %s at %s.",
        context.org_id,
        whenever.Instant.now().format_iso(unit="second"),
    )

    dataset = determine_dataset(context)
    if dataset is None:
        logger.warning("Could not determine which dataset to summarize. Exiting.")
        return

    ds_id = dataset.dataset_id
    recordings = list_mcap_files(dataset)

    logger.info("Found %d MCAP file(s) in dataset %s.", len(recordings), ds_id)
    logger.info("Generating AI summary for dataset %s...", ds_id)

    summarizer = CustomDatasetSummarizer.from_invocation_context(context)
    ai_summary = summarizer.summarize(dataset, recordings)

    if context.is_dry_run:
        logger.info("[dry run] Skipping setting AI summary on dataset %s.", ds_id)
        logger.info(ai_summary)
        return

    logger.info("Summary generated; persisting to dataset %s.", ds_id)
    dataset.set_summary(ai_summary)