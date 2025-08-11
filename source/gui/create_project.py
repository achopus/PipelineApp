import os
from datetime import datetime

import yaml
import pandas as pd

from tqdm import tqdm
from shutil import copy as shutil_copy

from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QLineEdit, QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog

from typing import Tuple

class CreateProjectDialog(QDialog):
    """Dialog to create a new project."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setModal(True)
        self.resize(400, 200)

        layout = QVBoxLayout()

        # Project name
        layout.addWidget(QLabel("Project Name:"))
        self.project_name = QLineEdit()
        layout.addWidget(self.project_name)
        self.project_name.textChanged.connect(self.validate)

        # Author
        layout.addWidget(QLabel("Author:"))
        self.author_name = QLineEdit()
        layout.addWidget(self.author_name)
        self.author_name.textChanged.connect(self.validate)

        # Project type
        layout.addWidget(QLabel("Experiment type:"))
        self.dropdown = QComboBox()
        self.dropdown.addItems(["OFT", "EPM (Not implemented)", "[PLACEHOLDER]"])
        layout.addWidget(self.dropdown)

        # Source folder selection
        folder_layout = QHBoxLayout()
        self.folder_field = QLineEdit()
        self.folder_field.setReadOnly(True)
        folder_layout.addWidget(self.folder_field)
        btn_select_folder = QPushButton("Select Folder")
        btn_select_folder.setFixedSize(120, 30)
        btn_select_folder.clicked.connect(self.select_folder)
        folder_layout.addWidget(btn_select_folder)
        layout.addWidget(QLabel("Source Folder:"))
        layout.addLayout(folder_layout)

        # OK and Cancel buttons
        buttons_layout = QHBoxLayout()
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setEnabled(False)  # disabled initially
        self.btn_ok.setStyleSheet("border: 1px solid red;")
        self.btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Initial validation (in case fields have default text)
        self.validate()

    def set_enabled(self, text_name: str, text_author: str, text_folder: str) -> None:
        enabled = bool(text_name.strip()) and bool(text_author.strip()) and bool(text_folder.strip())
        self.btn_ok.setEnabled(enabled)
        if enabled:
            self.btn_ok.setStyleSheet("border: 1px solid green;")
        else:
            self.btn_ok.setStyleSheet("border: 1px solid red;")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.folder_field.setText(folder)
            self.validate()  # validate after setting folder

    def validate(self):
        # Read current texts
        name = self.project_name.text()
        author = self.author_name.text()
        folder = self.folder_field.text()

        # Enable/disable OK button
        self.set_enabled(name, author, folder)

        # Border colors: red if empty, green if filled
        self.set_field_color(self.project_name, name)
        self.set_field_color(self.author_name, author)
        self.set_field_color(self.folder_field, folder)

    def set_field_color(self, field, text: str):
        if text.strip():
            field.setStyleSheet("border: 1px solid green;")
        else:
            field.setStyleSheet("border: 1px solid red;")
            
def create_project_folder(dialog: CreateProjectDialog) -> Tuple[str, str]:
    PROJECT_FOLDER = "//srv-fs.ad.nudz.cz/BV_data/TrackingPRC"
    if not os.path.exists(PROJECT_FOLDER):
        os.mkdir(PROJECT_FOLDER)
    
    # Main folder creation
    project_name = dialog.project_name.text()
    creation_time = datetime.now()
    folder_name = f"{project_name}_{creation_time.strftime('%d_%m_%Y__%H_%M')}"
    assert not os.path.exists(os.path.join(PROJECT_FOLDER, folder_name)), f"This project already exists. Choose a different name."
    os.mkdir(os.path.join(PROJECT_FOLDER, folder_name))
    
    # Subfolder creation
    for subfolder in ['videos', 'videos_preprocessed', 'tracking', 'results', 'images']:
        os.mkdir(os.path.join(PROJECT_FOLDER, folder_name, subfolder))
        
    # Video copy to project folder
    source_video_files = [vid for vid in os.listdir(dialog.folder_field.text()) if vid.endswith(('.mp4', '.avi'))]
    for video in tqdm(source_video_files, desc='Copying video files to project folder'):
        shutil_copy(os.path.join(dialog.folder_field.text(), video), os.path.join(PROJECT_FOLDER, folder_name, 'videos', video))
    
    # Create a tracking csv
    df = pd.DataFrame(
        data = {
            "videos": [os.path.join(PROJECT_FOLDER, folder_name, 'videos', video) for video in source_video_files],
            "Status": ['Loaded'] * len(source_video_files)
        }
    )
    project_df_path = os.path.join(PROJECT_FOLDER, folder_name, "project_dataframe.csv")
    df.to_csv(project_df_path, index=False)
    
    yaml_dict = {
        "project_name": project_name,
        "creation_time": creation_time,
        "author": dialog.author_name.text(),
        "experiment_type": dialog.dropdown.currentText(),
        "dataframe": project_df_path
    }
    
    yaml_path = os.path.join(PROJECT_FOLDER, folder_name, "config.yaml")
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_dict, f, default_flow_style=False, allow_unicode=True)
    
    
    return yaml_path, project_df_path