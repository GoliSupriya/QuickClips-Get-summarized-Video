import os
import shutil
import uuid
from download_audio import extract_audio
from transcript import transcribe_audio
from timestamps import generate_transcript_with_timestamps
from summarize_content import extract_main_points
from SummarizedTimestamps import match_summary_to_timestamps
from summarized_video import create_summarized_video

def cleanup_files(files=None, dirs=None):
    """Safely delete files and directories."""
    files = files or []
    dirs = dirs or []

    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception as e:
            print(f"⚠️ Could not delete file {f}: {e}")

    for d in dirs:
        try:
            if os.path.exists(d):
                shutil.rmtree(d, ignore_errors=True)
        except Exception as e:
            print(f"⚠️ Could not delete directory {d}: {e}")


def summarize_video(video_path):
    """
    Full video summarization pipeline.
    Saves the output as downloads/summarized_video_<UUID>.mp4
    Returns the path to the summarized video if successful, else None.
    """
    if not video_path or not os.path.exists(video_path):
        print("❌ No video provided or file does not exist.")
        return None

    # Ensure downloads folder exists
    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)

    # Unique filenames to avoid overwriting
    unique_id = str(uuid.uuid4())[:8]
    output_video_path = os.path.join(downloads_dir, f"summarized_video_{unique_id}.mp4")
    audio_file = os.path.join(downloads_dir, f"audio_{unique_id}.wav")
    transcript_txt_file = os.path.join(downloads_dir, f"transcript_{unique_id}.txt")
    transcript_json_file = os.path.join(downloads_dir, f"transcript_{unique_id}.json")
    summary_file = os.path.join(downloads_dir, f"summary_{unique_id}.txt")
    timestamps_file = os.path.join(downloads_dir, f"summary_with_timestamps_{unique_id}.json")
    temp_clips_dir = os.path.join(downloads_dir, f"temp_clips_{unique_id}")
    os.makedirs(temp_clips_dir, exist_ok=True)

    try:
        # 1️⃣ Extract audio from video
        print("🎵 Extracting audio...")
        extract_audio(video_path, output_audio_path=audio_file)

        # 2️⃣ Transcribe audio to text
        print("📝 Transcribing audio...")
        transcribe_audio(audio_file, output_dir=downloads_dir, output_file=os.path.basename(transcript_txt_file))

        # 3️⃣ Generate transcript with timestamps
        print("⏱ Generating transcript with timestamps...")
        generate_transcript_with_timestamps(audio_file, output_file=transcript_json_file)

        # 4️⃣ Extract main points (summary)
        print("📝 Extracting main points from transcript...")
        extract_main_points(transcript_txt_file, output_file=summary_file,
                            max_length=200, min_length=50)

        # 5️⃣ Match summary sentences to timestamps
        print("🔗 Matching summary sentences with timestamps...")
        match_summary_to_timestamps(summary_file, transcript_json_file, output_file=timestamps_file)

        # 6️⃣ Create summarized video
        print("🎬 Creating summarized video...")
        output_video = create_summarized_video(video_path, timestamps_file, output_video_path, temp_clips_dir=temp_clips_dir)

        # Cleanup intermediate files
        video="downloads/video.mp4"
        cleanup_files(
            files=[audio_file, transcript_txt_file, transcript_json_file, summary_file, timestamps_file,video],
            dirs=[temp_clips_dir]
        )

        if output_video and os.path.exists(output_video):
            print(f"✅ Summarized video created at: {output_video}")
            return output_video
        else:
            print("⚠️ Summarized video could not be created.")
            return None

    except Exception as e:
        print(f"⚠️ Error while creating summarized video: {e}")
        return None
