from dataclasses import dataclass


@dataclass(frozen=True)
class TrackInfo:
    title: str
    artist: str
    duration_seconds: int

    @property
    def duration_mm_ss(self) -> str:
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
