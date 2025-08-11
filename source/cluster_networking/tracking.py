import os
import pandas as pd
from pathlib import Path

from cluster_networking.ssh_handling import slurm_text_tracking, ssh_send_command
from cluster_networking.utils import convert_to_linux_path
from typing import Callable

def tracking_function(project_folder: str, files_to_process: list[str], target_folder: str):
    commands = slurm_text_tracking(project_folder, files_to_process, target_folder)
    ssh_send_command(commands)

def cluster_tracking(dataframe_path: str, preprocessing_function: Callable = tracking_function) -> bool:
    project_folder = os.path.dirname(dataframe_path)
    tracking_folder = os.path.join(project_folder, "tracking")
    completed_files = [Path(file).name for file in os.listdir(tracking_folder)]
    
    df = pd.read_csv(dataframe_path)
    
    files_to_process = df.loc[df['Status'] == 'Tracking ready', 'videos'].to_list()
    mask_done = [Path(file).name in completed_files for file in files_to_process]
    files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
    
    project_folder = convert_to_linux_path(project_folder)
    tracking_folder = convert_to_linux_path(tracking_folder)
    files_to_process = list(map(convert_to_linux_path, files_to_process))
    
    preprocessing_function(project_folder, files_to_process, tracking_folder)
    return True