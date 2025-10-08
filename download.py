import yt_dlp
import os

def download_youtube_video(url, path="downloads"):
    """
    Downloads a YouTube video with audio included using yt-dlp
    and saves it as video.mp4 only.
    Returns the saved file path if successful, else None.
    """
    # Ensure downloads folder exists
    os.makedirs(path, exist_ok=True)

    output_path = os.path.join(path, "video.mp4")

    ydl_opts = {
        'outtmpl': os.path.join(path, 'video.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': False,
        'ignoreerrors': True,
        'keepvideo': False,
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4',
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if info_dict:
                print(f"✅ Title: {info_dict.get('title')}")
                print(f"🎬 Saved as {output_path}")
                return output_path  # ✅ return the file path
            else:
                print("❌ Failed to download the video.")
                return None
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")
        return None
