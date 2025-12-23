import roboto

from .logger import logger
from .tracking_error import get_tracking_error


def main(context: roboto.InvocationContext) -> None:
    logger.setLevel(context.log_level)

    action_input = context.get_input()

    if not action_input.files:
        logger.info("No input files provided")
        return
        
    logger.info("Processing %d input file(s):", len(action_input.files))
    for file, _ in action_input.files:
        logger.info(
            "File: %s (ID: %s)",
            file.relative_path,
            file.file_id,
        )

        # Get the ingested position and setpoint topics
        position_topic = file.get_topic("vehicle_local_position")
        setpoint_topic = file.get_topic("vehicle_local_position_setpoint")

        # Get dataframes of both topics
        position_df = position_topic.get_data_as_df()
        setpoint_df = setpoint_topic.get_data_as_df()

        # Create a derivative dataframe with the position tracking error
        tracking_error_df = get_tracking_error(position_df, setpoint_df)

        if not context.is_dry_run:
            # Add derivative dataframe as a new topic to the file
            tracking_error_topic = file.add_topic(
                topic_name="setpoint_tracking_error",
                df=tracking_error_df,
                timestamp_column="log_time",
                timestamp_unit="ns"
            )
            logger.info(f"Created derivative topic: {tracking_error_topic.topic_name}")
        else:
            logger.info("Skipping topic creation in dry run mode")

