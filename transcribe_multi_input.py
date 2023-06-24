import os
import glob
import argparse
import datetime
import logging

import whisper

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_speaker(path):
    filename = os.path.basename(path)
    name = filename.split("-", 1)[-1].rsplit(".", 1)[0].rsplit("_", 1)[0]
    logging.info(f"Speaker {name} extracted from filename {filename}")
    return name

def transcribe(path, transcription_model_type="tiny"):
    whisper_model = whisper.load_model(transcription_model_type)
    logging.info(f"Transcribing {path} with \"{transcription_model_type}\" whisper model...")
    result = whisper_model.transcribe(
        path, verbose=False,
        no_speech_threshold=0.275, 
        logprob_threshold=None, 
        condition_on_previous_text=False
    )
    return result

def remove_duplicates(segments):
    # iterate through the segments and remove when the text in the next segment is the same as the previous segment
    # this is a hack to remove duplicate segments that whisper sometimes produces
    for i in range(len(segments)-1, 0, -1):
        if segments[i]["text"] == segments[i-1]["text"]:
            del segments[i]
    return segments
        
def add_speaker_to_segments(speaker, segments):
    for i in range(len(segments)):
        segments[i]["speaker"] = speaker
    return segments

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file to process")
    args = parser.parse_args()
    directory = args.path
    transcription_model = os.environ.get("TRANSCRIPTION_MODEL", "tiny")

    file_list = glob.glob(os.path.join(directory, "*.ogg"))
    logging.info(f'Transcribing {len(file_list)} files: {file_list}')

    transcript_segments = []
    results = []

    for file in file_list:
        speaker = get_speaker(file)
        result = transcribe(file, transcription_model)
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


