import os
from pathlib import Path

from cluster_networking.ssh_handling import slurm_text_tracking, ssh_send_command
from cluster_networking.utils import convert_to_linux_path
from typing import Callable

def tracking_function(project_folder: str, files_to_process: list[str], target_folder: str):
    commands = slurm_text_tracking(files_to_process, target_folder)
    ssh_send_command(commands)

def cluster_tracking(yaml_path: str, preprocessing_function: Callable = tracking_function) -> bool:
    project_folder = os.path.dirname(yaml_path)
    tracking_folder = os.path.join(project_folder, "tracking")
    completed_files = [Path(file).name for file in os.listdir(tracking_folder)]
    
    
    files_to_process = [os.path.join(project_folder, "videos_preprocessed", file) for file in os.listdir(os.path.join(project_folder, "videos_preprocessed")) if file.endswith(('.mp4', '.avi'))]
    mask_done = [Path(file).name in completed_files for file in files_to_process]
    files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
    
    project_folder = convert_to_linux_path(project_folder)
    tracking_folder = convert_to_linux_path(tracking_folder)
    files_to_process = list(map(convert_to_linux_path, files_to_process))
    files_to_process = [f.replace("/videos/", "/videos_preprocessed/") for f in files_to_process]

    preprocessing_function(project_folder, files_to_process, tracking_folder)
    return True