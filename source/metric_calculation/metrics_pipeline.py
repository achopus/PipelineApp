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
    
    # Check if visualization is enabled in settings
    viz_enabled = get_setting("viz_enabled", True)
    
    if visualize and viz_enabled and save_path:
        try:
            # Add retry logic and better error handling for network storage
            import time
            import os
            
            max_retries = int(get_setting("viz_retry_attempts", 3))
            retry_delay = 1.0
            
            for attempt in range(max_retries):
                try:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    # Create a temporary local path first
                    temp_path = save_path.replace('.png', f'_temp_{os.getpid()}.png')
                    
                    # Plot to temporary file first
                    plot_trajectory_figure(trajectory.copy(), temp_path)
                    
                    # If temp file was created successfully, move to final location
                    if os.path.exists(temp_path):
                        if os.path.exists(save_path):
                            os.remove(save_path)  # Remove existing file
                        os.rename(temp_path, save_path)
                        logger.debug(f"Successfully saved trajectory plot to {save_path}")
                        break
                    else:
                        raise FileNotFoundError("Temporary plot file was not created")
                        
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed to save plot: {e}")
                    
                    # Clean up temp file if it exists
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                    
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Failed to save trajectory plot after {max_retries} attempts: {e}")
                        # Don't raise the exception - continue processing without the plot
                        
        except Exception as e:
            logger.error(f"Unexpected error in plot saving: {e}")
            # Continue processing even if plotting fails
            
    elif visualize and not viz_enabled:
        logger.info("Visualization requested but disabled in settings (viz_enabled=False)")
    elif visualize and not save_path:
        logger.warning("Visualization requested but no save path provided.")
    
    return metrics