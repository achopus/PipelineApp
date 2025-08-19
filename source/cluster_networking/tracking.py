import os
from pathlib import Path
from typing import Callable, List

from cluster_networking.ssh_handling import slurm_text_tracking, ssh_send_command
from cluster_networking.utils import convert_to_linux_path


def tracking_function(project_folder: str, files_to_process: List[str], target_folder: str) -> bool:
    """Default tracking function that sends commands to the cluster."""
    try:
        commands = slurm_text_tracking(files_to_process, target_folder)
        return ssh_send_command(commands)
    except Exception as e:
        print(f"Error in tracking function: {e}")
        return False


def cluster_tracking(yaml_path: str, preprocessing_function: Callable = tracking_function) -> bool:
    """
    Process videos on the cluster for tracking.
    
    Args:
        yaml_path: Path to the project YAML file
        preprocessing_function: Function to use for tracking
        
    Returns:
        bool: True if tracking was initiated successfully
    """
    project_folder = os.path.dirname(yaml_path)
    tracking_folder = os.path.join(project_folder, "tracking")
    completed_files = [Path(file).name for file in os.listdir(tracking_folder)]
    
    # Get preprocessed files to process
    preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")
    files_to_process = [
        os.path.join(preprocessed_folder, file) 
        for file in os.listdir(preprocessed_folder) 
        if file.endswith(('.mp4', '.avi'))
    ]
    
    # Filter out already completed files
    mask_done = [Path(file).name in completed_files for file in files_to_process]
    files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
    
    # Convert paths to Linux format for cluster
    try:
        project_folder = convert_to_linux_path(project_folder)
        tracking_folder = convert_to_linux_path(tracking_folder)
        files_to_process = list(map(convert_to_linux_path, files_to_process))
        files_to_process = [f.replace("/videos/", "/videos_preprocessed/") for f in files_to_process]

        return preprocessing_function(project_folder, files_to_process, tracking_folder)
    except Exception as e:
        print(f"Error in cluster tracking: {e}")
        return False