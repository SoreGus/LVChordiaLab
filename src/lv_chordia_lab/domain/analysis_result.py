from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lv_chordia_lab.domain.chord_event import ChordEvent


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    audio_path: Path
    duration: float
    chords: tuple[ChordEvent, ...]

    def chord_at(self, time_seconds: float) -> ChordEvent | None:
        for event in self.chords:
            if event.contains(time_seconds):
                return event
        return None
