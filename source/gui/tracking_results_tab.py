"""
Tracking and Results Tab for the Video Tracking Application.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

from pandas import DataFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cluster_networking.tracking import cluster_tracking
from file_management.status import Status
from metric_calculation.metrics_pipeline import run_metrics_pipeline
from metric_calculation.utils import construct_metric_dataframe


class TrackingResultsTab(QWidget):
    """Widget containing the tracking and results functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_image_index = 0
        self.image_files = []
        
        # UI components
        self.metrics_progress_text: Optional[QTextEdit] = None
        self.metrics_table: Optional[QTableWidget] = None
        
    def setup_ui(self) -> None:
        """Set up the user interface for the tracking and results tab."""
        main_layout = QHBoxLayout()  # Main horizontal layout to split left/right sides
        
        # Left side layout - more compact
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)  # Reduce spacing between elements
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align to top
        
        # Compact button layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)  # Reduce spacing between buttons
        btn_run_tracking = QPushButton("Run Tracking")  # Shorter text
        btn_run_tracking.setFixedSize(150, 60)  # Smaller buttons
        btn_calculate_results = QPushButton("Get Results")  # Shorter text
        btn_calculate_results.setFixedSize(150, 60)
        
        # Add buttons to open folders
        btn_open_images = QPushButton("Open Images")
        btn_open_results = QPushButton("Open Results")
        btn_open_images.setFixedSize(150, 60)
        btn_open_results.setFixedSize(150, 60)
        
        def open_images_folder():
            """Open the images folder in the system file explorer."""
            if self.parent_window and hasattr(self.parent_window, 'folder_path'):
                images_path = os.path.join(self.parent_window.folder_path, "images")
                images_path = images_path.replace("/", "\\")  # Normalize path for cross-platform compatibility
                if os.path.exists(images_path):
                    if sys.platform == 'win32':
                        os.startfile(images_path)
                    elif sys.platform == 'darwin':
                        os.system(f'open "{images_path}"')
                    else:
                        os.system(f'xdg-open "{images_path}"')

        def open_results_folder():
            """Open the results folder in the system file explorer."""
            if self.parent_window and hasattr(self.parent_window, 'folder_path'):
                results_path = os.path.join(self.parent_window.folder_path, "results")
                results_path = results_path.replace("/", "\\")
                if os.path.exists(results_path):
                    if sys.platform == 'win32':
                        os.startfile(results_path)
                    elif sys.platform == 'darwin':
                        os.system(f'open "{results_path}"')
                    else:
                        os.system(f'xdg-open "{results_path}"')

        btn_open_images.clicked.connect(open_images_folder)
        btn_open_results.clicked.connect(open_results_folder)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_run_tracking)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_calculate_results)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_open_images)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_open_results)
        btn_layout.addStretch()
        left_layout.addLayout(btn_layout)
        left_layout.addStretch(1)
        
        # Create progress text field
        self.metrics_progress_text = QTextEdit()
        self.metrics_progress_text.setReadOnly(True)
        self.metrics_progress_text.setMaximumHeight(100)
        self.metrics_progress_text.setStyleSheet("background-color: #21657E; border: 1px solid #ccc; padding: 10px;")
        self.metrics_progress_text.setFont(QFont("", 32))  # Set font size to 32
        self.metrics_progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metrics_progress_text.setText("Metrics can be calculated once the tracking is done.")
        left_layout.addWidget(self.metrics_progress_text)
        left_layout.addStretch(1)

        # Compact image viewer
        image_viewer = QWidget()
        image_layout = QVBoxLayout()
        image_layout.setSpacing(25)  # Minimal spacing
        image_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setMaximumSize(746, 600)  # Limit image size
        file_label = QLabel()
        file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Center the labels by wrapping them in a widget
        label_container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(file_label)
        container_layout.addWidget(image_label)
        label_container.setLayout(container_layout)

        # Compact navigation
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(2)
        prev_button = QPushButton("< Previous")  # Shorter text
        next_button = QPushButton("Next >")
        prev_button.setFixedSize(100, 40)  # Tiny buttons
        next_button.setFixedSize(100, 40)
        nav_layout.addStretch()
        nav_layout.addWidget(prev_button)
        nav_layout.addWidget(next_button)
        nav_layout.addStretch()

        image_layout.addWidget(file_label)
        image_layout.addWidget(image_label)
        image_layout.addLayout(nav_layout)
        image_viewer.setLayout(image_layout)
        left_layout.addWidget(image_viewer)

        # Right side - Metrics table
        right_layout = QVBoxLayout()
        metrics_label = QLabel("Calculated Metrics:")
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(1)
        self.metrics_table.setHorizontalHeaderLabels(["Metrics will be shown here once the computation is done."])
        self.metrics_table.setColumnWidth(0, 400)
        right_layout.addWidget(metrics_label)
        right_layout.addWidget(self.metrics_table)

        # Combine layouts with more space for right side
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=2)
        
        self.setLayout(main_layout)

        # Image navigation logic
        def load_images() -> None:
            """Load images from the images folder."""
            if self.parent_window and hasattr(self.parent_window, 'folder_path'):
                image_path = os.path.join(self.parent_window.folder_path, "images")
                if os.path.exists(image_path):
                    self.image_files = [f for f in os.listdir(image_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
                    show_current_image()

        def show_current_image() -> None:
            """Display the current image in the image viewer."""
            if self.image_files and self.parent_window and hasattr(self.parent_window, 'folder_path'):
                image_path = os.path.join(self.parent_window.folder_path, "images", self.image_files[self.current_image_index])
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(746, 600, Qt.AspectRatioMode.KeepAspectRatio)
                image_label.setPixmap(scaled_pixmap)
                file_label.setText(self.image_files[self.current_image_index])

        def next_image():
            """Navigate to the next image."""
            if self.image_files:
                self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
                show_current_image()

        def prev_image():
            """Navigate to the previous image."""
            if self.image_files:
                self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
                show_current_image()

        next_button.clicked.connect(next_image)
        prev_button.clicked.connect(prev_image)
        
        def run_tracking():
            """Start the tracking process."""
            if self.parent_window and hasattr(self.parent_window, 'yaml_path'):
                cluster_tracking(self.parent_window.yaml_path)  # type: ignore
            
        def calculate_results():
            """Calculate metrics and load images."""
            if self.parent_window and hasattr(self.parent_window, 'metrics_pipeline_wrapper'):
                self.parent_window.metrics_pipeline_wrapper()
            load_images()

        load_images()
        btn_run_tracking.clicked.connect(run_tracking)
        btn_calculate_results.clicked.connect(calculate_results)

    def update_metrics_progress(self, i: int, n: int, video_name: str) -> None:
        """Update the metrics progress display."""
        if self.metrics_progress_text:
            self.metrics_progress_text.setText(f"Processing video {i+1} of {n}: {video_name}")
            QApplication.processEvents()

    def update_metrics_table(self, metrics_dataframe: Optional[DataFrame]) -> None:
        """Update the metrics table with current data."""
        if metrics_dataframe is not None and self.metrics_table is not None:
            self.metrics_table.setRowCount(len(metrics_dataframe))
            self.metrics_table.setColumnCount(len(metrics_dataframe.columns))
            self.metrics_table.setHorizontalHeaderLabels(metrics_dataframe.columns)
            
            for i, column in enumerate(metrics_dataframe.columns):
                for j, value in enumerate(metrics_dataframe[column]):
                    if column != 'Filename':
                        value = round(value, 2)
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # type: ignore
                    self.metrics_table.setItem(j, i, item)

    def check_preprocessing_status(self, yaml_path: str) -> None:
        """Check and display the preprocessing status of files."""
        project_folder = os.path.dirname(yaml_path)
        preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")

        if not os.path.exists(preprocessed_folder):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Warning", 
                f"Preprocessed folder not found:\n{preprocessed_folder}"
            )
            return

        completed_files = {Path(f).name for f in os.listdir(preprocessed_folder)}

        files_loaded = os.path.join(project_folder, "videos")
        files_preprocessed = os.path.join(project_folder, "videos_preprocessed")
        
        if len(files_preprocessed):
            files_to_process = [
                video_source for video_source in files_loaded 
                if video_source not in files_preprocessed
            ]
        else:
            files_to_process = files_loaded

        done_mask = []
        now = time.time()
        min_size_bytes = 5 * 1024 * 1024  # 5 MB
        min_mod_seconds = 30  # 30 seconds

        for file_path in files_to_process:
            fname = Path(file_path).name
            preprocessed_path = os.path.join(preprocessed_folder, fname)

            if fname in completed_files:
                try:
                    stat = os.stat(preprocessed_path)
                    size_ok = stat.st_size > min_size_bytes
                    time_ok = (now - stat.st_mtime) > min_mod_seconds
                    done_mask.append(size_ok and time_ok)
                except Exception:
                    done_mask.append(False)
            else:
                done_mask.append(False)

        # Show popup summary
        done_count = sum(done_mask)
        total = len(files_loaded)
        not_ready = total - done_count

        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Preprocessing Status",
            f"{done_count} files are ready for tracking.\n{not_ready} files are still not ready."
        )

        # Optionally refresh the UI table
        if self.parent_window and hasattr(self.parent_window, 'update_progress_table'):
            self.parent_window.update_progress_table()
