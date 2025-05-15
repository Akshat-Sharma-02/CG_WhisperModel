# Whisper Transcription App

A simple app that records or uploads audio, transcribes it using OpenAI's Whisper model, and saves the results.

---

## How to Run This App

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

---

## Folder Structure

- `uploads/` – Stores all previously recorded audio files
- `cleaned_audio/` – Stores all cleaned audio processed for transcription
- `logs/` – Stores all transcribed text logs in `.json` format

> All folders are created automatically on first run.
