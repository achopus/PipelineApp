import os
import time
from pathlib import Path
from typing import Dict

from file_management.status import Status


def check_preprocessing_status(video_path: str) -> Status:
    """
    Check the preprocessing status of a video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Status: Current status of the video file
    """
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

    # Check if video is annotated
    points_path = os.path.join(
        Path(video_path).parent, 
        'points', 
        Path(video_path).name.replace('.mp4', '.npy')
    )
    is_annotated = os.path.exists(points_path)

    return Status.READY_PREPROCESS if is_annotated else Status.LOADED


def extract_tracking_name(tracking_path: str) -> str:
    """Extract the base name from a tracking file path."""
    return tracking_path.split("DLC")[0]


def check_folders(
    source_folder: str, 
    preprocessing_folder: str, 
    tracking_folder: str, 
    point_folder: str, 
    image_folder: str
) -> Dict[str, Status]:
    """
    Check the status of files across different project folders.
    
    Args:
        source_folder: Path to source videos folder
        preprocessing_folder: Path to preprocessed videos folder
        tracking_folder: Path to tracking results folder
        point_folder: Path to annotation points folder
        image_folder: Path to result images folder
        
    Returns:
        Dict mapping video names to their current status
    """
    videos_source = [
        Path(video).stem for video in os.listdir(source_folder) 
        if video.endswith((".mp4", ".avi"))
    ]
    videos_prepro = [
        Path(video).stem for video in os.listdir(preprocessing_folder) 
        if video.endswith((".mp4", ".avi"))
    ]
    tracking = [
        Path(f).stem for f in os.listdir(tracking_folder) 
        if f.endswith(".csv")
    ]
    images = [
        Path(f).stem for f in os.listdir(image_folder) 
        if f.endswith((".jpg", ".png"))
    ]
    points = [
        Path(point).stem for point in os.listdir(point_folder) 
        if point.endswith(".npy")
    ]

    status = {video: Status.LOADED for video in videos_source}
    
    if len(videos_source):
        for video in videos_source:
            assert video in status.keys()
            if Path(video).stem in points:
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
            
    if len(images):
        source_names = [Path(video).stem for video in videos_source]
        for image in images:
            assert Path(image).stem in source_names
            status[image] = Status.RESULTS_DONE

    return status


