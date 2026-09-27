from __future__ import annotations

from pathlib import Path
from typing import Protocol

from lv_chordia_lab.domain.analysis_result import AnalysisResult


class ChordRecognizer(Protocol):
    def analyze(self, audio_path: Path) -> AnalysisResult:
        """Analyze a local audio file and return time-aligned chord events."""

    def close(self) -> None:
        """Release resources owned by the recognizer."""
