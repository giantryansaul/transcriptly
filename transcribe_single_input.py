import os
import glob
import argparse
import datetime
import pickle

import whisper

transcription_model = whisper.load_model("small")

def transcribe(path):
    print(f"Transcribing {path}...")
    result = transcription_model.transcribe(
        path, verbose=False,
        no_speech_threshold=0.275, 
        logprob_threshold=None, 
        condition_on_previous_text=False
    )
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the file to process")
    parser.add_argument('-r', '--resume', action='store_true', help='Resume from cache')
    args = parser.parse_args()
    file_path = args.path
    resume_from_cached = args.resume

    if not resume_from_cached:
        print(f'Transcribing file: {file_path}')

        transcript_segments = []

        result = transcribe(file_path)
        print(f'Sample text: {result["text"][:100]}')

        with open('cache/result.pkl', 'wb') as f:
            pickle.dump(result, f)

    else:
        with open('cache/result.pkl', 'rb') as f:
            result = pickle.load(f)

    now = datetime.datetime.now()
    date_string = now.strftime("%Y%m%d%H%M%S")
    transcript_file_name = f'transcriptions/transcript-{date_string}.txt'

    print(f'Writing transcript to {transcript_file_name}')
    with open(transcript_file_name, 'w') as f:
        for segment in result["segments"]:
            f.write(f'[{segment["text"]}\n')

