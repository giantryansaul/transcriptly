from dataclasses import dataclass
from typing import List

@dataclass
class Segment:
    text: str
    start_time: float
    end_time: float
    speaker: str = None

@dataclass
class TranscriptionResult:
    audio_file_path: str = None
    segments: List[Segment] = None
    text: str = None