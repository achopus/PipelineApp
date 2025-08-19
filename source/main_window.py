import sys
import os
import yaml
from pathlib import Path
import time
from datetime import datetime

import pandas as pd
from pandas import DataFrame

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QDialog, QSizePolicy, QMessageBox,
    QSpacerItem
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from gui.create_project import CreateProjectDialog, create_project_folder
from gui.style import DARK_STYLE, STATUS_COLORS

from gui.video_points_widget import VideoPointsWidget
from cluster_networking.preprocessing import cluster_preprocessing
from cluster_networking.tracking import cluster_tracking


from gui.style import PROJECT_FOLDER
from file_management.active_file_check import check_folders
from file_management.status import Status

from metric_calculation.metrics_pipeline import run_metrics_pipeline
from metric_calculation.utils import construct_metric_dataframe

from typing import Dict
from PyQt5.QtWidgets import QTextEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video tracking")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.folder_path: str | None = None
        self.status: Dict[str, Status] | None = None
        self.metrics: Dict[str, Dict[str, float]] = {}
        self.metrics_dataframe: DataFrame | None = None

        self.project_tab = self.create_project_management_tab()
        self.video_points_tab = QWidget()  # empty container for tab 2 content
        self.tracking_tab = QWidget()

        self.tabs.addTab(self.project_tab, "1. Project Management")
        self.tabs.addTab(self.video_points_tab, "2. Video Points Annotation")
        self.tabs.addTab(self.tracking_tab, "3. Animal tracking + Results")

        self.tabs.setTabEnabled(2, False)  # Disable tab 3 initially
        self.tabs.setTabEnabled(1, False)  # Disable tab 2 initially
        

        self.setCentralWidget(self.tabs)
        self.showMaximized()

        self.video_widget = None

    def create_project_management_tab(self) -> QWidget:
        tab = QWidget()
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

    def on_tab_changed(self):
        try:
            self.update_progress_table()
        except Exception as e:
            pass

    def load_yaml_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open YAML File", PROJECT_FOLDER, "YAML Files (*.yaml *.yml)")
        if not file_path:
            return

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        self.yaml_path = file_path
        self.folder_path =  os.path.dirname(file_path)
        metrics_dataframe_path = os.path.join(self.folder_path, "results", "metrics_dataframe.csv")
        if os.path.exists(metrics_dataframe_path):
            self.metrics_dataframe = pd.read_csv(metrics_dataframe_path)

        self.project_name.setText(str(data.get("project_name", "")))
        self.author_name.setText(str(data.get("author", "")))
        self.experiment_type.setText(str(data.get("experiment_type", "")))
        timestamp_str = str(data.get("creation_time", ""))
        timestamp_formated = datetime.fromisoformat(timestamp_str).strftime("%d.%m.%Y %H:%M")
        self.creation_time.setText(timestamp_formated)
        self.update_progress_table()

        self.btn_load_yaml.setVisible(False)
        self.btn_create_project.setVisible(False)
        
        self.tabs.setTabEnabled(2, True)
        self.tabs.setTabEnabled(1, True)

        self.enable_video_points_tab()
        self.enable_trackres_tab()
        self.update_metrics_table()

    def create_project(self):
        dialog = CreateProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.yaml_path = create_project_folder(dialog)
            self.folder_path = str(Path(self.yaml_path).parent)
            self.update_progress_table()
            self.project_name.setText(dialog.project_name.text())
            self.author_name.setText(dialog.author_name.text())
            self.experiment_type.setText(dialog.dropdown.currentText())
            timestamp_str = datetime.now().strftime("%d.%m.%Y %H:%M")
            self.creation_time.setText(timestamp_str)
            print(f"New Project: {dialog.project_name.text()}, Author: {dialog.author_name.text()}, Folder: {dialog.folder_field.text()}")

            self.tabs.setTabEnabled(2, True)
            self.tabs.setTabEnabled(1, True)
            self.enable_video_points_tab()
            self.enable_trackres_tab()
            self.btn_load_yaml.setVisible(False)
            self.btn_create_project.setVisible(False)

    def update_progress_table(self):
        source_folder = os.path.join(str(self.folder_path), "videos")
        preprocessin_folder = os.path.join(str(self.folder_path), "videos_preprocessed")
        tracking_folder = os.path.join(str(self.folder_path), "tracking")
        points_folder = os.path.join(str(self.folder_path), "points")
        image_folder = os.path.join(str(self.folder_path), "images")
        self.status = check_folders(source_folder, preprocessin_folder, tracking_folder, points_folder, image_folder)
        self.number_of_videos.setText(str(len(self.status)))
        self.table.setRowCount(len(self.status))
        for row, (k, v) in enumerate(self.status.items()):
            self.table.setItem(row, 0, QTableWidgetItem(Path(k).stem))
            self.table.setItem(row, 1, QTableWidgetItem(v.name))
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

        self.video_points_tab.setLayout(layout)
        self.tabs.setTabEnabled(1, True)

        def open_video_annotation():
            if self.video_widget is None:
                self.video_widget = VideoPointsWidget(os.path.join(self.folder_path, "videos"))  # pyright: ignore
                v_layout = QVBoxLayout()
                v_layout.setContentsMargins(0, 0, 0, 0)
                self.video_points_container.setLayout(v_layout)
                v_layout.addWidget(self.video_widget)
                self.video_points_container.setVisible(True)
            else:
                self.video_points_container.setVisible(True)
                
        def preprocessing_wrapper():
            succes_flag = cluster_preprocessing(self.yaml_path)
            if succes_flag:
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

        
    def enable_trackres_tab(self):
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
            if self.folder_path:
                images_path = os.path.join(self.folder_path, "images")
                images_path = images_path.replace("/", "\\")  # Normalize path for cross-platform compatibility
                if os.path.exists(images_path):
                    if sys.platform == 'win32':
                        os.startfile(images_path)
                    elif sys.platform == 'darwin':
                        os.system(f'open "{images_path}"')
                    else:
                        os.system(f'xdg-open "{images_path}"')

        def open_results_folder():
            if self.folder_path:
                results_path = os.path.join(self.folder_path, "results")
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

        # Right side - Metrics table (unchanged)
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
        
        self.tracking_tab.setLayout(main_layout)

        # Image navigation logic
        self.current_image_index = 0
        self.image_files = []

        def load_images() -> None:
            if self.folder_path:
                image_path = os.path.join(self.folder_path, "images")
                if os.path.exists(image_path):
                    self.image_files = [f for f in os.listdir(image_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
                    show_current_image()

        def show_current_image() -> None:
            if self.image_files and self.folder_path:
                image_path = os.path.join(self.folder_path, "images", self.image_files[self.current_image_index])
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(746, 600, Qt.AspectRatioMode.KeepAspectRatio)
                image_label.setPixmap(scaled_pixmap)
                file_label.setText(self.image_files[self.current_image_index])

        def next_image():
            if self.image_files:
                self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
                show_current_image()

        def prev_image():
            if self.image_files:
                self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
                show_current_image()

        next_button.clicked.connect(next_image)
        prev_button.clicked.connect(prev_image)
        
        self.tabs.setTabEnabled(2, True)  # Ensure tab 3 is enabled

        def run_tracking():
            cluster_tracking(self.yaml_path)  # type: ignore
            
        def calculate_results():
            self.metrics_pipeline_wrapper()
            load_images()

        load_images()
        btn_run_tracking.clicked.connect(run_tracking)
        btn_calculate_results.clicked.connect(calculate_results)

    # Update the metrics_pipeline_wrapper method
    def update_metrics_progress(self, i: int, n: int, video_name: str):
        self.metrics_progress_text.setText(f"Processing video {i+1} of {n}: {video_name}")
        QApplication.processEvents()

    def metrics_pipeline_wrapper(self):
        if self.folder_path is None:
            return
        source_videos = os.listdir(os.path.join(self.folder_path, "videos"))
        trackings = [tr for tr in os.listdir(os.path.join(self.folder_path, "tracking")) if tr.endswith(".csv")]
        
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
            no_data_dialog.resize(600, 200)  # Make the window bigger
            no_data_layout = QVBoxLayout()
            progress_label = QLabel(f"No tracking data found for video: {video_name}")
            progress_label.setFont(QFont("", 14))
            no_data_layout.addWidget(progress_label)
            no_data_dialog.setLayout(no_data_layout)
            no_data_dialog.setModal(True)
            no_data_dialog.exec_()
            return


        for i, (video_path, frame_path) in enumerate(pairs):
            metrics = run_metrics_pipeline(frame_path=os.path.join(self.folder_path, "tracking", frame_path),
                     source_video_path=os.path.join(self.folder_path, "videos", video_path),
                     save_path=os.path.join(self.folder_path, "images", f"{Path(video_path).stem}.png"))
            self.metrics[Path(video_path).name] = metrics
            if self.status is not None:
                self.status[Path(video_path).name] = Status.RESULTS_DONE
            self.update_metrics_progress(i, n_pairs, video_path)
        
        self.metrics_progress_text.setText("Metrics calculation completed.")
        QApplication.processEvents()
        self.update_progress_table()
        
        self.metrics_dataframe = construct_metric_dataframe(self.metrics)
        self.metrics_dataframe.to_csv(os.path.join(self.folder_path, "results", "metrics_dataframe.csv"), index=False)
        self.metrics_dataframe.to_excel(os.path.join(self.folder_path, "results", "metrics_dataframe.xlsx"), index=False)
        self.update_metrics_table()

    def update_metrics_table(self) -> None:
        if self.metrics_dataframe is not None:
            self.metrics_table.setRowCount(len(self.metrics_dataframe))
            self.metrics_table.setColumnCount(len(self.metrics_dataframe.columns))
            self.metrics_table.setHorizontalHeaderLabels(self.metrics_dataframe.columns)
            for i, column in enumerate(self.metrics_dataframe.columns):
                for j, value in enumerate(self.metrics_dataframe[column]):
                    if column != 'Filename':
                        value = round(value, 2)
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) # type: ignore
                    self.metrics_table.setItem(j, i, item)

    def check_preprocessing_status(self):
        project_folder = os.path.dirname(self.yaml_path)
        preprocessed_folder = os.path.join(project_folder, "videos_preprocessed")

        if not os.path.exists(preprocessed_folder):
            QMessageBox.warning(self, "Warning", f"Preprocessed folder not found:\n{preprocessed_folder}")
            return

        completed_files = {Path(f).name for f in os.listdir(preprocessed_folder)}

        files_loaded = os.path.join(project_folder, "videos")
        files_preprocessed = os.path.join(project_folder, "videos_preprocessed")
        if len(files_preprocessed):
            files_to_process = [video_source for video_source in files_loaded if video_source not in files_preprocessed]
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

        # Optionally refresh your UI table here
        self.update_progress_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    sys.exit(app.exec_())
