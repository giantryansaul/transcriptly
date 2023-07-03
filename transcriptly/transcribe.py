import os

from typing import List

from .transcribe_services.transcribe_service import TranscribeService
from .types import TranscriptionResult, Segment


class AudioInput:
    speaker: str
    file_path: str

class Transcribe:
    service_name: str
    model_name: str
    transcription_service: TranscribeService
    remove_duplicates: bool = False

    def __init__(self, service_name, **kwargs):
        self.service_name: str = service_name
        
        if "model_name" in kwargs and kwargs.get("model_name") != "":
            self.model_name = kwargs["model_name"]
        else:
            raise RuntimeError("Model name must be specified")
        
        if "remove_duplicates" in kwargs and kwargs.get("remove_duplicates") == True:
            self.remove_duplicates = True

        # Whisper Service
        if self.service_name == "whisper":
            from .transcribe_services.whisper_service import WhisperTranscribe

            if self.model_name == None:
                raise RuntimeError("Whisper model name must be specified")
            
            self.transcription_service = WhisperTranscribe(self.model_name)

    def transcribe_single_audio_file(self, file_path, speaker=None):
        """
        Transcribes a single audio file

        Input:
            file_path: str
            speaker: str

        Returns: TranscriptionResult
        """
        transcription = self.transcription_service.transcribe(file_path)
        if self.remove_duplicates:
            transcription.segments = self.remove_duplicates_from_segments(transcription.segments)
        if speaker != None:
            transcription.segments = self.add_speaker_to_segments(speaker, transcription.segments)
        return transcription
    
    def transcribe_multiple_audio_files(self, audio_inputs: List[AudioInput]):
        """
        Transcribes multiple audio files. The audio files are assumed to be
        from different speakers.

        Input:
            audio_input: List[AudioInput]

        Returns: List[Segment]
        """

        # TODO: Break this out so that I can multi-thread it and save progress if stopped.
        transcriptions = []
        for ainput in audio_inputs:
            logging.info(f"Transcribing {ainput.file_path} with Speaker as {ainput.speaker}...")
            transcription = self.transcribe_single_audio_file(ainput.file_path, ainput.speaker)

        # TODO: Start here when all transcriptions above are completed.
        transcript_segments = []
        for transcription in transcriptions:
            logging.info(f'{transcription.speaker} sample text: {transcription.text[:100]}')
            segments = transcription.segments
            transcript_segments.extend(segments)

        sorted_segments = sorted(transcript_segments, key=lambda k: k['start'])
        counter = 0 
        for segment in sorted_segments:
            counter += 1
            logging.info(f'[{segment["start"]:9.2f}] {segment["speaker"]:>16}: {segment["text"]}')
            if counter > 200:
                break
        
        return sorted_segments

    @staticmethod
    def remove_duplicates_from_segments(segments: List[Segment]) -> List[Segment]:
        """
        Removes duplicate segments from a list of segments. This is helpful for
        Whisper transcriptions, which sometimes return duplicate segments.
        """
        for i in range(len(segments)-1, 0, -1):
            if segments[i].text == segments[i-1].text:
                del segments[i]
        return segments

    @staticmethod
    def add_speaker_to_segments(speaker: str, segments: List[Segment]) -> List[Segment]:
        """
        Adds a speaker to a list of segments.
        """
        for i in range(len(segments)):
            segments[i].speaker = speaker
        return segments
    
    @staticmethod
    def get_speaker_from_file_path(file_path):
        filename = os.path.basename(file_path)
        name = filename.split("-", 1)[-1].rsplit(".", 1)[0].rsplit("_", 1)[0]
        return name

    
class MultiInputTranscribeUtils:
    @staticmethod
    def get_speaker(path):
        filename = os.path.basename(path)
        name = filename.split("-", 1)[-1].rsplit(".", 1)[0].rsplit("_", 1)[0]
        return name


if __name__ == "__main__":
    import argparse
    import os
    import glob
    import datetime
    import logging

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file to process")
    args = parser.parse_args()
    directory = args.path

    transcription_service_name = os.environ.get("TRANSCRIPTION_SERVICE", "whisper")
    transcription_model_name = os.environ.get("TRANSCRIPTION_MODEL", "tiny")
    transcribe = Transcribe(
        service_name=transcription_service_name, 
        model_name=transcription_model_name
    )

    #### Moving this section to classes ####
    file_list = glob.glob(os.path.join(directory, "*.ogg"))
    logging.info(f'Transcribing {len(file_list)} files: {file_list}')

    transcript_segments = []
    results = []

    for file_path in file_list:
        speaker = get_speaker(file)
        logging.info(f"Speaker {speaker} extracted from {file_path}")
        result = transcribe(file_path, transcription_model)
        logging.info(f'{speaker} sample text: {result["text"][:100]}')
        segments = result["segments"]
        segments = remove_duplicates(segments)
        segments = add_speaker_to_segments(speaker, segments)
        transcript_segments.extend(segments)

    logging.info(f'Sorting transcript segments by start position...')
    sorted_segments = sorted(transcript_segments, key=lambda k: k['start'])

    counter = 0 # why is this here?
    for segment in sorted_segments:
        counter += 1
        logging.info(f'[{segment["start"]:9.2f}] {segment["speaker"]:>16}: {segment["text"]}')
        if counter > 200:
            break
    #########################################

    now = datetime.datetime.now()
    date_string = now.strftime("%Y%m%d%H%M%S")
    
    transcript_file_name = f'{directory}/transcript-{date_string}.txt'
    logging.info(f'Writing transcript to {transcript_file_name}')
    with open(transcript_file_name, 'w') as f:
        for segment in sorted_segments:
            f.write(f'[{segment["start"]:9.2f}] {segment["speaker"]:>16}: {segment["text"]}\n')