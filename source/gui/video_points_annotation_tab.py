"""
Video Points Annotation Tab for the Video Tracking Application.
"""

import os
from typing import Optional

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cluster_networking.preprocessing import cluster_preprocessing
from gui.video_points_widget import VideoPointsWidget


class VideoPointsAnnotationTab(QWidget):
    """Widget containing the video points annotation functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.video_widget: Optional[VideoPointsWidget] = None
        self.video_points_container: QWidget = QWidget()
        
    def setup_ui(self) -> None:
        """Set up the user interface for the video points annotation tab."""
        # Layout & buttons for tab 2
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()

        btn_cluster = QPushButton("Process data on computational cluster")
        btn_cluster.setFixedSize(900, 60)
        btn_cluster.setStyleSheet("font-size: 42px;")  # Increase font size for better visibility

        btn_layout.addWidget(btn_cluster)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        # Container widget for VideoPointsWidget, added below buttons when opened
        self.video_points_container = QWidget()
        layout.addWidget(self.video_points_container)

        self.setLayout(layout)

        def open_video_annotation():
            """Open the video annotation widget."""
            if self.parent_window and hasattr(self.parent_window, 'folder_path'):
                if self.video_widget is None:
                    self.video_widget = VideoPointsWidget(
                        os.path.join(self.parent_window.folder_path, "videos")
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
                    QMessageBox.information(
                        self,
                        "Preprocessing Status",
                        "Sending all annotated videos to cluster for preprocessing."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Missing annotation",
                        "No preprocessing could have been done. Please annotate your data first!"
                    )
            
        open_video_annotation()
        btn_cluster.clicked.connect(preprocessing_wrapper)
