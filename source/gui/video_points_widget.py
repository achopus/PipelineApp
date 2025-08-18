import os
from pathlib import Path
import numpy as np
import json
import cv2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QSizePolicy, QFrame, QListWidget, QListWidgetItem,
    QApplication
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QFont, QColor, QGuiApplication
from PyQt5.QtCore import Qt, QTimer, QPoint

class VideoPointsWidget(QWidget):
    def __init__(self, video_folder: str):
        super().__init__()
        self.video_folder = video_folder
        self.videos = os.listdir(video_folder)
        self.current_index = 0
        self.points_per_video = {}  # Dict[int, List[QPoint]]  (stored as full-resolution coords)
        self.points = []  # Current video points (full-res coords)
        self.display_scale = 1.0  # scale factor from full-res -> displayed

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
        self.video_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # type: ignore
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
        points = [Path(p).name for p in os.listdir(os.path.join(Path(self.video_folder).parent, 'points'))]
        for i, video in self.videos:
            filename = Path(video).name
            annotated = filename in points
            item = QListWidgetItem(f"{i+1}. {Path(filename).stem}") # type: ignore
            if annotated:
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
            if 0 <= idx < len(self.videos):
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
            self.cap = None

        video_path = self.videos[index]
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", f"Cannot open video:\n{video_path}")
            return

        points_list = []
        points_path = os.path.join(Path(video_path).parent, 'points', Path(video_path).name.replace('.mp4', '.npy'))
        if os.path.exists(points_path):
            points_npy = np.load(points_path)
            try:
                coords = np.load(points_npy)
                # coords expected to be list of (x,y) in full-resolution coords
                points_list = [QPoint(int(x), int(y)) for x, y in coords] # TODO Match this to implementation
            except Exception as e:
                print(f"Failed to load points for video index {index}: {e}")

        if index not in self.points_per_video:
            self.points_per_video[index] = points_list

        self.points = self.points_per_video.get(index, [])

        # Compute display scaling: max 80% of screen height
        screen = QGuiApplication.primaryScreen()
        screen_height = screen.availableGeometry().height() if screen is not None else 1080
        max_display_h = int(screen_height * 0.8)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if height > max_display_h:
            self.display_scale = max_display_h / height
        else:
            self.display_scale = 1.0

        w_display = int(round(width * self.display_scale))
        h_display = int(round(height * self.display_scale))

        # Set fixed size of label to displayed size
        self.video_label.setFixedSize(w_display, h_display)

        # Start timer (30 fps approx)
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

        # Scale pixmap to display size (keep aspect ratio)
        w_display = self.video_label.width()
        h_display = self.video_label.height()
        pixmap = pixmap.scaled(w_display, h_display, Qt.AspectRatioMode.KeepAspectRatio)

        painter = QPainter(pixmap)
        for idx, pt in enumerate(self.points):
            # pt holds full-resolution coords; convert to display coords
            dx = int(round(pt.x() * self.display_scale))
            dy = int(round(pt.y() * self.display_scale))
            color = self.corner_colors[idx] if idx < len(self.corner_colors) else QColor('red')
            pen = QPen(color, 8)
            painter.setPen(pen)
            painter.drawPoint(dx, dy)

        # Draw video index and filename top-left corner (display coords)
        painter.setPen(QColor('white'))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)

        text = f"{self.current_index + 1} / {len(self.videos)} : {Path(self.videos[self.current_index]).stem}"
        painter.drawText(10, 30, text)

        painter.end()

        self.video_label.setPixmap(pixmap)

        self.update_legend_positions()

    def update_legend_positions(self):
        # Update the position labels next to legend entries (show full-resolution coords)
        for idx in range(len(self.corner_names)):
            if idx < len(self.points):
                pt = self.points[idx]  # full-res
                self.legend_pos_labels[idx].setText(f"(x={pt.x()}, y={pt.y()})")
            else:
                self.legend_pos_labels[idx].setText("(x=_, y=_)")

    def on_click(self, ev):
        # ev.pos() is in display coordinates; convert to full-resolution coords
        if len(self.points) >= 4:
            return

        pos = ev.pos()
        # bounds check against displayed label size
        if 0 <= pos.x() < self.video_label.width() and 0 <= pos.y() < self.video_label.height():
            # convert to full-resolution coords before storing
            orig_x = int(round(pos.x() / self.display_scale))
            orig_y = int(round(pos.y() / self.display_scale))
            self.points.append(QPoint(orig_x, orig_y))
            self.update_frame()

    def prev_video(self):
        new_index = (self.current_index - 1) % len(self.videos)
        self.load_video(new_index)


    def next_video(self):
        new_index = (self.current_index + 1) % len(self.videos)
        self.load_video(new_index)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            # Reset current video points
            self.points = []
            self.points_per_video[self.current_index] = []

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


        for video_name, point in self.points_per_video.items():
            np.save(os.path.join(Path(self.video_folder).parent, 'points', Path(video_name).name.replace('.mp4', '.npy')), np.array([(p.x(), p.y()) for p in point]))

        # Refresh video list colors
        self.populate_video_list()