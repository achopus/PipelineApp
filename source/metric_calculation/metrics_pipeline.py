from metric_calculation.trajectory import calculate_trajectory, calculate_timestamps, calculate_body_size
from metric_calculation.metrics import calculate_metrics
from metric_calculation.visualization import plot_trajectory_figure
from utils.logging_config import get_logger

from typing import Dict

logger = get_logger(__name__)

def run_metrics_pipeline(frame_path: str, source_video_path: str, save_path: str | None = None, visualize: bool = True) -> Dict[str, float]:
    frame = calculate_timestamps(frame_path, source_video_path)
    trajectory = calculate_trajectory(frame.copy())
    head_size, body_size = calculate_body_size(frame.copy())
    metrics = calculate_metrics(trajectory.copy(), head_size=head_size, body_size=body_size)
    if visualize and save_path:
        plot_trajectory_figure(trajectory.copy(), save_path)
    elif visualize and not save_path:
        logger.warning("Visualization requested but no save path provided.")
    
    return metrics