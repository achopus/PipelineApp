from trajectory import calculate_trajectory, calculate_timestamps, calculate_body_size
from metrics import calculate_metrics
from visualization import plot_trajectory_figure

from typing import Dict
from pandas import DataFrame

def run_metrics_pipeline(frame_path: str, source_video_path: str, save_path: str, visualize: bool = True) -> Dict[str, float]:
    frame = calculate_timestamps(frame_path, source_video_path)
    print("Frame loaded successfully.")
    trajectory = calculate_trajectory(frame)
    print("Trajectory calculated successfully.")
    head_size, body_size = calculate_body_size(frame)
    print(f"Body sizes calculated successfully. (Head: {head_size}, Body: {body_size})")
    metrics = calculate_metrics(trajectory, head_size=head_size, body_size=body_size)
    print("Metrics calculated successfully.")
    print("Metrics:", metrics)
    if visualize:
        plot_trajectory_figure(trajectory, save_path)
        print(f"Trajectory figure saved to {save_path}.")
    
    return metrics

if __name__ == "__main__":
    frame_path = "//srv-fs.ad.nudz.cz/BV_data/TrackingPRC/25ENBOH-Somethin_11_08_2025__14_13/tracking/10_25ENBOH_5mg_15min_ar4DLC_HrnetW32_NPSFeb19shuffle1_detector_060_snapshot_090.csv"
    source_video_path = "//srv-fs.ad.nudz.cz/BV_data/TrackingPRC/25ENBOH-Somethin_11_08_2025__14_13/videos/10_25ENBOH_5mg_15min_ar4.mp4"
    save_path = "example_output.png"
    run_metrics_pipeline(frame_path, source_video_path, save_path)