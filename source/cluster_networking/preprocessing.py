import os
import pandas as pd
from pathlib import Path

from shutil import copy # TODO Change this with networking
from typing import Callable

def preprocessing_function_dummy(files_to_process: list[str], keypoints: list[tuple[float, float]], target_folder: str):
    for file in files_to_process:
        copy(file, os.path.join(target_folder, Path(file).name))

# TODO Create ssh connect to cluster with slurm instructions
def preprocessing_function(files_to_process: list[str], keypoints: list[tuple[float, float]], target_folder: str):
    pass

def cluster_preprocessing(dataframe_path: str, preprocessing_function: Callable = preprocessing_function_dummy) -> None:
    project_folder = os.path.dirname(dataframe_path)
    preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")
    completed_files = [Path(file).name for file in os.listdir(preprocessed_folder)]
    
    df = pd.read_csv(dataframe_path)
    
    files_to_process = df.loc[df['Status'] == 'Preprocessing ready', 'videos'].to_list()
    mask_done = [Path(file).name in completed_files for file in files_to_process]
    points = df.loc[df['Status'] == 'Preprocessing ready', 'keypoint_positions'].to_list()
    files_to_process = [f for f, m in zip(files_to_process, mask_done) if not m]
    points = [p for p, m in zip(points, mask_done) if not m]
    
    preprocessing_function(files_to_process, points, preprocessed_folder)