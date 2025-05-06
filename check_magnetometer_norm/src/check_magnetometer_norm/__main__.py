from roboto import ActionRuntime, Event, EventDisplayOptions
from check_magnetometer_norm.utils import identify_mag_norm_spikes
import numpy as np

runtime = ActionRuntime.from_env()
inputs = runtime.get_input()

for file, path in inputs.files:
    topic = file.get_topic("sensor_mag")
    mag_df = topic.get_data_as_df(["x", "y", "z"])
    mag_norm = np.linalg.norm(mag_df[["x", "y", "z"]].values, axis=1)

    if mag_norm.std() > 0.05 * mag_norm.mean():
        file.put_tags(["mag_unstable", "needs_review"])

    mag_norm_spikes = identify_mag_norm_spikes(mag_df)

    for start_time, end_time in mag_norm_spikes:
        
        Event.create(
            start_time=start_time,
            end_time=end_time,
            name="mag_unstable",
            description="Magnetometer norm spike",
            topic_ids=[topic.topic_id],
            display_options=EventDisplayOptions(color="red"),
            caller_org_id=runtime.org_id,
        )
