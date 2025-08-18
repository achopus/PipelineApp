import os

from pathlib import Path

from cluster_networking.ssh_handling import slurm_text_preprocessing, ssh_send_command
from cluster_networking.utils import convert_to_linux_path
from typing import Callable

def preprocessing_function(files_to_process: list[str], keypoints: list[str], target_folder: str):
    commands = slurm_text_preprocessing(files_to_process, keypoints, target_folder)
    ssh_send_command(commands)

def cluster_preprocessing(yaml_path: str, preprocessing_function: Callable = preprocessing_function) -> bool:
    project_folder = os.path.dirname(yaml_path)
    preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")
    completed_files = [Path(file).name for file in os.listdir(preprocessed_folder)]
    
    files_to_process = [os.path.join(project_folder, "videos", file) for file in os.listdir(os.path.join(project_folder, "videos")) if file.endswith(('.mp4', '.avi'))]
    mask_done = [Path(file).name in completed_files for file in files_to_process]
    points = [os.path.join(project_folder, "points", Path(file).stem + ".npy") for file in files_to_process]
    files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
    points = [p for p, m in zip(points, mask_done) if not m]
    
    preprocessed_folder = convert_to_linux_path(preprocessed_folder)
    files_to_process = list(map(convert_to_linux_path, files_to_process))
    
    preprocessing_function(files_to_process, points, preprocessed_folder)
    return True