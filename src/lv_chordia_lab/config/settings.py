from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    device: str
    chord_dict: str
    log_level: str

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()

        return cls(
            device=os.getenv("LV_CHORDIA_DEVICE", "auto").strip() or "auto",
            chord_dict=os.getenv("LV_CHORDIA_CHORD_DICT", "submission").strip()
            or "submission",
            log_level=os.getenv("LV_CHORDIA_LOG_LEVEL", "INFO").strip().upper()
            or "INFO",
        )
