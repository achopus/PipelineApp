import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json
import cv2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QSizePolicy, QFrame, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal

class VideoPointsWidget(QWidget):
    data_changed = pyqtSignal(pd.DataFrame)
    def __init__(self, df: pd.DataFrame, video_col: str):
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.video_col = video_col
        self.current_index = 0
        self.points_per_video = {}  # Dict[int, List[QPoint]]
        self.points = []  # Current video points

        # Colors and corner labels
        self.corner_colors = [
            QColor('red'), 
            QColor('green'), 
            QColor('blue'), 
            QColor(255, 165, 0)  # orange
        ]
        self.corner_names = ["Top-left", "Top-right", "Bottom-right", "Bottom-left"]

        # Main horizontal layout: video on left, panel on right
        main_layout = QHBoxLayout(self)

        # Left side: video and buttons stacked vertically
        left_layout = QVBoxLayout()

        # Video display label
        self.video_label = QLabel("Video will display here")
        #self.video_label.setAlignment('Aling')
        self.video_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        left_layout.addWidget(self.video_label)

        # Buttons for video navigation
        btn_layout = QHBoxLayout()
        self.btn_prev = QPushButton("<<< Previous Video")
        self.btn_next = QPushButton("Next Video >>>")
        self.btn_save = QPushButton("Save")
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addWidget(self.btn_save)
        left_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout)

        # Right side: legend + points text + video list
        right_layout = QVBoxLayout()

        # Legend: show color box + label + position per corner
        self.legend_color_labels = []
        self.legend_pos_labels = []

        for color, name in zip(self.corner_colors, self.corner_names):
            hbox = QHBoxLayout()
            color_label = QLabel()
            color_label.setFixedSize(20, 20)
            color_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            hbox.addWidget(color_label)

            hbox.addWidget(QLabel(name))

            # Position label next to legend entry (empty initially)
            pos_label = QLabel("(x=_, y=_)")
            pos_label.setStyleSheet("font-style: italic;")
            hbox.addWidget(pos_label)
            self.legend_pos_labels.append(pos_label)

            hbox.addStretch()
            right_layout.addLayout(hbox)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        right_layout.addWidget(separator)
        
        hint = QLabel("Press 'r' to restart selection. Start from top-left and go clockwise.")
        right_layout.addWidget(hint)


        # Another separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        right_layout.addWidget(separator2)

        # Video list widget for direct access
        self.video_list = QListWidget()
        self.video_list.setMaximumWidth(300)
        self.video_list.itemClicked.connect(self.on_video_list_clicked)
        right_layout.addWidget(QLabel("Videos:"))
        right_layout.addWidget(self.video_list)

        main_layout.addLayout(right_layout)

        self.btn_prev.clicked.connect(self.prev_video)
        self.btn_next.clicked.connect(self.next_video)
        self.btn_save.clicked.connect(self.save_progress)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.frame = None

        self.video_label.mousePressEvent = self.on_click

        self.populate_video_list()
        self.load_video(self.current_index)
        self.setWindowTitle("Video Points Annotator")
        self.showMaximized()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def populate_video_list(self):
        self.video_list.clear()
        for i, row in self.df.iterrows():
            filename = row[self.video_col]
            status = row.get("Status", "")
            item = QListWidgetItem(f"{i+1}. {Path(filename).stem}") # pyright: ignore[reportOperatorIssue]
            if status == "Preprocessing ready":
                item.setForeground(QColor("white"))
                item.setBackground(QColor("green"))
            else:
                item.setForeground(QColor("white"))
                item.setBackground(QColor("darkred"))
            self.video_list.addItem(item)

    def on_video_list_clicked(self, item):
        # Parse the clicked item's index from the text
        text = item.text()
        try:
            idx_str = text.split(".", 1)[0]
            idx = int(idx_str) - 1
            if 0 <= idx < len(self.df):
                self.load_video(idx)
        except Exception:
            pass

    def load_video(self, index):
        # Save current points before switching
        if self.cap is not None:
            self.points_per_video[self.current_index] = self.points

        self.current_index = index

        if self.cap:
            self.cap.release()
        video_path = self.df.at[index, self.video_col]
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", f"Cannot open video:\n{video_path}")
            return

        # === Load saved points from dataframe if any ===
        points_list = []
        if "keypoint_positions" in self.df.columns:
            points_json = self.df.at[index, "keypoint_positions"]
            if points_json and isinstance(points_json, str):
                try:
                    coords = json.loads(points_json)
                    points_list = [QPoint(int(x), int(y)) for x, y in coords]
                except Exception as e:
                    print(f"Failed to load points for video index {index}: {e}")

        # Restore points from cache or from dataframe
        if index not in self.points_per_video:
            self.points_per_video[index] = points_list

        self.points = self.points_per_video.get(index, [])

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_label.setFixedSize(width, height)

        self.timer.start(int(1000 / 30))

        self.update_legend_positions()

        # Update selection in video list
        self.video_list.setCurrentRow(index)

    def next_frame(self):
        if self.cap is None:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return
        self.frame = frame
        self.update_frame()

    def update_frame(self):
        if self.frame is not None and isinstance(self.frame, (np.ndarray,)):
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        else:
            return

        pixmap = QPixmap.fromImage(qt_img)

        painter = QPainter(pixmap)
        for idx, pt in enumerate(self.points):
            color = self.corner_colors[idx] if idx < len(self.corner_colors) else QColor('red')
            pen = QPen(color, 8)
            painter.setPen(pen)
            painter.drawPoint(pt)

        # Draw video index and filename top-left corner
        painter.setPen(QColor('white'))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)

        text = f"{self.current_index + 1} / {len(self.df)} : {Path(self.df.at[self.current_index, self.video_col]).stem}"
        painter.drawText(10, 30, text)

        painter.end()

        self.video_label.setPixmap(pixmap)

        self.update_legend_positions()

    def update_legend_positions(self):
        # Update the position labels next to legend entries
        for idx in range(len(self.corner_names)):
            if idx < len(self.points):
                pt = self.points[idx]
                self.legend_pos_labels[idx].setText(f"(x={pt.x()}, y={pt.y()})")
            else:
                self.legend_pos_labels[idx].setText("(x=_, y=_)")

    def on_click(self, ev):
        if len(self.points) >= 4:
            return
        pos = ev.pos()
        if 0 <= pos.x() < self.video_label.width() and 0 <= pos.y() < self.video_label.height():
            self.points.append(pos)
            self.update_frame()


    def prev_video(self):
        new_index = (self.current_index - 1) % len(self.df)
        self.load_video(new_index)


    def next_video(self):
        new_index = (self.current_index + 1) % len(self.df)
        self.load_video(new_index)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            # Reset current video points
            self.points = []
            self.points_per_video[self.current_index] = []

            # Update DataFrame status back to 'Loaded' for this video index
            if "keypoint_positions" in self.df.columns:
                self.df.at[self.current_index, "keypoint_positions"] = ""
            self.df.at[self.current_index, "Status"] = "Loaded"

            self.update_frame()

            # Refresh video list colors
            self.populate_video_list()
            self.save_progress()

        else:
            super().keyPressEvent(event)

    def save_progress(self):
        def has_points(val: str | None):
            try:
                if val is None: return False
                return bool(val and val.strip())
            except Exception as e:
                return False

        self.points_per_video[self.current_index] = self.points
        if "keypoint_positions" not in self.df.columns:
            self.df["keypoint_positions"] = ""

        # Build a Series from points_per_video dict: index -> json string
        s = pd.Series({
            idx: json.dumps([(p.x(), p.y()) for p in points]) if (points and len(points) == 4) else ''
            for idx, points in self.points_per_video.items()
        })

        # Assign the Series to the DataFrame column by matching indices
        self.df.loc[s.index, "keypoint_positions"] = s
        self.df.loc[self.df["keypoint_positions"].apply(has_points), "Status"] = "Preprocessing ready"
        self.df.loc[~self.df["keypoint_positions"].apply(has_points), "Status"] = "Loaded"

        # Refresh video list colors
        self.populate_video_list()
        
        self.data_changed.emit(self.df.copy())
