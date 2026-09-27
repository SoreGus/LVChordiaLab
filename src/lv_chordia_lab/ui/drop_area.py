from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from lv_chordia_lab.audio.audio_file import SUPPORTED_EXTENSIONS


class DropArea(QFrame):
    choose_requested = Signal()
    file_dropped = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("Card")
        self.setAcceptDrops(True)
        self.setMinimumHeight(280)

        title = QLabel("Drop an audio file here")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 650;")

        subtitle = QLabel("WAV, MP3, M4A, AAC, FLAC or OGG")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("Subtitle")

        choose_button = QPushButton("Choose Audio")
        choose_button.setObjectName("PrimaryButton")
        choose_button.clicked.connect(self.choose_requested)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(choose_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        urls = event.mimeData().urls()
        if len(urls) == 1 and self._is_supported(urls[0].toLocalFile()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if len(urls) != 1:
            event.ignore()
            return

        local_path = urls[0].toLocalFile()
        if not self._is_supported(local_path):
            event.ignore()
            return

        self.file_dropped.emit(local_path)
        event.acceptProposedAction()

    @staticmethod
    def _is_supported(path: str) -> bool:
        return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS
