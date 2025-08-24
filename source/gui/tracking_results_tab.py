"""
Tracking and Results Tab for the Video Tracking Application.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

import pandas as pd
from pandas import DataFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from file_management.status import Status
from cluster_networking.tracking import cluster_tracking
from cluster_networking.expected_runtime import tracking_runtime


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
        # Create main horizontal layout with scroll areas
        main_layout = QHBoxLayout()
        
        # Create scroll areas for left and right sides
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(300)  # Ensure minimum width
        
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setMinimumWidth(400)  # Ensure minimum width
        
        # Left side widget and layout - more compact
        left_widget = QWidget()
        left_widget.setMinimumHeight(800)  # Ensure scrollable content
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        # Remove alignment setting for PyQt5 compatibility
        
        # Compact button layout with improved styling
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        def create_action_button(text, icon, color_start, color_end):
            button = QPushButton(f"{icon} {text}")
            button.setFixedSize(250, 50)
            button.setFont(QFont("Segoe UI", 10, QFont.Bold))
            button.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {color_start}, stop:1 {color_end});
                    border: 2px solid {color_start};
                    border-radius: 8px;
                    color: white;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {color_end}, stop:1 {color_start});
                    border: 2px solid {color_end};
                }}
            """)
            return button
        
        btn_run_tracking = create_action_button("Run Tracking", "🚀", "#FF5722", "#D84315")
        btn_calculate_results = create_action_button("Get Results", "📊", "#9C27B0", "#7B1FA2")
        btn_open_images = create_action_button("Open Images", "🖼️", "#FF9800", "#F57C00")
        btn_open_results = create_action_button("Open Results", "📁", "#607D8B", "#455A64")
        
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
        self.metrics_progress_text.setMaximumHeight(120)
        self.metrics_progress_text.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                           stop:0 #2d4f5a, stop:1 #1e3a42);
                border: 2px solid #4a90a4;
                border-radius: 8px;
                padding: 15px;
                color: #e6f3f7;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 24px;
                font-weight: 500;
                selection-background-color: #4a90a4;
            }
            QTextEdit:focus {
                border-color: #66c2d9;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                           stop:0 #325a66, stop:1 #234049);
            }
        """)
        self.metrics_progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metrics_progress_text.setText("📊 Metrics can be calculated once the tracking is completed.")
        left_layout.addWidget(self.metrics_progress_text)
        left_layout.addStretch(1)

        # Compact image viewer
        image_viewer = QWidget()
        image_viewer.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                           stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #444444;
                border-radius: 12px;
                margin: 5px;
            }
        """)
        image_layout = QVBoxLayout()
        image_layout.setSpacing(15)
        image_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add trajectory preview title
        trajectory_title = QLabel("Trajectory preview")
        trajectory_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trajectory_title.setStyleSheet("""
            QLabel {
                color: #e6f3f7;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                           stop:0 #3a6b7a, stop:1 #2d5463);
                border-radius: 6px;
                border: 1px solid #4a90a4;
                margin-bottom: 10px;
            }
        """)
        image_layout.addWidget(trajectory_title)
        
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        image_label.setMinimumSize(300, 200)
        image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px dashed #666666;
                border-radius: 8px;
                color: #999999;
                font-size: 14px;
                padding: 20px;
            }
        """)
        
        file_label = QLabel()
        file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_label.setStyleSheet("""
            QLabel {
                color: #e6f3f7;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 32px;
                font-weight: 600;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                           stop:0 #3a6b7a, stop:1 #2d5463);
                border-radius: 6px;
                border: 1px solid #4a90a4;
            }
        """)
        
        image_label_width = image_label.width()
        image_label_height = image_label.height()

        # Center the labels by wrapping them in a widget
        label_container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(file_label)
        container_layout.addWidget(image_label)
        label_container.setLayout(container_layout)

        # Compact navigation
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        def create_nav_button(text, icon):
            button = QPushButton(f"{icon} {text}")
            button.setFixedSize(160, 45)
            button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #4a6b7a, stop:1 #3a5463);
                    color: white;
                    border: 2px solid #5a8a9a;
                    border-radius: 8px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 24px;
                    font-weight: 600;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #5a7b8a, stop:1 #4a6473);
                    border-color: #6a9aaa;

                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #3a5b6a, stop:1 #2a4453);
                    border-color: #4a7a8a;

                }
                QPushButton:disabled {
                    background: #2a2a2a;
                    color: #666666;
                    border-color: #444444;
                }
            """)
            return button
            
        prev_button = create_nav_button("Previous", "◀")
        next_button = create_nav_button("Next", "▶")
        
        nav_layout.addStretch()
        nav_layout.addWidget(prev_button)
        nav_layout.addWidget(next_button)
        nav_layout.addStretch()

        image_layout.addWidget(file_label)
        image_layout.addWidget(image_label)
        image_layout.addLayout(nav_layout)
        image_viewer.setLayout(image_layout)
        left_layout.addWidget(image_viewer)
        left_layout.addStretch(1)

        # Right side - Metrics table
        right_widget = QWidget()
        right_widget.setMinimumHeight(600)  # Ensure scrollable content
        right_layout = QVBoxLayout(right_widget)
        metrics_label = QLabel("Calculated Metrics:")
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(1)
        self.metrics_table.setHorizontalHeaderLabels(["Metrics will be shown here once the computation is done."])
        self.metrics_table.setColumnWidth(0, 500)
        vertical_header = self.metrics_table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        right_layout.addWidget(metrics_label)
        right_layout.addWidget(self.metrics_table)

        # Set widgets for scroll areas
        left_scroll.setWidget(left_widget)
        right_scroll.setWidget(right_widget)

        # Combine scroll areas with more space for right side
        main_layout.addWidget(left_scroll, stretch=0)
        main_layout.addWidget(right_scroll, stretch=1)
        
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
                # Scale image to fit within a reasonable size while maintaining aspect ratio
                # Use the actual widget size or fallback to reasonable defaults
                widget_width = image_label_width
                widget_height = image_label_height
                
                
                scaled_pixmap = pixmap.scaled(
                    widget_width - 100,  # Leave some margin
                    widget_height - 100,  # Leave some margin
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
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
                videos = [os.path.join(self.parent_window.folder_path, "videos_preprocessed", v) for v in os.listdir(os.path.join(self.parent_window.folder_path, "videos_preprocessed")) if self.parent_window.status[Path(v).stem] == Status.READY_TRACKING]
                expected_runtime = tracking_runtime(videos)
                finish_time = datetime.now() + timedelta(seconds=expected_runtime)
                QMessageBox.information(
                    self,
                    "Expected Runtime",
                    f"Tracking will complete around:\n{finish_time.strftime('%d.%m %H:%M:%S')}"
                )
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
                    # Only round numeric values
                    if pd.api.types.is_numeric_dtype(metrics_dataframe[column]) and pd.notna(value):
                        try:
                            value = round(float(value), 2)
                        except (ValueError, TypeError):
                            pass  # Keep original value if rounding fails
                    item = QTableWidgetItem(str(value))
                    # Note: Item will be editable by default, but functionality should work
                    self.metrics_table.setItem(j, i, item)

    def check_preprocessing_status(self, yaml_path: str) -> None:
        """Check and display the preprocessing status of files."""
        project_folder = os.path.dirname(yaml_path)
        preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")

        if not os.path.exists(preprocessed_folder):
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


        QMessageBox.information(
            self,
            "Preprocessing Status",
            f"{done_count} files are ready for tracking.\n{not_ready} files are still not ready."
        )

        # Optionally refresh the UI table
        if self.parent_window and hasattr(self.parent_window, 'update_progress_table'):
            self.parent_window.update_progress_table()
