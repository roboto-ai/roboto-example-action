import roboto

from .logger import logger
from .utils import get_tracking_error


def main(context: roboto.InvocationContext) -> None:
    logger.setLevel(context.log_level)

    action_input = context.get_input()

    if action_input.files:
        logger.info("Processing %d input file(s):", len(action_input.files))
        for file, _ in action_input.files:
            logger.info(
                "%sFile: %s (ID: %s)",
                "  ",
                file.relative_path,
                file.file_id,
            )

            # Get the ingested position and setpoint topics
            pos_topic = file.get_topic("vehicle_local_position")
            sp_topic = file.get_topic("vehicle_local_position_setpoint")

            # Get dataframes of both topics
            pos_df = pos_topic.get_data_as_df()
            sp_df = sp_topic.get_data_as_df()

            # Create a derivative dataframe with the position tracking error
            err_df = get_tracking_error(pos_df, sp_df)

            # Add derivative dataframe as a new topic to the file
            err_topic = file.add_topic(
                topic_name="setpoint_tracking_error",
                df=err_df,
            )
            print(f"Created derivative topic: {err_topic.name}")

    else:
        logger.info("No input files provided")
