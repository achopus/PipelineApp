"""
Video Points Annotation Tab for the Video Tracking Application.
"""

import os
from typing import Optional

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from PyQt5.QtCore import QDateTime

from file_management.folders import Folder
from cluster_networking.preprocessing import cluster_preprocessing
from cluster_networking.expected_runtime import preprocessing_runtime
from gui.scaling import get_scaling_manager
from gui.video_points_widget import VideoPointsWidget


class VideoPointsAnnotationTab(QWidget):
    """Widget containing the video points annotation functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.scaling_manager = get_scaling_manager()
        self.video_widget: Optional[VideoPointsWidget] = None
        self.video_points_container: QWidget = QWidget()
        
    def setup_ui(self) -> None:
        """Set up the user interface for the video points annotation tab."""
        # Create main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)  # Ensure minimum height
        
        # Create main widget for the scroll area
        main_widget = QWidget()
        main_widget.setMinimumHeight(800)  # Ensure scrollable content
        layout = QVBoxLayout(main_widget)
        
        btn_layout = QHBoxLayout()

        btn_cluster = QPushButton("⬆️ Process data on computational cluster")
        btn_cluster.setToolTip("Send all annotated videos to the cluster for processing")
        btn_cluster.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #4CAF50, stop:1 #388E3C);
                border: 2px solid #66BB6A;
                border-radius: 10px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #66BB6A, stop:1 #4CAF50);
                border: 2px solid #81C784;

            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #388E3C, stop:1 #2E7D32);

            }
        """)
        btn_cluster.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        scaled_height = self.scaling_manager.scale_size(60)
        if isinstance(scaled_height, tuple):
            scaled_height = scaled_height[1]
        btn_cluster.setMinimumHeight(scaled_height)

        btn_layout.addWidget(btn_cluster)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        # Container widget for VideoPointsWidget, added below buttons when opened
        self.video_points_container = QWidget()
        layout.addWidget(self.video_points_container)

        # Set the main widget in the scroll area
        scroll_area.setWidget(main_widget)
        
        # Set up the main layout for this tab
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        self.setLayout(tab_layout)

        def open_video_annotation():
            """Open the video annotation widget."""
            if self.parent_window and hasattr(self.parent_window, 'folder_path'):
                if self.video_widget is None:
                    self.video_widget = VideoPointsWidget(
                        os.path.join(self.parent_window.folder_path, Folder.VIDEOS.value)
                    )
                    v_layout = QVBoxLayout()
                    v_layout.setContentsMargins(0, 0, 0, 0)
                    self.video_points_container.setLayout(v_layout)
                    v_layout.addWidget(self.video_widget)
                    self.video_points_container.setVisible(True)
                else:
                    self.video_points_container.setVisible(True)
                
        def preprocessing_wrapper():
            """Wrapper for cluster preprocessing with user feedback."""
            if self.parent_window and hasattr(self.parent_window, 'yaml_path'):
                success_flag = cluster_preprocessing(self.parent_window.yaml_path)
                if success_flag:
                    videos = [os.path.join(self.parent_window.folder_path, Folder.VIDEOS.value, f) for f in os.listdir(os.path.join(self.parent_window.folder_path, Folder.VIDEOS.value)) if f.endswith((".mp4", ".avi", ".mov"))]
                    expected_runtime = preprocessing_runtime(videos)
                    now_time = QDateTime.currentDateTime()
                    finish_time = now_time.addSecs(int(expected_runtime))
                    QMessageBox.information(
                        self,
                        "Preprocessing Status",
                        f"Sending all annotated videos to cluster for preprocessing.\nProcessing is expected to finish at {finish_time.toString('dd.MM hh:mm:ss')}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Missing annotation",
                        "No preprocessing could have been done. Please annotate your data first!"
                    )
            
        open_video_annotation()
        btn_cluster.clicked.connect(preprocessing_wrapper)
