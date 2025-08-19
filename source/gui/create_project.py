import os
from datetime import datetime
from typing import Optional

import yaml
from shutil import copy as shutil_copy

from PyQt5.QtWidgets import (
    QHBoxLayout, 
    QComboBox, 
    QLineEdit, 
    QDialog, 
    QVBoxLayout, 
    QLabel, 
    QPushButton, 
    QFileDialog,
    QWidget,
    QProgressDialog,
    QApplication
)
from PyQt5.QtCore import Qt

from gui.style import PROJECT_FOLDER


class CreateProjectDialog(QDialog):
    """Dialog to create a new project."""
    
    def __init__(self, parent: Optional[QWidget] = None):
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
        """Enable or disable the OK button based on field validity."""
        enabled = bool(text_name.strip()) and bool(text_author.strip()) and bool(text_folder.strip())
        self.btn_ok.setEnabled(enabled)
        if enabled:
            self.btn_ok.setStyleSheet("border: 1px solid green;")
        else:
            self.btn_ok.setStyleSheet("border: 1px solid red;")

    def select_folder(self) -> None:
        """Open a dialog to select the source folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.folder_field.setText(folder)
            self.validate()  # validate after setting folder

    def validate(self) -> None:
        """Validate all input fields and update UI accordingly."""
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

    def set_field_color(self, field: QLineEdit, text: str) -> None:
        """Set the border color of a field based on whether it has text."""
        if text.strip():
            field.setStyleSheet("border: 1px solid green;")
        else:
            field.setStyleSheet("border: 1px solid red;")


def create_project_folder(dialog: CreateProjectDialog) -> str:
    """
    Create a new project folder structure and configuration file.
    
    Args:
        dialog: The dialog containing project information
        
    Returns:
        str: Path to the created YAML configuration file
    """
    if not os.path.exists(PROJECT_FOLDER):
        os.mkdir(PROJECT_FOLDER)
    
    # Main folder creation
    project_name = dialog.project_name.text()
    creation_time = datetime.now()
    folder_name = f"{project_name}_{creation_time.strftime('%d_%m_%Y__%H_%M')}"
    
    project_path = os.path.join(PROJECT_FOLDER, folder_name)
    assert not os.path.exists(project_path), \
        f"This project already exists. Choose a different name."
    os.mkdir(project_path)
    
    # Subfolder creation
    subfolders = ['videos', 'points', 'videos_preprocessed', 'tracking', 'results', 'images']
    for subfolder in subfolders:
        os.mkdir(os.path.join(project_path, subfolder))
        
    # Video copy to project folder
    source_video_files = [
        vid for vid in os.listdir(dialog.folder_field.text()) 
        if vid.endswith(('.mp4', '.avi'))
    ]
    
    if source_video_files:
        # Create progress dialog
        progress_dialog = QProgressDialog(
            "Copying video files to project folder...", 
            "Cancel", 
            0, 
            len(source_video_files),
            dialog
        )
        progress_dialog.setWindowTitle("Creating Project")
        progress_dialog.setMinimumDuration(0)  # Show immediately
        progress_dialog.show()
        
        for i, video in enumerate(source_video_files):
            if progress_dialog.wasCanceled():
                # Clean up partially created project if cancelled
                import shutil
                shutil.rmtree(project_path)
                raise RuntimeError("Project creation was cancelled by user")
                
            progress_dialog.setLabelText(f"Copying: {video}")
            progress_dialog.setValue(i)
            QApplication.processEvents()  # Keep UI responsive
            
            source_path = os.path.join(dialog.folder_field.text(), video)
            dest_path = os.path.join(project_path, 'videos', video)
            shutil_copy(source_path, dest_path)
        
        progress_dialog.setValue(len(source_video_files))  # Complete
        progress_dialog.close()
    
    # Create YAML configuration
    yaml_dict = {
        "project_name": project_name,
        "creation_time": creation_time,
        "author": dialog.author_name.text(),
        "experiment_type": dialog.dropdown.currentText(),
    }
    
    yaml_path = os.path.join(project_path, "config.yaml")
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_dict, f, default_flow_style=False, allow_unicode=True)
    
    return yaml_path