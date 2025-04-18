import numpy as np
import pandas as pd

def find_magnetometer_anomaly_events(mag_df, window_size=50, threshold_ratio=0.05):
    """
    Finds intervals where rolling std of magnetometer norm exceeds a threshold.
    """
    if not {'x', 'y', 'z'}.issubset(mag_df.columns):
        raise ValueError("mag_df must have 'x', 'y', and 'z' columns.")

    norm = np.linalg.norm(mag_df[['x', 'y', 'z']].values, axis=1)
    mean = pd.Series(norm).rolling(window=window_size, min_periods=1).mean()
    std = pd.Series(norm).rolling(window=window_size, min_periods=1).std()

    mask = std > (threshold_ratio * mean)
    times = [int(t) for t in mag_df.index.to_numpy()]

    segments = []
    start = None

    for i, flag in enumerate(mask):
        if flag and start is None:
            start = times[i]
        elif not flag and start is not None:
            segments.append((start, times[i]))
            start = None

    if start is not None:
        segments.append((start, times[-1]))

    return segments
