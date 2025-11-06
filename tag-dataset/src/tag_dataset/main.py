import roboto

from .logger import logger


def main(context: roboto.InvocationContext) -> None:
    logger.setLevel(context.log_level)

    # 1: Look up the keyword to search for in the logs from the action's runtime parameters.
    # Default to "ERROR" if the `"keyword"` parameter is not provided.
    keyword = context.get_optional_parameter("keyword", "ERROR")

    # 2: Iterate over log files provided to the action at runtime.
    for _, log_path in context.get_input().files:
        if not log_path:
            raise ValueError(
                "Expected 'log_path' to be a pathlib.Path. "
                "If 'requires_downloaded_inputs' is assigned a value in 'action.json', "
                "it should be 'true' for this example."
            )

        # 3: A `pathlib.Path` pointer to the log file downloaded into the action's runtime workspace is provided by Roboto.
        with log_path.open("rt", encoding="utf-8") as file_handle:
            for log_line in file_handle:
                if keyword and keyword in log_line:
                    logger.info("Found '%s' in log file.", keyword)

                    # 4: If running the action locally, skip adding tags to a dataset if the `--dry-run` flag is provided.
                    if context.is_dry_run:
                        logger.info("DRY RUN: not modifying dataset tags")
                    else:
                        context.dataset.put_tags([keyword])

                    return

            logger.info("'%s' not found in log file.", keyword)