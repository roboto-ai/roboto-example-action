from roboto import ActionRuntime
from roboto.domain import events
from check_magnetometer_norm.utils import find_magnetometer_anomaly_events
import numpy as np

runtime = ActionRuntime.from_env()
inputs = runtime.get_input()

for file, path in runtime.get_input().files:
    topic = file.get_topic("sensor_mag")
    df = topic.get_data_as_df(['x', 'y', 'z'])
    norm = np.linalg.norm(df[['x', 'y', 'z']].values, axis=1)

    if norm.std() > 0.05 * norm.mean():
        file.put_tags(["magnetometer_anomaly", "needs_review"])

    anomaly_events = find_magnetometer_anomaly_events(df)

    for start_time, end_time in anomaly_events:

        events.Event.create(
            start_time=start_time,
            end_time=end_time,
            name="magnetometer_anomaly",
            description="High magnetometer norm variation",
            associations=[topic.to_association()],
            caller_org_id=runtime.org_id,
        )
