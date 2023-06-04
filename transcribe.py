import os
import glob
import argparse
import datetime

import whisper

transcription_model = whisper.load_model("tiny")

def get_speaker(path):
    filename = os.path.basename(path)
    name = filename.split("-", 1)[-1].rsplit(".", 1)[0].rsplit("_", 1)[0]
    print(f"Speaker {name} extracted from filename {filename}")
    return name

def transcribe(path):
    print(f"Transcribing {path}...")
    result = transcription_model.transcribe(
        path, verbose=False,
        no_speech_threshold=0.275, 
        logprob_threshold=None, 
        condition_on_previous_text=False
    )
    return result
        
def add_speaker_to_segments(speaker, segments):
    for i in range(len(segments)):
        segments[i]["speaker"] = speaker
    return segments

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file to process")
    args = parser.parse_args()
    directory = args.path

    file_list = glob.glob(os.path.join(directory, "*.ogg"))
    print(f'Transcribing {len(file_list)} files: {file_list}')

    transcript_segments = []
    results = []

    for file in file_list:
        speaker = get_speaker(file)
        result = transcribe(file)
        print(f'{speaker} sample text: {result["text"][:100]}')
        modified_segements = add_speaker_to_segments(speaker, result["segments"])
        transcript_segments.extend(modified_segements)

    print(f'Sorting transcript segments by start position...')
    sorted_segments = sorted(transcript_segments, key=lambda k: k['start'])

    counter = 0
    for segment in sorted_segments:
        counter += 1
        print(f'[{segment["start"]:9.2f}] {segment["speaker"]:>16}: {segment["text"]}')
        if counter > 200:
            break

    now = datetime.datetime.now()
    date_string = now.strftime("%Y%m%d%H%M%S")
    
    transcript_file_name = f'{directory}/transcript-{date_string}.txt'
    print(f'Writing transcript to {transcript_file_name}')
    with open(transcript_file_name, 'w') as f:
        for segment in sorted_segments:
            f.write(f'[{segment["start"]:9.2f}] {segment["speaker"]:>16}: {segment["text"]}\n')


