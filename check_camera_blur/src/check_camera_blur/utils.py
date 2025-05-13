import numpy as np
import cv2

def to_cv2_img(msg):
    return cv2.imdecode(np.frombuffer(msg["data"], np.uint8), cv2.IMREAD_COLOR)

def get_blur_events(blur_info):
    """
    Scan the `blur_info` dictionary (key is timestamp, value is bool indicating blur)
    and return a list of event tuples (start_time, end_time) for each blurry stretch.
    """
    event_tuples = []
    segment_start = None  # None -> currently *not* inside a blur section

    for timestamp, is_blur in blur_info.items():
        if is_blur:
            # Enter (or stay in) a blurry stretch
            segment_start = segment_start or timestamp
        elif segment_start:
            # We just left a blurry stretch → close it
            event_tuples.append((segment_start, timestamp))
            segment_start = None  # reset

    # If the last segment ends while still blurry -> close it
    if segment_start:
        event_tuples.append((segment_start, max(blur_info.keys())))  # Using max timestamp as end

    return event_tuples
