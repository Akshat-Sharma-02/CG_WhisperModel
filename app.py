import os
import json
import datetime
import whisper
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import ffmpeg

app = Flask(__name__)
model = whisper.load_model("medium")  # More accurate, works well for Hindi

UPLOAD_DIR = 'uploads'
CLEAN_DIR = 'cleaned_audio'
LOG_DIR = 'logs'

for folder in [UPLOAD_DIR, CLEAN_DIR, LOG_DIR]:
    os.makedirs(folder, exist_ok=True)

def get_today_folder(base_path):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(base_path, today)
    os.makedirs(folder, exist_ok=True)
    return folder, today

def denoise_audio(input_path, output_path):
    (
        ffmpeg
        .input(input_path)
        .output(output_path, af='highpass=f=200, lowpass=f=3000, dynaudnorm', ac=1, ar='16000')
        .run(quiet=True, overwrite_output=True)
    )

def log_transcription(date_str, data):
    log_path = os.path.join(LOG_DIR, f"{date_str}.json")
    logs = []

    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)

    logs.append(data)

    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    file = request.files['audio']
    original_filename = secure_filename(file.filename)

    # Append timestamp to filename for uniqueness
    timestamp = datetime.datetime.now().strftime("%H%M%S%f")
    name, ext = os.path.splitext(original_filename)
    unique_filename = f"{name}_{timestamp}{ext}"

    upload_folder, date_str = get_today_folder(UPLOAD_DIR)
    clean_folder, _ = get_today_folder(CLEAN_DIR)

    raw_path = os.path.join(upload_folder, unique_filename)
    cleaned_path = os.path.join(clean_folder, f"cleaned_{unique_filename}.wav")
    file.save(raw_path)

    try:
        denoise_audio(raw_path, cleaned_path)
        result = model.transcribe(cleaned_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    transcript_data = {
        "filename": unique_filename,
        "date": date_str,
        "language": result["language"],
        "transcript": result["text"]
    }

    log_transcription(date_str, transcript_data)

    return jsonify(transcript_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
