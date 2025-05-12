import os

from roboto import ActionRuntime, Event

import numpy as np
import cv2

from check_camera_blur.utils import create_blur_events_from_dict

runtime = ActionRuntime.from_env()
inputs = runtime.get_input()

BLUR_THRESHOLD: int = int(os.getenv("ROBOTO_PARAM_BLUR_THRESHOLD", 20))

blur_info = {}

def convert_image_msg_to_cv2(msg):
    return cv2.imdecode(np.frombuffer(msg["data"], np.uint8), cv2.IMREAD_COLOR)

def is_blurry(img, threshold=20.0):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

for file, path in inputs.files:

    topic = file.get_topic("/camera")
    topic_data = topic.get_data()
    
    for i, image_msg in enumerate(topic_data):
        img = convert_image_msg_to_cv2(image_msg)
        timestamp = image_msg["log_time"]
        blur_info[timestamp] = is_blurry(img, threshold=BLUR_THRESHOLD)

    if any(blur_info.values()):
        file.put_tags(["camera_blur", "needs_review"])

    event_tuples = create_blur_events_from_dict(blur_info, runtime.org_id, topic)

    for start_time, end_time in event_tuples:
        Event.create(
            start_time=start_time,
            end_time=end_time,
            name="Blurry Segment",
            description="Continuous blurry image segment detected.",
            topic_ids=[topic.topic_id],
            caller_org_id=runtime.org_id)
