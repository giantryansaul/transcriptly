import json
import os
import pathlib

from typing import List

from .transcribe_services.transcribe_service import TranscribeService
from .types import AudioInput, TranscriptionResult, Segment

import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

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

    def transcribe_single_audio_file(self, file_path, speaker=None) -> List[Segment]:
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
        return transcription.segments
    
    def transcribe_multiple_audio_files(self, audio_inputs: List[AudioInput]) -> List[Segment]:
        """
        Transcribes multiple audio files. The audio files are assumed to be
        from different speakers.

        Input:
            audio_inputs: List[AudioInput]

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
    
    def write_transcription_to_file(self, transcription_segments: List[Segment], output_file: str) -> None:
        logging.info(f'Writing transcript to {output_file}')
        with open(output_file, 'w') as f:
            for segment in transcription_segments:
                f.write(f'[{segment.start_time:9.2f}]{segment.speaker:>16}: {segment.text}\n')

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
    def get_speaker_from_file_path(file_path) -> str:
        filename = os.path.basename(file_path)
        name = filename.split("-", 1)[-1].rsplit(".", 1)[0].rsplit("_", 1)[0]
        return name


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=pathlib.Path, help="Input audio file, inputs JSON file, or directory. Speaker names are extracted from the file names for a directory.")
    parser.add_argument("speaker", type=str, help="Speaker name for a single audio file. Speaker names for multiple audio files are extracted from the file names.")
    args = parser.parse_args()
    input = args.input
    speaker = args.speaker

    transcription_service_name = os.environ.get("TRANSCRIPTION_SERVICE", "whisper")
    transcription_model_name = os.environ.get("TRANSCRIPTION_MODEL", "tiny")
    transcribe = Transcribe(
        service_name=transcription_service_name, 
        model_name=transcription_model_name
    )

    transcription = None
    if os.path.isfile(input):
        # If input is a json file, run multi-file transcription
        if input.endswith(".json"):
            logging.info(f'Input is a JSON file. Running multi-file transcription...')
            with open(input, "r") as f:
                audio_inputs = json.load(f)
            transcription = transcribe.transcribe_multiple_audio_files(audio_inputs)
        # If input is an audio file, run single-file transcription
        else:
            logging.info(f'Input is an audio file. Running single-file transcription...')
            transcription = transcribe.transcribe_single_audio_file(input, speaker)
    elif os.path.isdir(input):
        # If input is a directory, run multi-file transcription
        logging.info(f'Input is a directory. Running multi-file transcription...')
        file_list = [os.path.join(input, f) for f in os.listdir(input) if os.path.isfile(os.path.join(input, f))]
        audio_inputs = []
        for file_path in file_list:
            speaker = transcribe.get_speaker_from_file_path(file_path)
            audio_inputs.append(AudioInput(speaker, file_path))
        transcription = transcribe.transcribe_multiple_audio_files(audio_inputs)
    else:
        raise RuntimeError("Input parameter must be a file or directory")
    logging.info(f'Transcription complete.')

    transcribe.write_transcription_to_file(transcription)