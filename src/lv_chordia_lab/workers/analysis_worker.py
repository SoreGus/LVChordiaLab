from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from lv_chordia_lab.domain.analysis_result import AnalysisResult
from lv_chordia_lab.services.analysis_service import AnalysisService


class AnalysisWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)
    completed = Signal()

    def __init__(self, service: AnalysisService, audio_path: Path) -> None:
        super().__init__()
        self._service = service
        self._audio_path = audio_path

    @Slot()
    def run(self) -> None:
        try:
            result: AnalysisResult = self._service.analyze(self._audio_path)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.completed.emit()
