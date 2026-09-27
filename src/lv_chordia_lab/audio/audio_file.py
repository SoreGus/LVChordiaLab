from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".wav",
}


@dataclass(frozen=True, slots=True)
class AudioFile:
    path: Path

    @classmethod
    def from_path(cls, path: str | Path) -> "AudioFile":
        resolved = Path(path).expanduser().resolve()

        if not resolved.exists() or not resolved.is_file():
            raise ValueError("The selected audio file does not exist.")

        if resolved.suffix.lower() not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise ValueError(f"Unsupported audio format. Supported: {supported}")

        return cls(path=resolved)

    @property
    def name(self) -> str:
        return self.path.name
