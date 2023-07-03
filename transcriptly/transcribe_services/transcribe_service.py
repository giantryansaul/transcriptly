from ..types import TranscriptionResult


class TranscribeService:
    def __init__(self):
        raise NotImplementedError("TranscribeService class not implemented")

    def transcribe(self, file_path) -> TranscriptionResult:
        raise NotImplementedError("transcribe method not implemented")


