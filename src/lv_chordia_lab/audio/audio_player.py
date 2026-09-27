from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioPlayer(QObject):
    position_changed = Signal(float)
    duration_changed = Signal(float)
    playback_changed = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(1.0)

        self._player = QMediaPlayer(self)
        self._player.setAudioOutput(self._audio_output)

        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.errorOccurred.connect(self._on_error)

    @property
    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    @property
    def position(self) -> float:
        return self._player.position() / 1000.0

    @property
    def duration(self) -> float:
        return self._player.duration() / 1000.0

    def load(self, path: Path) -> None:
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(str(path)))

    def toggle(self) -> None:
        if self.is_playing:
            self._player.pause()
        else:
            self._player.play()

    def stop(self) -> None:
        self._player.stop()

    def seek(self, seconds: float) -> None:
        milliseconds = max(0, int(seconds * 1000))
        self._player.setPosition(milliseconds)

    def _on_position_changed(self, milliseconds: int) -> None:
        self.position_changed.emit(milliseconds / 1000.0)

    def _on_duration_changed(self, milliseconds: int) -> None:
        self.duration_changed.emit(milliseconds / 1000.0)

    def _on_playback_state_changed(
        self,
        state: QMediaPlayer.PlaybackState,
    ) -> None:
        self.playback_changed.emit(
            state == QMediaPlayer.PlaybackState.PlayingState
        )

    def _on_error(self, _error: QMediaPlayer.Error, message: str) -> None:
        if message:
            self.error_occurred.emit(message)
