import numpy as np

from typing import Tuple, Dict, Optional
from pandas import DataFrame
from numpy.typing import NDArray
from utils.settings_manager import get_setting

import warnings
warnings.filterwarnings("ignore")


def get_velocity(frame: DataFrame) -> Tuple[NDArray, NDArray]:
    x = frame["x"].to_numpy()
    y = frame["y"].to_numpy()
    t = frame["timestamps"].to_numpy()
    fps = np.round(1 / np.diff(frame["timestamps"].to_numpy(), 1).mean()).astype(int)

    x = x[::fps]
    y = y[::fps]
    t = t[::fps]
    dx = np.diff(x, append=x[-1])
    dy = np.diff(y, append=y[-1])
    dt = np.diff(t, append=t[-1])
    
    dx[np.isnan(x)] = np.nan
    dy[np.isnan(y)] = np.nan

    vx = dx / dt
    vy = dy / dt
    v = np.sqrt(vx**2 + vy**2)
    velocity_threshold = get_setting("velocity_threshold", 1.0)
    v[v < velocity_threshold] = 0

    return v, t

def get_total_distance(velocity: NDArray, time: NDArray, t_start: float, t_end: float) -> float:
    if t_end == np.inf: t_end = time[-1]
    dt = time[1] - time[0]
    i0 = np.argmin(np.abs(time - t_start))
    i1 = np.argmin(np.abs(time - t_end))
    s = velocity[i0:i1] * dt
    p_nan = np.mean(np.isnan(s))
    s = s[~np.isnan(s)]
    return np.sum(s * dt) / (1 - p_nan)

def get_distance_to_wall(x: np.ndarray, y: np.ndarray, arena_size: Optional[Tuple[float, float] | float] = None) -> np.ndarray:
        if arena_size is None:
            arena_side_cm = get_setting("arena_side_cm", 80.0)
            arena_size = (arena_side_cm, arena_side_cm)
        if type(arena_size) == float:
            arena_size = (arena_size, arena_size)
        x_dist = np.minimum(np.abs(x), np.abs(x - arena_size[1])) # type: ignore
        y_dist = np.minimum(np.abs(y), np.abs(y - arena_size[0])) # type: ignore
        return np.minimum(x_dist, y_dist)
    
def get_thigmotaxis(x: NDArray, y: NDArray, arena_size: Optional[float] = None, bin_count: Optional[int] = None) -> float:
    if arena_size is None:
        arena_size = float(get_setting("arena_side_cm", 80.0))
    if bin_count is None:
        bin_count = int(get_setting("thigmotaxis_bin_count", 25))
        
    bin_side = int(np.sqrt(bin_count))
    bin_size = arena_size / float(bin_side)

    x /= bin_size
    y /= bin_size


    x_prev, y_prev = x[0], y[0]
    X, Y = [], []
    for xi, yi in zip(x, y):
        if np.abs(xi - x_prev) > 1 or np.abs(yi - y_prev) > 1:
            X.append(np.nan)
            Y.append(np.nan)
        else:
            X.append(xi)
            Y.append(yi)
            x_prev = xi
            y_prev = yi
        
    X, Y = np.array(X), np.array(Y)
    X, Y = X[~np.isnan(X)], Y[~np.isnan(Y)]
    X, Y = X.astype(int), Y.astype(int)
    X = np.clip(X, 0, bin_side - 1)
    Y = np.clip(Y, 0, bin_side - 1)


    M = np.zeros((bin_side, bin_side))
    for x0, y0, x1, y1 in zip(X[:-1], Y[:-1], X[1:], Y[1:]):
        if any([np.isnan(num) for num in [x0, x1, y0, y1]]):
            continue
        if x1 != x0 or y1 != y0:
            M[int(y1), int(x1)] += 1

    center = M[1:-1, 1:-1]
    
    return 1 - float(center.sum() / M.sum())

def calculate_metrics(frame: DataFrame, arena_size_cm: Optional[float] = None, body_size: Optional[float] = None, head_size: Optional[float] = None, timebin_minutes: Optional[float] = None, max_time: Optional[float] = None) -> Dict[str, float]:
    # Use settings if parameters not provided
    if arena_size_cm is None:
        arena_size_cm = float(get_setting("arena_side_cm", 80.0))
    if body_size is None:
        body_size_mode = get_setting("body_size_mode", "auto")
        if body_size_mode == "manual":
            body_size = float(get_setting("manual_body_size", 1.0))
        else:
            body_size = 1.0  # Will be calculated later
    if head_size is None:
        head_size_mode = get_setting("head_size_mode", "auto")
        if head_size_mode == "manual":
            head_size = float(get_setting("manual_head_size", 1.0))
        else:
            head_size = 1.0  # Will be calculated later
    if timebin_minutes is None:
        timebin_minutes = float(get_setting("timebin_minutes", 5.0))
    if max_time is None:
        max_time_minutes = get_setting("max_time_minutes", float('inf'))
        max_time = float('inf') if max_time_minutes == float('inf') else max_time_minutes * 60  # Convert to seconds
    
    # Ensure max_time is not None for type checking
    assert max_time is not None
    
    velocity, time = get_velocity(frame)
    fps = np.round(1 / np.diff(frame["timestamps"].to_numpy(), 1).mean()).astype(int)
    total_distance = get_total_distance(velocity, time, t_start=0, t_end=np.inf)
    distance_to_wall = get_distance_to_wall(frame["x"].to_numpy(), frame["y"].to_numpy(), arena_size=(arena_size_cm, arena_size_cm))
    thigmotaxis = get_thigmotaxis(frame["x"].to_numpy(), frame["y"].to_numpy(), arena_size=arena_size_cm)
    
    is_moving = velocity > (head_size / 2)
    is_center = (distance_to_wall > body_size)[::fps]
    is_moving_in_center = np.logical_and(is_moving, is_center)

    metrics = {
        "is_moving": is_moving.mean(),
        "is_center": is_center.mean(),
        "is_moving_in_center": is_moving_in_center.mean(),
        "thigmotaxis": thigmotaxis,
        "total_distance": total_distance
    }

    i = 0
    timewindow = timebin_minutes * 60
    while True:
        time_start = i * timewindow
        time_end = time_start + timewindow
        i += 1
        if time_start > max_time or time_start > frame["timestamps"].iloc[-1]: break
        distance = get_total_distance(velocity, time, t_start=time_start, t_end=time_end)
        metrics[f"D_{int(time_start) // 60}_to_{int(time_end) // 60}"] = distance

    return metrics