from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class AudioHeader(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._title = QLabel()
        self._title.setObjectName("Title")

        self._duration = QLabel("00:00")
        self._duration.setObjectName("Subtitle")

        self._open_button = QPushButton("Open another")
        self._open_button.setObjectName("PrimaryButton")

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title_layout.addWidget(self._title)
        title_layout.addWidget(self._duration)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(title_layout)
        root.addStretch()
        root.addWidget(self._open_button, alignment=Qt.AlignmentFlag.AlignVCenter)

    @property
    def open_button(self) -> QPushButton:
        return self._open_button

    def set_audio(self, filename: str, duration_seconds: float) -> None:
        self._title.setText(filename)
        self.set_duration(duration_seconds)

    def set_duration(self, duration_seconds: float) -> None:
        total_seconds = max(0, int(round(duration_seconds)))
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            text = f"{minutes:02d}:{seconds:02d}"

        self._duration.setText(text)
