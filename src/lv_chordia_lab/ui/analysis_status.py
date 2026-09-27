from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class AnalysisStatus(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._title = QLabel("Analyzing audio…")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("font-size: 20px; font-weight: 650;")

        self._filename = QLabel()
        self._filename.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._filename.setObjectName("Subtitle")

        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setTextVisible(False)
        progress.setMaximumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 48, 24, 48)
        layout.setSpacing(14)
        layout.addStretch()
        layout.addWidget(self._title)
        layout.addWidget(self._filename)
        layout.addSpacing(8)
        layout.addWidget(progress, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def set_filename(self, filename: str) -> None:
        self._filename.setText(filename)
