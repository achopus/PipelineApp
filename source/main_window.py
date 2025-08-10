import sys
import os
from cv2 import QT_FONT_BLACK
import yaml
from pathlib import Path
import time
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QDialog, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QFont
from gui.create_project import CreateProjectDialog, create_project_folder
from gui.style import DARK_STYLE, STATUS_COLORS

from gui.video_points_widget import VideoPointsWidget
from cluster_networking.preprocessing import cluster_preprocessing

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video tracking")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        self.project_tab = self.create_project_management_tab()
        self.video_points_tab = QWidget()  # empty container for tab 2 content
        self.tracking_tab = QWidget()

        self.tabs.addTab(self.project_tab, "1. Project Management")
        self.tabs.addTab(self.video_points_tab, "2. Video Points Annotation")
        self.tabs.addTab(self.tracking_tab, "3. Animal tracking")

        self.tabs.setTabEnabled(2, False)  # Disable tab 3 initially
        self.tabs.setTabEnabled(1, False)  # Disable tab 2 initially
        

        self.setCentralWidget(self.tabs)
        self.showMaximized()

        self.dataframe_path = None
        self.dataframe = None
        self.video_widget = None

    def create_project_management_tab(self) -> QWidget:
        tab = QWidget()
        main_layout = QHBoxLayout()  # Horizontal: left (buttons+yaml) | right (table)

        # ----- LEFT SIDE -----
        left_layout = QVBoxLayout()

        # Buttons
        button_layout = QHBoxLayout()
        btn_create_project = QPushButton("Create project...")
        btn_create_project.setFixedSize(200, 30)
        btn_create_project.clicked.connect(self.create_project)

        btn_load_yaml = QPushButton("Load existing project...")
        btn_load_yaml.setFixedSize(200, 30)
        btn_load_yaml.clicked.connect(self.load_yaml_file)

        button_layout.addWidget(btn_create_project)
        button_layout.addWidget(btn_load_yaml)
        button_layout.addStretch()
        left_layout.addLayout(button_layout)

        # YAML fields
        self.project_name = QLineEdit()
        self.author_name = QLineEdit()
        self.experiment_type = QLineEdit()
        self.creation_time = QLineEdit()
        self.number_of_videos = QLineEdit()
        self.overall_status = QLineEdit()

        for field in (self.project_name, self.author_name, self.experiment_type, self.creation_time, self.number_of_videos, self.overall_status):
            field.setReadOnly(True)
            field.setMinimumWidth(300)
            field.setFont(QFont("", 16))  # Set font size to 16

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
        yaml_layout.addWidget(QLabel("Overall status:"))
        yaml_layout.addWidget(self.overall_status)

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
        #self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setColumnWidth(0, 550)
        self.table.setColumnWidth(1, 300)

        right_layout.addWidget(self.table)

        # Add both columns to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        tab.setLayout(main_layout)
        return tab

    def load_yaml_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open YAML File", "", "YAML Files (*.yaml *.yml)")
        if not file_path:
            return

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        self.project_name.setText(str(data.get("project_name", "")))
        self.author_name.setText(str(data.get("author", "")))
        self.experiment_type.setText(str(data.get("experiment_type", "")))
        timestamp_str = str(data.get("creation_time", ""))
        timestamp_formated = datetime.fromisoformat(timestamp_str).strftime("%d.%m.%Y %H:%M")
        self.creation_time.setText(timestamp_formated)
        self.dataframe_path = str(data.get("dataframe", ""))
        self.load_progress_table()
        self.number_of_videos.setText(str(self.dataframe.shape[0] if type(self.dataframe) == pd.DataFrame else 0))

        self.enable_video_points_tab()

    def create_project(self):
        dialog = CreateProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.yaml_path, self.dataframe_path = create_project_folder(dialog)
            self.load_progress_table()
            self.project_name.setText(dialog.project_name.text())
            self.author_name.setText(dialog.author_name.text())
            self.experiment_type.setText(dialog.dropdown.currentText())
            timestamp_str = datetime.now().strftime("%d.%m.%Y %H:%M")
            self.creation_time.setText(timestamp_str)
            self.number_of_videos.setText(str(self.dataframe.shape[0] if type(self.dataframe) == pd.DataFrame else 0))
            print(f"New Project: {dialog.project_name.text()}, Author: {dialog.author_name.text()}, Folder: {dialog.folder_field.text()}")

            self.enable_video_points_tab()

    def load_progress_table(self):
        if self.dataframe_path and os.path.exists(self.dataframe_path):
            df = pd.read_csv(self.dataframe_path)
            self.dataframe = df.copy()
        else:
            df = pd.DataFrame(columns=["Filename", "Status"])

        self.table.setRowCount(len(df))
        for row in range(len(df)):
            self.table.setItem(row, 0, QTableWidgetItem(Path(str(df.iloc[row, 0])).stem))
            self.table.setItem(row, 1, QTableWidgetItem(str(df.iloc[row, 1])))
        self.color_status_rows()
            
    def update_progress_table(self):
        if type(self.dataframe) != pd.DataFrame: return
        df = self.dataframe.copy()
        self.table.setRowCount(len(df))
        for row in range(len(df)):
            self.table.setItem(row, 0, QTableWidgetItem(Path(str(df.iloc[row, 0])).stem))
            self.table.setItem(row, 1, QTableWidgetItem(str(df.iloc[row, 1])))
        self.color_status_rows()

    def color_status_rows(self):
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

    def enable_video_points_tab(self):
        if not self.dataframe_path or not os.path.exists(self.dataframe_path):
            return

        df = pd.read_csv(self.dataframe_path)

        # Layout & buttons for tab 2
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()

        btn_open_video = QPushButton("Open Video Annotation")
        btn_open_video.setFixedSize(350, 30)

        btn_cluster = QPushButton("Process data on computational cluster")
        btn_cluster.setFixedSize(450, 30)
        
        btn_check_status = QPushButton("Check preprocessing status")
        btn_check_status.setFixedSize(400, 30)
        

        btn_layout.addWidget(btn_open_video)
        btn_layout.addWidget(btn_cluster)
        btn_layout.addWidget(btn_check_status)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)


        # Container widget for VideoPointsWidget, added below buttons when opened
        self.video_points_container = QWidget()
        #self.video_points_container.setVisible(False)
        layout.addWidget(self.video_points_container)

        self.video_points_tab.setLayout(layout)
        self.tabs.setTabEnabled(1, True)

        def open_video_annotation():
            if self.video_widget is None:
                self.video_widget = VideoPointsWidget(df, "videos")
                self.video_widget.data_changed.connect(self.on_video_points_data_changed)
                v_layout = QVBoxLayout()
                v_layout.setContentsMargins(0, 0, 0, 0)
                self.video_points_container.setLayout(v_layout)
                v_layout.addWidget(self.video_widget)
                self.video_points_container.setVisible(True)
            else:
                self.video_points_container.setVisible(True)
                
        def preprocessing_wrapper():
            #self.video_points_container.setVisible(False)
            assert self.dataframe_path is not None, "Path to the project dataframe has not been set."
            succes_flag = cluster_preprocessing(self.dataframe_path)
            if succes_flag:
                QMessageBox.information(
                    self,
                    "Preprocessing Status",
                    "Sending all annotated videos to cluster for preprocessing. Check on their status with the 'Check preprocessing status' button."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Missing annotation",
                    "No preprocessing could have been done. Please annotate your data first!"
                )
            
        def check_preprocessing_status():
            assert self.dataframe_path and isinstance(self.dataframe, pd.DataFrame)
            project_folder = os.path.dirname(self.dataframe_path)
            preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")

            if not os.path.exists(preprocessed_folder):
                QMessageBox.warning(self, "Warning", f"Preprocessed folder not found:\n{preprocessed_folder}")
                return

            completed_files = {Path(f).name for f in os.listdir(preprocessed_folder)}

            files_to_process = self.dataframe.loc[self.dataframe['Status'] == 'Preprocessing ready', 'videos'].to_list()

            done_mask = []
            now = time.time()
            min_size_bytes = 5 * 1024 * 1024  # 5 MB
            min_mod_seconds = 5  # 5 seconds

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

            # Update dataframe status for done files
            idxs = self.dataframe[self.dataframe['Status'] == 'Preprocessing ready'].index
            done_indices = idxs[[i for i, done in enumerate(done_mask) if done]]

            self.dataframe.loc[done_indices, 'Status'] = 'Tracking ready'

            # Show popup summary
            done_count = self.dataframe[self.dataframe['Status'] == 'Tracking ready'].shape[0]
            total = self.dataframe.shape[0]
            not_ready = total - done_count

            QMessageBox.information(
                self,
                "Preprocessing Status",
                f"{done_count} files are ready for tracking.\n{not_ready} files are still not ready."
            )

            # Optionally refresh your UI table here
            self.update_progress_table()
            # Save dataframe changes if needed
            if self.dataframe_path:
                self.dataframe.to_csv(self.dataframe_path, index=False)
            
            
            

        btn_open_video.clicked.connect(open_video_annotation)
        btn_cluster.clicked.connect(preprocessing_wrapper)
        btn_check_status.clicked.connect(check_preprocessing_status)
    
    def on_video_points_data_changed(self, updated_df: pd.DataFrame):
        self.dataframe = updated_df.copy()
        self.update_progress_table()
        # Save to CSV file immediately
        if self.dataframe_path:
            self.dataframe.to_csv(self.dataframe_path, index=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    sys.exit(app.exec_())
