import json
import os
import subprocess


def time_str_to_seconds(time_str):
    """Convert 'start --> end' style timestamp to float seconds."""
    parts = time_str.split("-->")
    start = float(parts[0].strip())
    end = float(parts[1].strip())
    return start, end


def cut_clip(video_file, start, end, clip_path):
    """Try fast cut for video, but always re-encode audio for clarity."""

    # --- Fast cut: video copy, audio re-encode ---
    cmd_fast = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", video_file,
        "-c:v", "copy",            # fast video copy
        "-c:a", "aac",             # re-encode audio for clarity
        "-b:a", "192k",            # good audio quality
        clip_path
    ]
    subprocess.run(cmd_fast, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # If clip is valid, return success
    if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1000:
        return True

    # --- Fallback: re-encode both video + audio ---
    cmd_reencode = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", video_file,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        clip_path
    ]
    subprocess.run(cmd_reencode, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return os.path.exists(clip_path) and os.path.getsize(clip_path) > 1000


def create_summarized_video(video_file, timestamps_file, output_file="downloads/summarized_video.mp4"):
    try:
        # Load timestamps
        with open(timestamps_file, "r", encoding="utf-8") as f:
            summary_data = json.load(f)

        clips_dir = "downloads/temp_clips"
        os.makedirs(clips_dir, exist_ok=True)
        clip_files = []

        # Generate clips
        for i, item in enumerate(summary_data):
            start, end = time_str_to_seconds(item["timestamp"])
            if end > start:
                clip_path = os.path.join(clips_dir, f"clip_{i+1}.mp4")
                if cut_clip(video_file, start, end, clip_path):
                    clip_files.append(clip_path)

        if not clip_files:
            print("⚠️ No valid clips were created. Check timestamps.")
            return None

        # Write list of clips for concatenation
        list_file = os.path.join(clips_dir, "clips_list.txt")
        with open(list_file, "w") as f:
            for clip in clip_files:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        # Concatenate all clips
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_file
        ]
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"✅ Summarized video saved at: {output_file}")
        return output_file

    except Exception as e:
        print(f"⚠️ Error while creating summarized video: {e}")
        return None


if __name__ == "__main__":
    video_path = "downloads/video.mp4"  # your input video
    timestamps_path = "downloads/summary_with_timestamps.json"  # your JSON file
    output_video_path = "downloads/summarized_video.mp4"

    create_summarized_video(video_path, timestamps_path, output_video_path)
