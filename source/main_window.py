"""
Main Window for the Video Tracking Pipeline Application.
"""

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
import pandas as pd
from pandas import DataFrame
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

# Local application imports
from file_management.status import Status
from gui.project_management_tab import ProjectManagementTab
from gui.style import DARK_STYLE
from gui.tracking_results_tab import TrackingResultsTab
from gui.video_points_annotation_tab import VideoPointsAnnotationTab
from metric_calculation.metrics_pipeline import run_metrics_pipeline
from metric_calculation.utils import construct_metric_dataframe


class MainWindow(QMainWindow):
    """Main application window containing all tabs."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video tracking")

        # Initialize data attributes
        self.folder_path: Optional[str] = None
        self.yaml_path: Optional[str] = None
        self.status: Optional[Dict[str, Status]] = None
        self.metrics: Dict[str, Dict[str, float]] = {}
        self.metrics_dataframe: Optional[DataFrame] = None
        self.video_widget = None

        # Set up the tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Create tab instances
        self.project_management_tab = ProjectManagementTab(self)
        self.video_points_tab = VideoPointsAnnotationTab(self)
        self.tracking_results_tab = TrackingResultsTab(self)

        # Add tabs to the tab widget
        self.tabs.addTab(self.project_management_tab, "1. Project Management")
        self.tabs.addTab(self.video_points_tab, "2. Video Points Annotation")
        self.tabs.addTab(self.tracking_results_tab, "3. Animal tracking + Results")

        # Initially disable tabs 2 and 3
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)

        self.setCentralWidget(self.tabs)
        self.showMaximized()

    def on_tab_changed(self) -> None:
        """Handle tab change events."""
        try:
            if hasattr(self.project_management_tab, 'update_progress_table'):
                self.project_management_tab.update_progress_table()
        except Exception:
            pass

    def enable_video_points_tab(self) -> None:
        """Enable and set up the video points annotation tab."""
        self.video_points_tab.setup_ui()
        self.tabs.setTabEnabled(1, True)

    def enable_tracking_tab(self) -> None:
        """Enable and set up the tracking and results tab."""
        self.tracking_results_tab.setup_ui()
        self.tabs.setTabEnabled(2, True)

    def update_metrics_progress(self, i: int, n: int, video_name: str) -> None:
        """Update the metrics progress display."""
        self.tracking_results_tab.update_metrics_progress(i, n, video_name)

    def metrics_pipeline_wrapper(self) -> None:
        """Wrapper for the metrics pipeline processing."""
        if self.folder_path is None:
            return
            
        source_videos = os.listdir(os.path.join(self.folder_path, "videos"))
        trackings = [
            tr for tr in os.listdir(os.path.join(self.folder_path, "tracking")) 
            if tr.endswith(".csv")
        ]
        
        pairs = []
        for video_file in source_videos:
            video_name = Path(video_file).stem
            for tracking_file in trackings:
                tracking_name = Path(tracking_file).stem
                if video_name in tracking_name:
                    pairs.append((video_file, tracking_file))
                    break
        
        n_pairs = len(pairs)
        if n_pairs == 0:
            no_data_dialog = QDialog(self)
            no_data_dialog.setWindowTitle("No tracking data to process.")
            no_data_dialog.resize(600, 200)
            from PyQt5.QtWidgets import QVBoxLayout, QLabel
            from PyQt5.QtGui import QFont
            no_data_layout = QVBoxLayout()
            progress_label = QLabel("No tracking data found for videos")
            progress_label.setFont(QFont("", 14))
            no_data_layout.addWidget(progress_label)
            no_data_dialog.setLayout(no_data_layout)
            no_data_dialog.setModal(True)
            no_data_dialog.exec_()
            return

        for i, (video_path, frame_path) in enumerate(pairs):
            metrics = run_metrics_pipeline(
                frame_path=os.path.join(self.folder_path, "tracking", frame_path),
                source_video_path=os.path.join(self.folder_path, "videos", video_path),
                save_path=os.path.join(self.folder_path, "images", f"{Path(video_path).stem}.png")
            )
            self.metrics[Path(video_path).name] = metrics
            if self.status is not None:
                self.status[Path(video_path).name] = Status.RESULTS_DONE
            self.update_metrics_progress(i, n_pairs, video_path)
        
        if self.tracking_results_tab.metrics_progress_text:
            self.tracking_results_tab.metrics_progress_text.setText("Metrics calculation completed.")
        QApplication.processEvents()
        
        if hasattr(self.project_management_tab, 'update_progress_table'):
            self.project_management_tab.update_progress_table()
        
        self.metrics_dataframe = construct_metric_dataframe(self.metrics)
        self.metrics_dataframe.to_csv(
            os.path.join(self.folder_path, "results", "metrics_dataframe.csv"), 
            index=False
        )
        self.metrics_dataframe.to_excel(
            os.path.join(self.folder_path, "results", "metrics_dataframe.xlsx"), 
            index=False
        )
        self.update_metrics_table()

    def update_metrics_table(self) -> None:
        """Update the metrics table with current data."""
        self.tracking_results_tab.update_metrics_table(self.metrics_dataframe)

    def check_preprocessing_status(self) -> None:
        """Check and display the preprocessing status of files."""
        if self.yaml_path:
            self.tracking_results_tab.check_preprocessing_status(self.yaml_path)


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
