import os
import subprocess
from pydub import AudioSegment

def extract_audio(video_path, output_audio_path="extracted_audio.wav"):
    try:
        if not os.path.exists(video_path):
            print(f"❌ Error: Video file not found -> {video_path}")
            return None

        video_path = os.path.abspath(video_path)
        output_audio_path = os.path.abspath(output_audio_path)
        temp_audio = os.path.abspath("temp_audio.mp3")

        # ✅ Run ffmpeg to check if audio exists
        probe = subprocess.run(
            ["ffmpeg", "-i", video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if "Audio:" not in probe.stderr.decode():
            print("⚠️ No audio stream found in this video!")
            return None

        # ✅ Extract audio
        result = subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", temp_audio, "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            print("❌ FFmpeg extraction error:", result.stderr.decode())
            return None

        audio = AudioSegment.from_file(temp_audio, format="mp3")
        audio.export(output_audio_path, format="wav")
        os.remove(temp_audio)

        print(f"✅ Audio extracted successfully: {output_audio_path}")
        return output_audio_path

    except Exception as e:
        print("❌ Exception:", e)
        return None


