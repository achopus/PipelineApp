import os
import pandas as pd
from pathlib import Path
import time

from pandas import DataFrame
from typing import Dict

from file_management.status import Status


def check_preprocessing_status(video_path: str, df: DataFrame) -> Status:
    if os.path.exists(video_path):
        min_size_bytes = 5 * 1024 * 1024  # 5 MB
        min_mod_seconds = 30  # 30 seconds
        now = time.time()
        stat = os.stat(video_path)
        size_ok = stat.st_size > min_size_bytes
        time_ok = (now - stat.st_mtime) > min_mod_seconds
        if size_ok and time_ok:
            return Status.READY_TRACKING
        else:
            return Status.PREPROCESSING_IN_PROGRESS

    
    points = df[df['videos'] == video_path, 'keypoint_locations']
    if type(points) == str:
        return Status.READY_PREPROCESS
    else:
        return Status.LOADED


def extract_tracking_name(tracking_path: str) -> str:
    return tracking_path.split("DLC")[0] + ".mp4"


def check_folders(source_folder: str, preprocessing_folder: str, tracking_folder: str, dataframe_path: str) -> Dict[str, Status]:
    df = pd.read_csv(dataframe_path)
    videos_source = os.listdir(source_folder)
    videos_prepro = os.listdir(preprocessing_folder)
    tracking = [f for f in os.listdir(tracking_folder) if f.endswith(".csv")]

    status = {video: Status.LOADED for video in videos_source}
    
    
    if len(videos_source):
        for video in videos_source:
            points = df.loc[df['videos'] == video, 'keypoint_positions']
            if type(points) == str:
                status[video] = Status.READY_PREPROCESS
    else:
        return status    
        
    if len(videos_prepro):
        for video in videos_prepro:
            assert video in status.keys()
            status[video] = Status.READY_TRACKING
    else:
        return status

    if len(tracking):
        for track in tracking:
            track_modified = extract_tracking_name(track)
            assert track_modified in status.keys()
            status[track_modified] = Status.TRACKED

    return status


