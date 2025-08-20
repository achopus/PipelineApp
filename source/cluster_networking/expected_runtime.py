import cv2
import numpy as np
from typing import List

def tracking_runtime(video_list: List[str], n_parallel: int = 4, time_conversion: float = 2.95) -> float:
    return runtime(video_list, n_parallel, time_conversion)

def preprocessing_runtime(video_list: List[str], n_parallel: int = 16, time_conversion: float = 0.5) -> float:
    return runtime(video_list, n_parallel, time_conversion)


def runtime(video_list: List[str], n_parallel: int, time_conversion: float) -> float:
    processes = np.zeros(n_parallel, dtype=float)
    for video in video_list:
       cap = cv2.VideoCapture(video)
       if not cap.isOpened():
           raise ValueError(f"Could not open video file: {video}")
       video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
       video_duration = video_duration * time_conversion
       lowest_process = np.argmin(processes).min() # Get first index of the lowest process (If time is the same)
       processes[lowest_process] += video_duration
       cap.release()

    return np.max(processes)
