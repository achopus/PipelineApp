"""
Project Management Tab for the Video Tracking Application.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import yaml
from pandas import DataFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from file_management.active_file_check import check_folders
from file_management.status import Status
from gui.create_project import CreateProjectDialog, create_project_folder
from gui.scaling import get_scaling_manager
from gui.style import PROJECT_FOLDER, STATUS_COLORS


class ProjectManagementTab(QWidget):
    """Widget containing the project management functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.scaling_manager = get_scaling_manager()
        
        # Initialize attributes that will be used by parent
        self.folder_path: Optional[str] = None
        self.status: Optional[Dict[str, Status]] = None
        self.metrics_dataframe: Optional[DataFrame] = None
        
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Set up the user interface for the project management tab."""
        # Create main horizontal layout with scroll areas
        main_layout = QHBoxLayout()
        
        # Create scroll area for left side
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(400)  # Ensure minimum width
        
        # Create scroll area for right side  
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setMinimumWidth(500)  # Ensure minimum width

        # ----- LEFT SIDE -----
        left_widget = QWidget()
        left_widget.setMinimumHeight(600)  # Ensure scrollable content
        left_layout = QVBoxLayout(left_widget)

        # Buttons with improved styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.btn_create_project = QPushButton("🖊️ Create New Project")
        self.btn_create_project.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        scaled_height = self.scaling_manager.scale_size(55)
        if isinstance(scaled_height, tuple):
            scaled_height = scaled_height[1]
        self.btn_create_project.setMinimumHeight(scaled_height)
        font_size = self.scaling_manager.scale_font_size(12)
        self.btn_create_project.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.btn_create_project.setStyleSheet("""
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
        self.btn_create_project.clicked.connect(self.create_project)

        self.btn_load_yaml = QPushButton("📂 Load Existing Project")
        self.btn_load_yaml.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_load_yaml.setMinimumHeight(scaled_height)
        self.btn_load_yaml.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.btn_load_yaml.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #2196F3, stop:1 #1976D2);
                border: 2px solid #42A5F5;
                border-radius: 10px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #42A5F5, stop:1 #2196F3);
                border: 2px solid #64B5F6;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #1976D2, stop:1 #1565C0);
            }
        """)
        self.btn_load_yaml.clicked.connect(self.load_yaml_file)

        button_layout.addWidget(self.btn_create_project)
        button_layout.addWidget(self.btn_load_yaml)
        button_layout.addStretch()
        left_layout.addLayout(button_layout)
        left_layout.addSpacing(20)

        # YAML fields
        self.project_name = QLineEdit()
        self.author_name = QLineEdit()
        self.experiment_type = QLineEdit()
        self.creation_time = QLineEdit()
        self.number_of_videos = QLineEdit()
        self.filename_structure = QTextEdit()

        for field in (
            self.project_name, 
            self.author_name, 
            self.experiment_type, 
            self.creation_time, 
            self.number_of_videos
        ):
            field.setReadOnly(True)
            field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            scaled_height = self.scaling_manager.scale_size(50)
            if isinstance(scaled_height, tuple):
                scaled_height = scaled_height[1]
            field.setMinimumHeight(scaled_height)
            field.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(12), QFont.Normal))
            field.setStyleSheet("""
                QLineEdit {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #3a3a3a, stop:1 #2d2d2d);
                    border: 2px solid #4dd0e1;
                    border-radius: 8px;
                    padding: 10px 15px;
                    color: #f0f0f0;
                    font-weight: 500;
                }
                QLineEdit:focus {
                    border-color: #66d9ef;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #404040, stop:1 #333333);
                }
            """)

        # Special formatting for filename structure field
        self.filename_structure.setReadOnly(True)
        self.filename_structure.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        scaled_max_height = self.scaling_manager.scale_size(120)
        scaled_min_height = self.scaling_manager.scale_size(80)
        if isinstance(scaled_max_height, tuple):
            scaled_max_height = scaled_max_height[1]
        if isinstance(scaled_min_height, tuple):
            scaled_min_height = scaled_min_height[1]
        self.filename_structure.setMaximumHeight(scaled_max_height)
        self.filename_structure.setMinimumHeight(scaled_min_height)
        self.filename_structure.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(11), QFont.Normal))
        self.filename_structure.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                           stop:0 #3a3a3a, stop:1 #2d2d2d);
                border: 2px solid #4dd0e1;
                border-radius: 8px;
                padding: 12px 15px;
                color: #f0f0f0;
                font-weight: 500;
            }
            QTextEdit:focus {
                border-color: #66d9ef;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                           stop:0 #404040, stop:1 #333333);
            }
        """)

        yaml_layout = QVBoxLayout()
        yaml_layout.setSpacing(15)
        
        # Create styled labels
        def create_label(text):
            label = QLabel(text)
            label.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(13), QFont.Bold))
            label.setStyleSheet("color: #4dd0e1; margin-bottom: 8px; margin-top: 5px;")
            return label
        
        yaml_layout.addWidget(create_label("Project Name:"))
        yaml_layout.addWidget(self.project_name)
        yaml_layout.addWidget(create_label("Author:"))
        yaml_layout.addWidget(self.author_name)
        yaml_layout.addWidget(create_label("Experiment Type:"))
        yaml_layout.addWidget(self.experiment_type)
        yaml_layout.addWidget(create_label("Creation Time:"))
        yaml_layout.addWidget(self.creation_time)
        yaml_layout.addWidget(create_label("Number of Videos:"))
        yaml_layout.addWidget(self.number_of_videos)
        yaml_layout.addWidget(create_label("Filename Structure:"))
        yaml_layout.addWidget(self.filename_structure)
        
        # Manual field with improved styling
        manual_text = """📖 How to use this application:

🎯 1. Project Management:
   • Create a new project or load an existing one
   • For new projects, fill in project details and select videos
   • Configure filename structure for organized data

🎬 2. Video Points Annotation:
   • Switch to tab 2 after creating/loading a project
   • Mark 4 corner points of the arena for each video:
     - Top-left (red) • Top-right (green)
     - Bottom-right (blue) • Bottom-left (orange)
   • Use arrow keys to navigate between videos
   • Press 'R' to reset points, 'S' to save progress
   • Click 'Process data on computational cluster' when done
   ⚠️ Note: This process may take a while!

🔬 3. Tracking & Analysis:
   • Switch to tab 3 after preprocessing is complete
   • Click 'Run Tracking on Cluster' to start pose estimation
   • Calculate behavioral metrics and view results
   • Export trajectory visualizations and CSV data
   ⚠️ Note: This process may take time (even days for large datasets)

💡 Tips:
   • Ensure all videos are properly annotated before processing
   • Check file status in the progress table below
   • Use consistent lighting and camera angles for best results
        """
        
        manual_label = QLabel("📋 User Manual")
        manual_label.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(16), QFont.Bold))
        manual_label.setStyleSheet("color: #4dd0e1; margin-top: 20px; margin-bottom: 10px;")
        
        manual_field = QTextEdit()
        manual_field.setReadOnly(True)
        manual_field.setText(manual_text)
        manual_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scaled_manual_height = self.scaling_manager.scale_size(450)
        if isinstance(scaled_manual_height, tuple):
            scaled_manual_height = scaled_manual_height[1]
        manual_field.setMinimumHeight(scaled_manual_height)
        manual_field.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(11), QFont.Normal))
        manual_field.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #1e4a5c, stop:1 #21657E);
                border: 2px solid #4dd0e1;
                border-radius: 10px;
                padding: 20px;
                line-height: 1.6;
                color: #f0f0f0;
            }
        """)
        
        yaml_layout.addSpacerItem(QSpacerItem(0, 30))
        yaml_layout.addWidget(manual_label)
        yaml_layout.addWidget(manual_field)

        # Keep fields compact
        yaml_container = QWidget()
        yaml_container.setLayout(yaml_layout)
        yaml_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(yaml_container)
        left_layout.addStretch()

        # ----- RIGHT SIDE -----
        right_widget = QWidget()
        right_widget.setMinimumHeight(600)  # Ensure scrollable content
        right_layout = QVBoxLayout(right_widget)
        progress_label = QLabel("📊 File Progress & Status")
        progress_label.setFont(QFont("Segoe UI", self.scaling_manager.scale_font_size(16), QFont.Bold))
        progress_label.setStyleSheet("color: #4dd0e1; margin-bottom: 15px;")
        right_layout.addWidget(progress_label)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Filename", "Processing Status"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        scaled_table_height = self.scaling_manager.scale_size(500)
        if isinstance(scaled_table_height, tuple):
            scaled_table_height = scaled_table_height[1]
        self.table.setMinimumHeight(scaled_table_height)
        
        # Hide row numbers in the vertical header
        vertical_header = self.table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)

        self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #3c3f41;
                    border: 2px solid #555;
                    border-radius: 8px;
                    color: #f0f0f0;
                    gridline-color: #555;
                    font-size: 12pt;
                }"""
            )

        right_layout.addWidget(self.table)

        # Set widgets for scroll areas
        left_scroll.setWidget(left_widget)
        right_scroll.setWidget(right_widget)

        # Add both scroll areas to main layout
        main_layout.addWidget(left_scroll)
        main_layout.addWidget(right_scroll)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """Handle resize events to maintain proportional column widths."""
        super().resizeEvent(event)
        if hasattr(self, 'table') and self.table:
            # Calculate 60% and 40% of the table width
            table_width = self.table.width() - 4  # Account for borders
            if table_width > 0:
                col1_width = int(table_width * 0.6)
                col2_width = int(table_width * 0.4)
                self.table.setColumnWidth(0, col1_width)
                self.table.setColumnWidth(1, col2_width)

    def load_yaml_file(self) -> None:
        """Load an existing project from a YAML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open YAML File", 
            PROJECT_FOLDER, 
            "YAML Files (*.yaml *.yml)"
        )
        
        if not file_path:
            return

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            
        self.yaml_path = file_path
        self.folder_path = os.path.dirname(file_path)
        
        # Update parent window attributes
        if self.parent_window:
            self.parent_window.yaml_path = self.yaml_path
            self.parent_window.folder_path = self.folder_path
        
        metrics_dataframe_path = os.path.join(self.folder_path, "results", "metrics_dataframe.csv")
        if os.path.exists(metrics_dataframe_path):
            self.metrics_dataframe = pd.read_csv(metrics_dataframe_path)
            if self.parent_window:
                self.parent_window.metrics_dataframe = self.metrics_dataframe
                # Enable statistical analysis tab since we have metrics data
                self.parent_window.enable_statistical_analysis_tab()

        self.project_name.setText(str(data.get("project_name", "")))
        self.author_name.setText(str(data.get("author", "")))
        self.experiment_type.setText(str(data.get("experiment_type", "")))
        
        timestamp_str = str(data.get("creation_time", ""))
        timestamp_formatted = datetime.fromisoformat(timestamp_str).strftime("%d.%m.%Y %H:%M")
        self.creation_time.setText(timestamp_formatted)
        
        # Display filename structure information
        filename_structure = data.get("filename_structure", {})
        if filename_structure:
            field_names = filename_structure.get("field_names", [])
            num_fields = filename_structure.get("num_fields", len(field_names))
            description = filename_structure.get("description", f"{num_fields} fields: " + " _ ".join(field_names))
            self.filename_structure.setText(description)
        else:
            self.filename_structure.setText("No filename structure defined")
        
        self.update_progress_table()

        self.btn_load_yaml.setVisible(False)
        self.btn_create_project.setVisible(False)
        
        # Enable other tabs
        if self.parent_window:
            self.parent_window.tabs.setTabEnabled(2, True)
            self.parent_window.tabs.setTabEnabled(1, True)
            self.parent_window.enable_video_points_tab()
            self.parent_window.enable_tracking_tab()
            self.parent_window.update_metrics_table()

    def create_project(self) -> None:
        """Create a new project using the project creation dialog."""
        dialog = CreateProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.yaml_path = create_project_folder(dialog)
                self.folder_path = str(Path(self.yaml_path).parent)
                
                # Update parent window attributes
                if self.parent_window:
                    self.parent_window.yaml_path = self.yaml_path
                    self.parent_window.folder_path = self.folder_path
                
                self.update_progress_table()
                
                self.project_name.setText(dialog.project_name.text())
                self.author_name.setText(dialog.author_name.text())
                self.experiment_type.setText(dialog.dropdown.currentText())
                
                timestamp_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                self.creation_time.setText(timestamp_str)
                
                # Display filename structure information
                field_names = dialog.get_field_names()
                num_fields = dialog.num_fields_spin.value()
                description = f"{num_fields} fields: " + " _ ".join(field_names)
                self.filename_structure.setText(description)

                # Enable other tabs
                if self.parent_window:
                    self.parent_window.tabs.setTabEnabled(2, True)
                    self.parent_window.tabs.setTabEnabled(1, True)
                    self.parent_window.enable_video_points_tab()
                    self.parent_window.enable_tracking_tab()
                    
            except (ValueError, RuntimeError) as e:
                QMessageBox.critical(self, "Error", f"Failed to create project:\n{str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Unexpected error during project creation:\n{str(e)}")
                
            self.btn_load_yaml.setVisible(False)
            self.btn_create_project.setVisible(False)

    def update_progress_table(self) -> None:
        """Update the progress table with current file statuses."""
        if not self.folder_path:
            return
            
        source_folder = os.path.join(str(self.folder_path), "videos")
        preprocessing_folder = os.path.join(str(self.folder_path), "videos_preprocessed")
        tracking_folder = os.path.join(str(self.folder_path), "tracking")
        points_folder = os.path.join(str(self.folder_path), "points")
        image_folder = os.path.join(str(self.folder_path), "images")
        
        self.status = check_folders(
            source_folder, 
            preprocessing_folder, 
            tracking_folder, 
            points_folder, 
            image_folder
        )
        
        # Update parent window status
        if self.parent_window:
            self.parent_window.status = self.status
        
        self.number_of_videos.setText(str(len(self.status)))
        self.table.setRowCount(len(self.status))
        
        for row, (k, v) in enumerate(self.status.items()):
            filename = Path(k).stem
            
            # Filename column
            filename_item = QTableWidgetItem(filename)
            filename_item.setFont(QFont("Segoe UI", 11, QFont.Normal))
            self.table.setItem(row, 0, filename_item)
            
            # Processing status column
            processing_item = QTableWidgetItem(v.name)
            processing_item.setFont(QFont("Segoe UI", 11, QFont.Medium))
            self.table.setItem(row, 1, processing_item)
            
        self.color_status_rows()

    def color_status_rows(self) -> None:
        """Apply background colors to rows in table based on processing status."""
        for row in range(self.table.rowCount()):
            # Color processing status (column 1)
            processing_item = self.table.item(row, 1)
            if processing_item:
                status_text = processing_item.text().strip()
                if status_text in STATUS_COLORS:
                    color = STATUS_COLORS[status_text]
                    # Apply color to both filename and processing status columns
                    for col in [0, 1]:
                        cell_item = self.table.item(row, col)
                        if cell_item:
                            # Force the background color by creating a new item with the color
                            cell_text = cell_item.text()
                            new_item = QTableWidgetItem(cell_text)
                            new_item.setBackground(color)
                            new_item.setForeground(QColor("#ffffff"))
                            # Force the item to ignore stylesheets for background
                            new_item.setFlags(cell_item.flags())
                            self.table.setItem(row, col, new_item)
