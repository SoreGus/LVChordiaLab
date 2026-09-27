from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from lv_chordia_lab.domain.chord_event import ChordEvent


class ChordInspector(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        caption = QLabel("Current chord")
        caption.setObjectName("Subtitle")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._chord = QLabel("—")
        self._chord.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._chord.setStyleSheet("font-size: 34px; font-weight: 750;")

        self._time = QLabel("")
        self._time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time.setObjectName("Subtitle")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)
        layout.addWidget(caption)
        layout.addWidget(self._chord)
        layout.addWidget(self._time)

    def set_event(self, event: ChordEvent | None) -> None:
        if event is None:
            self._chord.setText("—")
            self._time.clear()
            return

        self._chord.setText(event.chord)
        self._time.setText(f"{event.start_time:.1f} — {event.end_time:.1f} s")
