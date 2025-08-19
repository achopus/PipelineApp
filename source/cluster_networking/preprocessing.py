"""
Video preprocessing functionality for cluster operations.
"""

import os
from pathlib import Path
from typing import Callable, List

from cluster_networking.ssh_handling import slurm_text_preprocessing, ssh_send_command
from cluster_networking.utils import convert_to_linux_path, validate_directory_exists, validate_file_exists


def preprocessing_function(files_to_process: List[str], keypoints: List[str], target_folder: str) -> bool:
    """
    Default preprocessing function that sends commands to the cluster.
    
    Args:
        files_to_process: List of video files to process
        keypoints: List of keypoint files corresponding to videos
        target_folder: Target folder for processed output
        
    Returns:
        bool: True if commands were sent successfully
    """
    try:
        commands = slurm_text_preprocessing(files_to_process, keypoints, target_folder)
        return ssh_send_command(commands)
    except Exception as e:
        print(f"Error in preprocessing function: {e}")
        return False


def cluster_preprocessing(yaml_path: str, preprocessing_function: Callable = preprocessing_function) -> bool:
    """
    Process videos on the cluster for preprocessing.
    
    Args:
        yaml_path: Path to the project YAML file
        preprocessing_function: Function to use for preprocessing
        
    Returns:
        bool: True if preprocessing was initiated successfully
    """
    if not validate_file_exists(yaml_path):
        print(f"Error: YAML file does not exist: {yaml_path}")
        return False
        
    project_folder = os.path.dirname(yaml_path)
    videos_folder = os.path.join(project_folder, "videos")
    points_folder = os.path.join(project_folder, "points")
    preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")
    
    # Validate required directories exist
    if not validate_directory_exists(videos_folder):
        print(f"Error: Videos folder does not exist: {videos_folder}")
        return False
        
    if not validate_directory_exists(points_folder):
        print(f"Error: Points folder does not exist: {points_folder}")
        return False
        
    # Create preprocessed folder if it doesn't exist
    if not os.path.exists(preprocessed_folder):
        try:
            os.makedirs(preprocessed_folder)
        except OSError as e:
            print(f"Error creating preprocessed folder: {e}")
            return False
    
    # Get completed files to avoid reprocessing
    completed_files = []
    if validate_directory_exists(preprocessed_folder):
        completed_files = [
            Path(file).name for file in os.listdir(preprocessed_folder)
            if file.endswith(('.mp4', '.avi'))
        ]
    
    # Get files to process
    try:
        video_files = [
            file for file in os.listdir(videos_folder)
            if file.endswith(('.mp4', '.avi'))
        ]
        
        files_to_process = [
            os.path.join(videos_folder, file) 
            for file in video_files
            if validate_file_exists(os.path.join(videos_folder, file))
        ]
        
        # Check for corresponding point files
        points = []
        valid_files = []
        for file_path in files_to_process:
            point_file = os.path.join(points_folder, Path(file_path).stem + ".npy")
            if validate_file_exists(point_file):
                points.append(point_file)
                valid_files.append(file_path)
            else:
                print(f"Warning: Point file not found for {file_path}: {point_file}")
        
        files_to_process = valid_files
        
        if not files_to_process:
            print("No valid files to process")
            return True
            
        # Filter out already completed files
        mask_done = [Path(file).name in completed_files for file in files_to_process]
        files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
        points = [p for p, m in zip(points, mask_done) if not m]
        
        if not files_to_process:
            print("All files already processed")
            return True
        
        # Convert paths to Linux format for cluster
        preprocessed_folder_linux = convert_to_linux_path(preprocessed_folder)
        files_to_process_linux = list(map(convert_to_linux_path, files_to_process))
        points_linux = list(map(convert_to_linux_path, points))
        
        print(f"Processing {len(files_to_process)} files")
        return preprocessing_function(files_to_process_linux, points_linux, preprocessed_folder_linux)
        
    except OSError as e:
        print(f"Error accessing directories: {e}")
        return False
    except Exception as e:
        print(f"Error in cluster preprocessing: {e}")
        return False