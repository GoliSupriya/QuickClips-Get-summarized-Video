import os
import torch
import whisper

def transcribe_audio(audio_file, output_dir="downloads", output_file="transcript.txt"):
    """
    Transcribe audio to text and save as transcript.txt in downloads folder.
    """
    if not os.path.exists(audio_file):
        print(f"Error: {audio_file} not found.")
        return None

    # Create downloads folder if not exists
    os.makedirs(output_dir, exist_ok=True)

    # Load Whisper model (choose from: tiny, base, small, medium, large)
    print("Loading Whisper model...")
    model = whisper.load_model("base")  # "tiny" is faster, "base" is balanced

    # Transcribe
    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)

    transcript_text = result["text"]

    # Save transcript
    transcript_path = os.path.join(output_dir, output_file)
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    print(f"Transcript saved at {transcript_path}")
    return transcript_path


