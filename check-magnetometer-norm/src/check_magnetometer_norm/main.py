import numpy as np
import pandas as pd
import roboto

from .logger import logger


def main(context: roboto.InvocationContext) -> None:
    logger.setLevel(context.log_level)

    for file, _ in context.get_input().files:
        if file.ingestion_status == roboto.IngestionStatus.NotIngested:
            raise ValueError(
                "This action can only be run on files that have been ingested. "
                f"Make certain 'ulog_ingestion' has run to completion on {file.relative_path} in dataset {file.dataset_id}."
            )

        topic = file.get_topic("sensor_mag")
        mag_df = topic.get_data_as_df(["x", "y", "z"])

        mag_norm: np.typing.NDArray = np.linalg.norm(
            mag_df[["x", "y", "z"]].values, axis=1
        )

        if mag_norm.std() > 0.05 * mag_norm.mean():
            tags = ["mag_unstable", "needs_review"]
            if context.is_dry_run:
                logger.info(
                    "DRY RUN: would put tags %r on file %s", tags, file.relative_path
                )
            else:
                logger.info("Putting tags %r on file %s", tags, file.relative_path)
                file.put_tags(tags)

        mag_norm_spikes = identify_mag_norm_spikes(mag_norm, mag_df.index.tolist())

        for start_time, end_time in mag_norm_spikes:
            event_name = "mag_unstable"
            if context.is_dry_run:
                logger.info(
                    "DRY RUN: would create event '%s' from %d to %d on topic '%s' (%s)",
                    event_name,
                    start_time,
                    end_time,
                    topic.topic_name,
                    topic.topic_id,
                )
            else:
                logger.info(
                    "Creating event '%s' from %d to %d on topic '%s' (%s)",
                    event_name,
                    start_time,
                    end_time,
                    topic.topic_name,
                    topic.topic_id,
                )
                roboto.Event.create(
                    start_time=start_time,
                    end_time=end_time,
                    name=event_name,
                    description="Magnetometer norm spike",
                    topic_ids=[topic.topic_id],
                    display_options=roboto.EventDisplayOptions(color="red"),
                    caller_org_id=context.org_id,
                )


def identify_mag_norm_spikes(
    mag_norm: np.typing.NDArray,
    timestamps: list[int],
    window_size: int = 50,
    threshold_ratio: float = 0.05,
):
    """
    Identify intervals where rolling std of magnetometer norm exceeds a threshold.
    """
    mag_norm_series = pd.Series(mag_norm)
    mean = mag_norm_series.rolling(window=window_size, min_periods=1).mean()
    std = mag_norm_series.rolling(window=window_size, min_periods=1).std()

    mask = std > (threshold_ratio * mean)

    segments = []
    start = None

    for i, flag in enumerate(mask):
        if flag and start is None:
            start = timestamps[i]
        elif not flag and start is not None:
            segments.append((start, timestamps[i]))
            start = None

    if start is not None:
        segments.append((start, timestamps[-1]))

    return segments
