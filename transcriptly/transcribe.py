from .transcribe_services.transcribe_service import TranscribeService


class Transcribe:
    service_name: str
    model_name: str
    transcription_service: TranscribeService

    def __init__(self, service_name, **kwargs):
        self.service_name = service_name
        
        if "model_name" in kwargs and kwargs.get("model_name") != "":
            self.model_name = kwargs["model_name"]

        if self.service_name == "whisper":
            from .transcribe_services.whisper_service import WhisperTranscribe

            if self.model_name == None:
                raise RuntimeError("Whisper model name must be specified")
            
            self.transcription_service = WhisperTranscribe(self.model_name)

    def transcribe(self, file_path):
        return self.transcription_service.transcribe(file_path)


class MultiInputTranscription:
    audio_file_paths: list
    segments: list
    results: list
    

class SingleInputTranscription:
    audio_file_path: str
    transcription: str


class TranscribeUtils:
    @staticmethod
    def remove_duplicates(segments):
        for i in range(len(segments)-1, 0, -1):
            if segments[i]["text"] == segments[i-1]["text"]:
                del segments[i]
        return segments
    
class MultiInputTranscribeUtils:
    @staticmethod
    def get_speaker(path):
        filename = os.path.basename(path)
        name = filename.split("-", 1)[-1].rsplit(".", 1)[0].rsplit("_", 1)[0]
        return name
    
    @staticmethod
    def add_speaker_to_segments(speaker, segments):
        for i in range(len(segments)):
            segments[i]["speaker"] = speaker
        return segments


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

    now = datetime.datetime.now()
    date_string = now.strftime("%Y%m%d%H%M%S")
    
    transcript_file_name = f'{directory}/transcript-{date_string}.txt'
    logging.info(f'Writing transcript to {transcript_file_name}')
    with open(transcript_file_name, 'w') as f:
        for segment in sorted_segments:
            f.write(f'[{segment["start"]:9.2f}] {segment["speaker"]:>16}: {segment["text"]}\n')