import whisper

from ..data_types import TranscriptionResult, Segment
from .transcribe_service import TranscribeService

class WhisperTranscribe(TranscribeService):
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.whisper_model = whisper.load_model(self.model_name)
        self.no_speech_threshold = kwargs.get("no_speech_threshold", 0.275)
        self.logprob_threshold = kwargs.get("logprob_threshold", None)
        self.condition_on_previous_text = kwargs.get("condition_on_previous_text", False)

    def transcribe(self, file_path, verbose=False) -> TranscriptionResult:
        whisper_result = self.whisper_model.transcribe(
            file_path, 
            verbose=verbose,
            no_speech_threshold=self.no_speech_threshold, 
            logprob_threshold=self.logprob_threshold, 
            condition_on_previous_text=self.condition_on_previous_text
        )
        result = TranscriptionResult()
        segments = []
        for segment in whisper_result["segments"]:
            segments.append(Segment(segment["text"], segment["start"], segment["end"]))
        result.segments = segments
        result.text = whisper_result["text"]
        result.audio_file_path = file_path
        return result