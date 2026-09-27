from __future__ import annotations

from pathlib import Path

from lv_chordia_lab.domain.analysis_result import AnalysisResult
from lv_chordia_lab.inference.chord_recognizer import ChordRecognizer


class AnalysisService:
    def __init__(self, recognizer: ChordRecognizer) -> None:
        self._recognizer = recognizer

    def analyze(self, audio_path: Path) -> AnalysisResult:
        return self._recognizer.analyze(audio_path)

    def close(self) -> None:
        self._recognizer.close()
