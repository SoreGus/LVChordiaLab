from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChordEvent:
    start_time: float
    end_time: float
    chord: str
    confidence: float | None = None

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def contains(self, time_seconds: float) -> bool:
        return self.start_time <= time_seconds < self.end_time
