from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QWidget


class PlaybackControls(QWidget):
    toggle_requested = Signal()
    seek_requested = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._duration = 0.0
        self._updating_slider = False

        self._play_button = QPushButton("▶")
        self._play_button.setFixedWidth(48)
        self._play_button.clicked.connect(self.toggle_requested)

        self._position_label = QLabel("00:00.0")
        self._position_label.setMinimumWidth(62)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 1000)
        self._slider.sliderReleased.connect(self._slider_released)

        self._duration_label = QLabel("00:00.0")
        self._duration_label.setMinimumWidth(62)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self._play_button)
        layout.addWidget(self._position_label)
        layout.addWidget(self._slider, stretch=1)
        layout.addWidget(self._duration_label)

    def set_playing(self, playing: bool) -> None:
        self._play_button.setText("❚❚" if playing else "▶")

    def set_duration(self, seconds: float) -> None:
        self._duration = max(0.0, seconds)
        self._duration_label.setText(self._format_time(self._duration))

    def set_position(self, seconds: float) -> None:
        seconds = max(0.0, seconds)
        self._position_label.setText(self._format_time(seconds))

        if self._duration <= 0 or self._slider.isSliderDown():
            return

        self._updating_slider = True
        ratio = min(1.0, seconds / self._duration)
        self._slider.setValue(round(ratio * self._slider.maximum()))
        self._updating_slider = False

    def _slider_released(self) -> None:
        if self._updating_slider or self._duration <= 0:
            return

        ratio = self._slider.value() / self._slider.maximum()
        self.seek_requested.emit(ratio * self._duration)

    @staticmethod
    def _format_time(seconds: float) -> str:
        total_tenths = max(0, int(seconds * 10))
        total_seconds, tenths = divmod(total_tenths, 10)
        minutes, second = divmod(total_seconds, 60)
        hours, minute = divmod(minutes, 60)

        if hours:
            return f"{hours:02d}:{minute:02d}:{second:02d}.{tenths}"
        return f"{minute:02d}:{second:02d}.{tenths}"
