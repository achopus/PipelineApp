from metric_calculation.trajectory import calculate_trajectory, calculate_timestamps, calculate_body_size
from metric_calculation.metrics import calculate_metrics
from metric_calculation.visualization import plot_trajectory_figure
from utils.logging_config import get_logger
from utils.settings_manager import get_setting

from typing import Dict

logger = get_logger(__name__)

def run_metrics_pipeline(frame_path: str, source_video_path: str, save_path: str | None = None, visualize: bool = True) -> Dict[str, float]:
    frame = calculate_timestamps(frame_path, source_video_path)
    trajectory = calculate_trajectory(frame.copy())
    
    # Handle body size and head size based on settings
    body_size_mode = get_setting("body_size_mode", "auto")
    head_size_mode = get_setting("head_size_mode", "auto")
    
    if body_size_mode == "auto" or head_size_mode == "auto":
        calculated_head_size, calculated_body_size = calculate_body_size(frame.copy())
    
    # Determine final body size
    if body_size_mode == "manual":
        body_size = float(get_setting("manual_body_size", 1.0))
    else:
        body_size = calculated_body_size
    
    # Determine final head size
    if head_size_mode == "manual":
        head_size = float(get_setting("manual_head_size", 1.0))
    else:
        head_size = calculated_head_size
    
    metrics = calculate_metrics(trajectory.copy(), body_size=body_size, head_size=head_size)
    
    if visualize and save_path:
        plot_trajectory_figure(trajectory.copy(), save_path)
    elif visualize and not save_path:
        logger.warning("Visualization requested but no save path provided.")
    
    return metrics