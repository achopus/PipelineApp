import os
import time
from pathlib import Path
from file_management.status import Status

from typing import Dict



def check_preprocessing_status(video_path: str) -> Status:
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

    is_annotated = os.path.exists(os.path.join(Path(video_path).parent, 'points', Path(video_path).name.replace('.mp4', '.npy')))

    return Status.READY_PREPROCESS if is_annotated else Status.LOADED

def extract_tracking_name(tracking_path: str) -> str:
    return tracking_path.split("DLC")[0] + ".mp4"


def check_folders(source_folder: str, preprocessing_folder: str, tracking_folder: str, point_folder: str) -> Dict[str, Status]:
    videos_source = os.listdir(source_folder)
    videos_prepro = os.listdir(preprocessing_folder)
    tracking = [f for f in os.listdir(tracking_folder) if f.endswith(".csv")]

    status = {video: Status.LOADED for video in videos_source}
    
    points = [Path(point).name for point in os.listdir(point_folder)]
    if len(videos_source):
        for video in videos_source:
            assert video in status.keys()
            if Path(video).name in points:
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


