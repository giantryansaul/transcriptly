import datetime

import whisper
from blinker import Namespace
from flask import Flask, request

my_signals = Namespace()
audio_uploaded = my_signals.signal("audio_uploaded")
app = Flask(__name__)

def datetime_stamp():
    return datetime.datetime.now().strftime("%y%m%d%H%m%S")

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        f = request.files['file']
        uploaded_file_path = f'./uploads/uploaded_file-{datetime_stamp()}.txt'
        f.save(uploaded_file_path)
        print(f"[{datetime_stamp()}] File uploaded to: {uploaded_file_path}")
        audio_uploaded.send(app, path=uploaded_file_path)
        return "File uploaded successfully"

@audio_uploaded.connect
def transcribe(app, path):
    model = whisper.load_model("small")
    result = model.transcribe(path)
    print(f"[{datetime_stamp()}] Transcription Sample -->{result['text'][:100]}")
    transcription_path = f"transcriptions/transcription-{datetime_stamp()}.txt"
    with open (transcription_path, "w") as f:
        f.write(result["text"])
    print(f"[{datetime_stamp()}] Transcription saved to: {transcription_path}")