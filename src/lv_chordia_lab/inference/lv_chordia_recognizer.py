from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from lv_chordia_lab.domain.analysis_result import AnalysisResult
from lv_chordia_lab.domain.chord_event import ChordEvent
from lv_chordia_lab.inference.inference_error import InferenceError

logger = logging.getLogger(__name__)


class LVChordiaRecognizer:
    def __init__(
        self,
        chord_dict: str = "submission",
        device: str = "auto",
    ) -> None:
        self._chord_dict = chord_dict
        self._device = device

    def analyze(self, audio_path: Path) -> AnalysisResult:
        if not audio_path.exists() or not audio_path.is_file():
            raise InferenceError(
                f"Audio file does not exist: {audio_path}"
            )

        try:
            from lv_chordia.chord_recognition import chord_recognition

            logger.info(
                "Running lv-chordia with chord dictionary: %s",
                self._chord_dict,
            )

            raw_events = chord_recognition(
                audio_path=str(audio_path),
                chord_dict_name=self._chord_dict,
            )

        except ImportError as exc:
            logger.exception("Failed to import lv-chordia")
            raise InferenceError(
                f"lv-chordia could not be imported: {exc}"
            ) from exc

        except Exception as exc:
            logger.exception("lv-chordia inference failed")
            raise InferenceError(
                f"Chord recognition failed: {exc}"
            ) from exc

        chords = tuple(
            self._parse_event(item)
            for item in raw_events
        )

        duration = max(
            (event.end_time for event in chords),
            default=0.0,
        )

        return AnalysisResult(
            audio_path=audio_path,
            duration=duration,
            chords=chords,
        )

    def close(self) -> None:
        pass

    @staticmethod
    def _parse_event(item: dict[str, Any]) -> ChordEvent:
        try:
            start_time = float(item["start_time"])
            end_time = float(item["end_time"])
            chord = str(item["chord"])

        except (KeyError, TypeError, ValueError) as exc:
            raise InferenceError(
                f"Invalid lv-chordia event: {item!r}"
            ) from exc

        confidence_value = item.get("confidence")

        confidence = (
            float(confidence_value)
            if confidence_value is not None
            else None
        )

        return ChordEvent(
            start_time=start_time,
            end_time=end_time,
            chord=chord,
            confidence=confidence,
        )