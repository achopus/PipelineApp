"""
Video tracking functionality for cluster operations.
"""

import logging
import os
from pathlib import Path
from typing import Callable, List

from cluster_networking.ssh_handling import slurm_text_tracking, ssh_send_command
from cluster_networking.utils import convert_to_linux_path, validate_directory_exists, validate_file_exists
from file_management.folders import Folder

# Get logger for this module
logger = logging.getLogger(__name__)


def tracking_function(project_folder: str, files_to_process: List[str], target_folder: str) -> bool:
    """
    Default tracking function that sends commands to the cluster.
    
    Args:
        project_folder: Project folder path
        files_to_process: List of video files to process
        target_folder: Target folder for tracking output
        
    Returns:
        bool: True if commands were sent successfully
    """
    try:
        commands = slurm_text_tracking(files_to_process, target_folder, max_concurrent=5)
        return ssh_send_command(commands)
    except Exception as e:
        logger.error(f"Error in tracking function: {e}")
        return False


def cluster_tracking(yaml_path: str, tracking_function_param: Callable = tracking_function) -> bool:
    """
    Process videos on the cluster for tracking.
    
    Args:
        yaml_path: Path to the project YAML file
        tracking_function_param: Function to use for tracking
        
    Returns:
        bool: True if tracking was initiated successfully
    """
    if not validate_file_exists(yaml_path):
        logger.error(f"YAML file does not exist: {yaml_path}")
        return False
        
    project_folder = os.path.dirname(yaml_path)
    tracking_folder = os.path.join(project_folder, Folder.TRACKING.value)
    preprocessed_folder = os.path.join(project_folder, Folder.VIDEOS_PREPROCESSED.value)

    # Validate required directories exist
    if not validate_directory_exists(preprocessed_folder):
        logger.error(f"Preprocessed videos folder does not exist: {preprocessed_folder}")
        logger.error("Please run preprocessing first")
        return False
    
    # Create tracking folder if it doesn't exist
    if not os.path.exists(tracking_folder):
        try:
            os.makedirs(tracking_folder)
        except OSError as e:
            logger.error(f"Error creating tracking folder: {e}")
            return False
    
    # Get completed files to avoid reprocessing
    completed_files = []
    if validate_directory_exists(tracking_folder):
        completed_files = [
            Path(file).stem + ".mp4" for file in os.listdir(tracking_folder)
            if file.endswith('.csv')
        ] + [
            Path(file).stem + ".avi" for file in os.listdir(tracking_folder)
            if file.endswith('.csv')
        ]
    
    # Get preprocessed files to process
    try:
        preprocessed_files = [
            file for file in os.listdir(preprocessed_folder)
            if file.endswith(('.mp4', '.avi'))
        ]
        
        files_to_process = [
            os.path.join(preprocessed_folder, file) 
            for file in preprocessed_files
            if validate_file_exists(os.path.join(preprocessed_folder, file))
        ]
        
        if not files_to_process:
            logger.warning("No preprocessed files found to track")
            return True
        
        # Filter out already completed files
        mask_done = [Path(file).name in completed_files for file in files_to_process]
        files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
        
        if not files_to_process:
            logger.info("All files already tracked")
            return True
        
        # Convert paths to Linux format for cluster
        project_folder_linux = convert_to_linux_path(project_folder)
        tracking_folder_linux = convert_to_linux_path(tracking_folder)
        files_to_process_linux = list(map(convert_to_linux_path, files_to_process))
        
        logger.info(f"Tracking {len(files_to_process)} files")
        return tracking_function_param(project_folder_linux, files_to_process_linux, tracking_folder_linux)
        
    except OSError as e:
        logger.error(f"Error accessing directories: {e}")
        return False
    except Exception as e:
        logger.error(f"Error in cluster tracking: {e}")
        return False