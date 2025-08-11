import os
import pandas as pd
from pathlib import Path

from cluster_networking.ssh_handling import slurm_text_preprocessing, ssh_send_command
from utils import convert_to_linux_path
from typing import Callable

def preprocessing_function(project_folder: str, files_to_process: list[str], keypoints: list[str], target_folder: str):
    commands = slurm_text_preprocessing(project_folder, files_to_process, keypoints, target_folder)
    ssh_send_command(commands)

def cluster_preprocessing(dataframe_path: str, preprocessing_function: Callable = preprocessing_function) -> bool:
    project_folder = os.path.dirname(dataframe_path)
    preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")
    completed_files = [Path(file).name for file in os.listdir(preprocessed_folder)]
    
    df = pd.read_csv(dataframe_path)
    if 'keypoint_positions' not in df.columns:
        return False
    
    files_to_process = df.loc[df['Status'] == 'Preprocessing ready', 'videos'].to_list()
    mask_done = [Path(file).name in completed_files for file in files_to_process]
    points = df.loc[df['Status'] == 'Preprocessing ready', 'keypoint_positions'].to_list()
    files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
    points = [p for p, m in zip(points, mask_done) if not m]
    
    project_folder = convert_to_linux_path(project_folder)
    preprocessed_folder = convert_to_linux_path(preprocessed_folder)
    files_to_process = list(map(convert_to_linux_path, files_to_process))
    
    preprocessing_function(project_folder, files_to_process, points, preprocessed_folder)
    return True