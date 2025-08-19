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
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
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
from gui.style import PROJECT_FOLDER, STATUS_COLORS


class ProjectManagementTab(QWidget):
    """Widget containing the project management functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Initialize attributes that will be used by parent
        self.folder_path: Optional[str] = None
        self.status: Optional[Dict[str, Status]] = None
        self.metrics_dataframe: Optional[DataFrame] = None
        
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Set up the user interface for the project management tab."""
        main_layout = QHBoxLayout()  # Horizontal: left (buttons+yaml) | right (table)

        # ----- LEFT SIDE -----
        left_layout = QVBoxLayout()

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_create_project = QPushButton("Create project...")
        self.btn_create_project.setFixedSize(200, 30)
        self.btn_create_project.clicked.connect(self.create_project)

        self.btn_load_yaml = QPushButton("Load existing project...")
        self.btn_load_yaml.setFixedSize(200, 30)
        self.btn_load_yaml.clicked.connect(self.load_yaml_file)

        button_layout.addWidget(self.btn_create_project)
        button_layout.addWidget(self.btn_load_yaml)
        button_layout.addStretch()
        left_layout.addLayout(button_layout)

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
            self.number_of_videos, 
        ):
            field.setReadOnly(True)
            field.setMinimumWidth(300)
            field.setFont(QFont("", 16))  # Set font size to 16

        # Special formatting for filename structure field
        self.filename_structure.setReadOnly(True)
        self.filename_structure.setMinimumWidth(300)
        self.filename_structure.setMaximumHeight(80)
        self.filename_structure.setFont(QFont("", 14))

        yaml_layout = QVBoxLayout()
        yaml_layout.setSpacing(10)
        yaml_layout.addWidget(QLabel("Project Name:"))
        yaml_layout.addWidget(self.project_name)
        yaml_layout.addWidget(QLabel("Author:"))
        yaml_layout.addWidget(self.author_name)
        yaml_layout.addWidget(QLabel("Experiment type:"))
        yaml_layout.addWidget(self.experiment_type)
        yaml_layout.addWidget(QLabel("Creation time:"))
        yaml_layout.addWidget(self.creation_time)
        yaml_layout.addWidget(QLabel("Number of videos:"))
        yaml_layout.addWidget(self.number_of_videos)
        yaml_layout.addWidget(QLabel("Filename Structure:"))
        yaml_layout.addWidget(self.filename_structure)
        
        # Manual field
        manual_text = """
How to use this application:

1. Project Management:
\t- Create a new project or load an existing one
\t- For new projects, fill in project details and select videos

2. Video Points Annotation:
\t- Switch to tab 2
\t- Mark points of interest (arena corners) on your videos
\t- Click 'Process data on computational cluster' when done
\t  Note: This process may take a while!

3. Tracking:
\t- Switch to tab 3 after preprocessing is complete
\t- Click 'Run Tracking on Cluster' to start tracking
\t- Wait for results
\t  Note: This process may take a while (even days for larger datasets)

Note: Ensure all videos are properly annotated before processing.
        """
        manual_label = QLabel("Manual:")
        manual_label.setFont(QFont("", 64))
        manual_field = QTextEdit()
        manual_field.setReadOnly(True)
        manual_field.setText(manual_text)
        manual_field.setMinimumWidth(900)
        manual_field.setMinimumHeight(600)
        manual_field.setFont(QFont("", 42))
        manual_field.setStyleSheet("background-color: #21657E; border: 1px solid #ccc; padding: 10px;")
        yaml_layout.addSpacerItem(QSpacerItem(0, 120))
        yaml_layout.addWidget(manual_label)
        yaml_layout.addWidget(manual_field)

        # Keep fields compact
        yaml_container = QWidget()
        yaml_container.setLayout(yaml_layout)
        yaml_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        left_layout.addWidget(yaml_container)
        left_layout.addStretch()

        # ----- RIGHT SIDE -----
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("File Progress:"))

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Filename", "Status"])
        # self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setColumnWidth(0, 550)
        self.table.setColumnWidth(1, 300)

        right_layout.addWidget(self.table)

        # Add both columns to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

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
            self.table.setItem(row, 0, QTableWidgetItem(Path(k).stem))
            self.table.setItem(row, 1, QTableWidgetItem(v.name))
            
        self.color_status_rows()

    def color_status_rows(self) -> None:
        """Apply background colors to rows in table based on exact status matches."""
        status_col_index = None
        
        # Find which column is 'Status'
        for col in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item is not None and header_item.text() == "Status":
                status_col_index = col
                break

        if status_col_index is None:
            return  # No status column found

        for row in range(self.table.rowCount()):
            item = self.table.item(row, status_col_index)
            if item:
                status_text = item.text().strip()
                if status_text in STATUS_COLORS:
                    color = STATUS_COLORS[status_text]
                    for col in range(self.table.columnCount()):
                        cell_item = self.table.item(row, col)
                        if cell_item:
                            cell_item.setBackground(color)
