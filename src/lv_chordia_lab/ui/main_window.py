from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from lv_chordia_lab.audio.audio_file import AudioFile, SUPPORTED_EXTENSIONS
from lv_chordia_lab.audio.audio_player import AudioPlayer
from lv_chordia_lab.config.settings import Settings
from lv_chordia_lab.domain.analysis_result import AnalysisResult
from lv_chordia_lab.inference.lv_chordia_recognizer import LVChordiaRecognizer
from lv_chordia_lab.services.analysis_service import AnalysisService
from lv_chordia_lab.ui.analysis_status import AnalysisStatus
from lv_chordia_lab.ui.audio_header import AudioHeader
from lv_chordia_lab.ui.chord_inspector import ChordInspector
from lv_chordia_lab.ui.drop_area import DropArea
from lv_chordia_lab.ui.playback_controls import PlaybackControls
from lv_chordia_lab.ui.timeline_view import TimelineView
from lv_chordia_lab.workers.analysis_worker import AnalysisWorker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)

        self._settings = settings
        self._recognizer = LVChordiaRecognizer(
            chord_dict=settings.chord_dict,
            device=settings.device,
        )
        self._analysis_service = AnalysisService(self._recognizer)
        self._player = AudioPlayer(self)

        self._analysis_thread: QThread | None = None
        self._analysis_worker: AnalysisWorker | None = None
        self._result: AnalysisResult | None = None
        self._audio_file: AudioFile | None = None

        self._stack = QStackedWidget()
        self._drop_area = DropArea()
        self._analysis_status = AnalysisStatus()
        self._result_page = self._build_result_page()

        self._stack.addWidget(self._drop_area)
        self._stack.addWidget(self._analysis_status)
        self._stack.addWidget(self._result_page)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(18)

        title = QLabel("LV Chordia Lab")
        title.setObjectName("Title")

        subtitle = QLabel(
            f"Local chord recognition · {settings.chord_dict} vocabulary"
        )
        subtitle.setObjectName("Subtitle")

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(4)
        root.addWidget(self._stack, stretch=1)

        self.setCentralWidget(container)
        self.resize(1100, 680)
        self.setMinimumSize(820, 560)
        self.setWindowTitle("LV Chordia Lab")

        self._connect_signals()
        self._stack.setCurrentWidget(self._drop_area)

    def closeEvent(self, event) -> None:
        self._player.stop()
        self._analysis_service.close()
        event.accept()

    def _build_result_page(self) -> QWidget:
        page = QWidget()

        self._audio_header = AudioHeader()
        self._playback_controls = PlaybackControls()
        self._timeline = TimelineView()
        self._inspector = ChordInspector()

        timeline_card = QFrame()
        timeline_card.setObjectName("Card")

        timeline_layout = QVBoxLayout(timeline_card)
        timeline_layout.setContentsMargins(18, 18, 18, 18)
        timeline_layout.setSpacing(14)
        timeline_layout.addWidget(self._playback_controls)
        timeline_layout.addWidget(self._timeline)

        inspector_card = QFrame()
        inspector_card.setObjectName("Card")

        inspector_layout = QVBoxLayout(inspector_card)
        inspector_layout.setContentsMargins(18, 12, 18, 12)
        inspector_layout.addWidget(self._inspector)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(self._audio_header)
        layout.addWidget(timeline_card, stretch=1)
        layout.addWidget(inspector_card)

        return page

    def _connect_signals(self) -> None:
        self._drop_area.choose_requested.connect(self._choose_audio)
        self._drop_area.file_dropped.connect(self._load_audio_path)

        self._audio_header.open_button.clicked.connect(self._choose_audio)

        self._playback_controls.toggle_requested.connect(self._player.toggle)
        self._playback_controls.seek_requested.connect(self._player.seek)

        self._timeline.seek_requested.connect(self._player.seek)
        self._timeline.event_selected.connect(self._inspector.set_event)

        self._player.position_changed.connect(self._playback_controls.set_position)
        self._player.position_changed.connect(self._timeline.set_position)
        self._player.position_changed.connect(self._update_current_chord)
        self._player.duration_changed.connect(self._on_player_duration_changed)
        self._player.playback_changed.connect(self._playback_controls.set_playing)
        self._player.error_occurred.connect(self._show_player_error)

    def _choose_audio(self) -> None:
        patterns = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS))
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Audio",
            "",
            f"Audio Files ({patterns});;All Files (*)",
        )

        if path:
            self._load_audio_path(path)

    def _load_audio_path(self, path: str) -> None:
        if self._analysis_thread is not None:
            return

        try:
            audio_file = AudioFile.from_path(path)
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Audio", str(exc))
            return

        self._audio_file = audio_file
        self._result = None
        self._player.stop()

        self._analysis_status.set_filename(audio_file.name)
        self._stack.setCurrentWidget(self._analysis_status)
        self._start_analysis(audio_file.path)

    def _start_analysis(self, path: Path) -> None:
        thread = QThread(self)
        worker = AnalysisWorker(self._analysis_service, path)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._analysis_finished)
        worker.failed.connect(self._analysis_failed)
        worker.completed.connect(thread.quit)
        worker.completed.connect(worker.deleteLater)
        thread.finished.connect(self._analysis_thread_finished)
        thread.finished.connect(thread.deleteLater)

        self._analysis_thread = thread
        self._analysis_worker = worker

        thread.start()

    def _analysis_finished(self, result: object) -> None:
        if not isinstance(result, AnalysisResult):
            self._analysis_failed("Unexpected analysis result.")
            return

        self._result = result
        self._player.load(result.audio_path)

        self._audio_header.set_audio(result.audio_path.name, result.duration)
        self._playback_controls.set_duration(result.duration)
        self._playback_controls.set_position(0.0)
        self._timeline.set_result(result)
        self._timeline.set_position(0.0)
        self._inspector.set_event(result.chord_at(0.0))

        self._stack.setCurrentWidget(self._result_page)

    def _analysis_failed(self, message: str) -> None:
        logger.error("Analysis failed: %s", message)
        self._stack.setCurrentWidget(self._drop_area)
        QMessageBox.critical(
            self,
            "Analysis Failed",
            message or "The audio could not be analyzed.",
        )

    def _analysis_thread_finished(self) -> None:
        self._analysis_thread = None
        self._analysis_worker = None

    def _on_player_duration_changed(self, seconds: float) -> None:
        if seconds <= 0:
            return

        self._audio_header.set_duration(seconds)
        self._playback_controls.set_duration(seconds)

    def _update_current_chord(self, seconds: float) -> None:
        if self._result is None:
            self._inspector.set_event(None)
            return

        self._inspector.set_event(self._result.chord_at(seconds))

    def _show_player_error(self, message: str) -> None:
        QMessageBox.warning(self, "Playback Error", message)
