import os
import numpy as np
import pandas as pd
import scipy.ndimage
import cv2

from pandas import DataFrame
from numpy.typing import NDArray
from typing import Tuple


def gaussian_blur_nan(y: NDArray, sigma: float) -> NDArray:
    """Applies Gaussian blur while ignoring NaN values."""
    nan_mask = np.isnan(y)  # Identify NaNs
    y_filled = np.copy(y)

    # Fill NaNs with 0 to avoid affecting convolution
    y_filled[nan_mask] = 0  

    # Apply Gaussian filter
    blurred = scipy.ndimage.gaussian_filter1d(y_filled, sigma=sigma, mode='constant')

    # Create a weight array (1 for valid values, 0 for NaNs)
    weights = np.ones_like(y)
    weights[nan_mask] = 0
    weights = scipy.ndimage.gaussian_filter1d(weights, sigma=sigma, mode='constant')

    # Avoid division by zero (where all nearby values were NaN)
    valid = weights > 0
    blurred[valid] /= weights[valid]
    blurred[~valid] = np.nan  # Keep NaNs where all values were NaN
    
    return blurred

def calculate_timestamps(dataframe_path: str, source_video_path: str) -> DataFrame:
    assert os.path.exists(dataframe_path) and os.path.exists(source_video_path), "Dataframe or video path does not exist."
    
    df = pd.read_csv(dataframe_path, header=[1, 2]) # DLC specific data saving
    
    cap = cv2.VideoCapture(source_video_path)
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    time_step = 1 / fps
    
    timestamps = np.arange(0, n_frames / fps, time_step)
    df['timestamps'] = timestamps
    return df

def point_to_line_distance(X: NDArray, Y: NDArray) -> NDArray:
    """Calculate the perpendicular distance of p2 from the line passing through p1 and p3."""
    x1, y1 = X[:, 0], Y[:, 0]
    x2, y2 = X[:, 2], Y[:, 2]
    
    x0, y0 = X[:, 1], Y[:, 1]
    
    return np.abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt((y2 - y1)**2 + (x2 - x1)**2)

def remove_small_clusters(arr : NDArray, cluster_size: int) -> NDArray:
    arr = np.array(arr, dtype=float)  # Ensure it's a NumPy array of floats (to support np.nan)
    mask = np.isnan(arr)
    
    # Identify clusters of non-NaN values
    clusters = []
    start = None
    
    for i in range(len(arr)):
        if not mask[i]:
            if start is None:
                start = i
        else:
            if start is not None:
                clusters.append((start, i))
                start = None
    
    if start is not None:
        clusters.append((start, len(arr)))
    
    # Remove clusters with <= N elements
    for start, end in clusters:
        if end - start <= cluster_size:
            arr[max(start - cluster_size // 5, 0):min(end + cluster_size // 5, len(arr) - 1)] = np.nan

    return arr

def calculate_body_size(dataframe: DataFrame, arena_side_cm: float = 80.0, corner_x_px: int = 1100, corner_y_px: int = 100) -> Tuple[float, float]:
    trajectory_nose = dataframe.nose
    trajectory_neck = dataframe.neck
    trajectory_tail = dataframe.tail_start

    x_nose = trajectory_nose.x.to_numpy() # type: ignore
    y_nose = trajectory_nose.y.to_numpy() # type: ignore
    l_nose = trajectory_nose.likelihood.to_numpy() # type: ignore

    x_neck = trajectory_neck.x.to_numpy() # type: ignore
    y_neck = trajectory_neck.y.to_numpy() # type: ignore
    l_neck = trajectory_neck.likelihood.to_numpy() # type: ignore

    x_tail = trajectory_tail.x.to_numpy() # type: ignore
    y_tail = trajectory_tail.y.to_numpy() # type: ignore
    l_tail = trajectory_tail.likelihood.to_numpy() # type: ignore

    

    X = np.hstack([x_nose[:, None], x_neck[:, None], x_tail[:, None]])
    Y = np.hstack([y_nose[:, None], y_neck[:, None], y_tail[:, None]])
    X = (X - corner_x_px) * (arena_side_cm / 100)
    Y = (Y - corner_y_px) * (arena_side_cm / 100)
    
    L = np.hstack([l_nose[:, None], l_neck[:, None], l_tail[:, None]])
    mask = L.min(1) > 0.95
    X = X[mask, :]
    Y = Y[mask, :]
    
    body_size = np.sqrt((X[:, 1] - X[:, 2])**2 + (Y[:, 1] - Y[:, 2])**2)
    head_size = np.sqrt((X[:, 0] - X[:, 1])**2 + (Y[:, 0] - Y[:, 1])**2)
    on_line = point_to_line_distance(X, Y)
    on_line_mask = on_line < 0.25
    body_size = body_size[on_line_mask]
    head_size = head_size[on_line_mask]
    body_size = np.median(body_size)
    head_size = np.median(head_size)
    
    return float(body_size), float(head_size)

def calculate_trajectory(dataframe: DataFrame,
                         arena_side_cm: float = 80, corner_x_px: int = 1100, corner_y_px: int = 100,
                         detection_threshold: float = 0.6, motion_blur: float = 2) -> DataFrame:
    timestamps = dataframe['timestamps'].values
    time_step = timestamps[1] - timestamps[0] if len(timestamps) > 1 else 1
    
    trajectory_nose = dataframe.nose
    trajectory_neck = dataframe.neck
    trajectory_tail = dataframe.tail_start

    x_nose = trajectory_nose.x.to_numpy() # type: ignore
    y_nose = trajectory_nose.y.to_numpy() # type: ignore
    l_nose = trajectory_nose.likelihood.to_numpy() # type: ignore

    x_neck = trajectory_neck.x.to_numpy() # type: ignore
    y_neck = trajectory_neck.y.to_numpy() # type: ignore
    l_neck = trajectory_neck.likelihood.to_numpy() # type: ignore

    x_tail = trajectory_tail.x.to_numpy() # type: ignore
    y_tail = trajectory_tail.y.to_numpy() # type: ignore
    l_tail = trajectory_tail.likelihood.to_numpy() # type: ignore

    X = np.hstack([x_nose[:, None], x_neck[:, None], x_tail[:, None]])
    Y = np.hstack([y_nose[:, None], y_neck[:, None], y_tail[:, None]])
    L = np.hstack([l_nose[:, None], l_neck[:, None], l_tail[:, None]])

    X = (X - corner_x_px) * (arena_side_cm / 100)
    Y = (Y - corner_y_px) * (arena_side_cm / 100)
    X = (X * L).sum(1) / L.sum(1)
    Y = (Y * L).sum(1) / L.sum(1)
    X[L.max(1) < detection_threshold] = np.nan
    Y[L.max(1) < detection_threshold] = np.nan

    X = remove_small_clusters(X, 1 * int(1 / time_step))
    Y = remove_small_clusters(Y, 1 * int(1 / time_step))
    
    X = gaussian_blur_nan(X, sigma=motion_blur)
    Y = gaussian_blur_nan(Y, sigma=motion_blur)

    df_center = pd.DataFrame(data={
        "x": X,
        "y": Y,
        "timestamps": timestamps
    })

    return df_center

