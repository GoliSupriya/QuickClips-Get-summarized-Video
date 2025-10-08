import whisper
import json
import os

def generate_transcript_with_timestamps(audio_file, output_file="downloads/transcript.json"):
    try:
        model = whisper.load_model("base")  # you can use "small" / "medium" for better accuracy
        result = model.transcribe(audio_file, verbose=True)

        transcript_data = []
        for seg in result["segments"]:
            transcript_data.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=4)

        print(f"✅ Transcript with timestamps saved at {output_file}")
        return transcript_data
    except Exception as e:
        print(f"⚠️ Error generating transcript: {e}")
        return None



