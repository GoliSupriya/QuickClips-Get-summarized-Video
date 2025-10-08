import os
from moviepy.editor import VideoFileClip
from download import download_youtube_video
from transcript import transcribe_audio
from download_audio import extract_audio
from summarize_content import extract_main_points
from timestamps import generate_transcript_with_timestamps
from SummarizedTimestamps import match_summary_to_timestamps
from summarized_video import create_summarized_video

def run_pipeline(yturl=None, video_path=None, output_type="text"):
    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)

    video_file = os.path.join(downloads_dir, "video.mp4")
    audio_file = os.path.join(downloads_dir, "output_audio.wav")
    transcript_path = os.path.join(downloads_dir, "transcript.json")
    output_summary_path = os.path.join(downloads_dir, "main_points_summary.txt")
    output_file = os.path.join(downloads_dir, "summary_with_timestamps.json")
    output_video_path = os.path.join(downloads_dir, "summarized_video.mp4")

    try:
        # --- Download or use uploaded video ---
        if yturl:
            download_youtube_video(yturl, video_file)
        elif video_path:
            video_file = video_path
        else:
            return {"status": "error", "message": "No video or URL provided."}

        # --- Extract audio safely ---
        try:
            clip = VideoFileClip(video_file)
            if clip.audio is None:
                return {"status": "error", "message": "No audio track found in video."}
            clip.audio.write_audiofile(audio_file)
        except Exception as e:
            return {"status": "error", "message": f"Audio extraction failed: {str(e)}"}

        # --- Transcribe audio ---
        try:
            transcribe_audio(audio_file)
        except Exception as e:
            return {"status": "error", "message": f"Audio transcription failed: {str(e)}"}

        # --- Generate timestamps ---
        try:
            generate_transcript_with_timestamps(audio_file, transcript_path)
        except Exception as e:
            return {"status": "error", "message": f"Timestamp generation failed: {str(e)}"}

        # --- Summarize content ---
        try:
            extract_main_points(transcript_path, output_file=output_summary_path)
        except Exception as e:
            return {"status": "error", "message": f"Content summarization failed: {str(e)}"}

        # --- Match summary to timestamps ---
        try:
            match_summary_to_timestamps(output_summary_path, transcript_path, output_file)
        except Exception as e:
            return {"status": "error", "message": f"Matching summary to timestamps failed: {str(e)}"}

        # --- Create summarized video if requested ---
        if output_type == "video":
            try:
                create_summarized_video(video_file, output_file, output_video_path)
                return {"status": "success", "video": output_video_path}
            except Exception as e:
                return {"status": "error", "message": f"Video creation failed: {str(e)}"}
        else:
            with open(output_summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read()
            return {"status": "success", "summary": summary_text}

    finally:
        # Cleanup intermediate files (keep final video if exists)
        for f in [audio_file, transcript_path, output_summary_path, output_file]:
            if os.path.exists(f):
                os.remove(f)
