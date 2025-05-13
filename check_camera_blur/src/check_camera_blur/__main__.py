import os
import cv2
from roboto import ActionRuntime, Event
from check_camera_blur.utils import to_cv2_img, get_blur_events

runtime = ActionRuntime.from_env()
inputs = runtime.get_input()

BLUR_THRESHOLD = int(os.getenv("ROBOTO_PARAM_BLUR_THRESHOLD", "20"))

def is_blurry(img, threshold=BLUR_THRESHOLD):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

for file, path in inputs.files:

    topic = file.get_topic("/camera")
    topic_data = topic.get_data()
    blur_info = {}
    
    for i, msg in enumerate(topic_data):
        img = to_cv2_img(msg)
        blur_info[msg["log_time"]] = is_blurry(img)

    if any(blur_info.values()):
        file.put_tags(["camera_blur", "needs_review"])

    events = get_blur_events(blur_info)

    for start_time, end_time in events:
        Event.create(
            start_time=start_time,
            end_time=end_time,
            name="Blurry Segment",
            description="Continuous blurry image segment detected.",
            topic_ids=[topic.topic_id],
            caller_org_id=runtime.org_id)
