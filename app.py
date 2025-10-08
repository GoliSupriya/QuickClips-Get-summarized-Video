from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import time
from werkzeug.utils import secure_filename
from download import download_youtube_video
from download_audio import extract_audio
from transcript import transcribe_audio
from timestamps import generate_transcript_with_timestamps
from summarize_content import extract_main_points
from SummarizedTimestamps import match_summary_to_timestamps
from summarized_video import create_summarized_video

app = Flask(__name__)

# Folder paths
DOWNLOAD_FOLDER = os.path.abspath("downloads")  # absolute path ensures Flask finds the file
UPLOAD_FOLDER = os.path.abspath("uploads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed video formats
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    """Check if uploaded file has a valid extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def summarize_video_pipeline(video_path):
    """
    Full video summarization pipeline.
    Always outputs downloads/summarized_video.mp4
    """
    if not video_path or not os.path.exists(video_path):
        print("❌ No video provided or file does not exist.")
        return None

    downloads_dir = app.config["DOWNLOAD_FOLDER"]
    os.makedirs(downloads_dir, exist_ok=True)

    # Fixed output filename
    output_video_path = os.path.join(downloads_dir, "summarized_video.mp4")

    # Intermediate files with timestamp to avoid collisions
    timestamp = int(time.time())
    audio_file = os.path.join(downloads_dir, f"audio_{timestamp}.wav")
    transcript_txt_file = os.path.join(downloads_dir, f"transcript_{timestamp}.txt")
    transcript_json_file = os.path.join(downloads_dir, f"transcript_{timestamp}.json")
    summary_file = os.path.join(downloads_dir, f"summary_{timestamp}.txt")
    timestamps_file = os.path.join(downloads_dir, f"timestamps_{timestamp}.json")

    try:
        # 1️⃣ Extract audio
        print("🎵 Extracting audio...")
        extract_audio(video_path, output_audio_path=audio_file)

        # 2️⃣ Transcribe audio
        print("📝 Transcribing audio...")
        transcribe_audio(audio_file, output_dir=downloads_dir,
                         output_file=os.path.basename(transcript_txt_file))

        # 3️⃣ Generate transcript with timestamps
        print("⏱ Generating transcript with timestamps...")
        generate_transcript_with_timestamps(audio_file, output_file=transcript_json_file)

        # 4️⃣ Extract main points
        print("📝 Extracting main points...")
        extract_main_points(transcript_txt_file, output_file=summary_file,
                            max_length=200, min_length=50)

        # 5️⃣ Match summary to timestamps
        print("🔗 Matching summary sentences with timestamps...")
        match_summary_to_timestamps(summary_file, transcript_json_file,
                                    output_file=timestamps_file)

        # 6️⃣ Create summarized video
        print("🎬 Creating summarized video...")
        output_video = create_summarized_video(video_path, timestamps_file, output_video_path)

        # Cleanup intermediates
        for f in [audio_file, transcript_txt_file, transcript_json_file, summary_file, timestamps_file]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as e:
                print(f"⚠️ Could not delete {f}: {e}")

        # Confirm video exists
        if output_video and os.path.exists(output_video):
            print(f"✅ Summarized video created at: {output_video}")
            return output_video
        else:
            print("⚠️ Summarized video could not be created.")
            return None

    except Exception as e:
        print(f"⚠️ Error while creating summarized video: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video/<filename>')
def serve_video(filename):
    """Serve video file for browser playback"""
    video_path = os.path.join(app.config["DOWNLOAD_FOLDER"], filename)
    if not os.path.exists(video_path):
        return "❌ Video not found", 404
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename, mimetype='video/mp4')


@app.route('/watch/<filename>')
def watch_video(filename):
    """Render HTML page with video player"""
    video_path = os.path.join(app.config["DOWNLOAD_FOLDER"], filename)
    if not os.path.exists(video_path):
        return f"❌ Video file not found at {video_path}"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Watch Summarized Video</title>
    </head>
    <body style="background-color:black; color:white;">
        <h2 style="align-items:center;text-align:center;">Summarized Video</h2>
        <video width="720" controls autoplay>
            <source src="/video/{filename}?t={int(time.time())}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    """


@app.route('/process', methods=['POST'])
def process():
    youtube_url = request.form.get('yturl')
    video_file = request.files.get('videofile')
    summarization_type = request.form.get('summarization_type')

    video_path = None

    # Case 1: YouTube video
    if youtube_url:
        video_path = download_youtube_video(youtube_url)
        if not video_path or not os.path.exists(video_path):
            return render_template("error.html", message="❌ Failed to download video."), 400

    # Case 2: Uploaded video
    elif video_file and video_file.filename:
        if not allowed_file(video_file.filename):
            return render_template("error.html", message="❌ Invalid file type."), 400
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        video_file.save(video_path)
    else:
        return render_template("error.html", message="❌ Provide YouTube URL or upload a video."), 400

    if summarization_type == 'summarized_video':
        summarized_video_path = summarize_video_pipeline(video_path)
        if not summarized_video_path:
            return render_template("error.html", message="❌ Summarization failed."), 500

        # Cleanup uploaded file
        if youtube_url is None and video_file:
            try:
                os.remove(video_path)
            except Exception as e:
                print(f"⚠️ Could not delete uploaded file: {e}")

        # Redirect to fixed filename
        return redirect(url_for('watch_video', filename="summarized_video.mp4"))

    elif summarization_type == 'summarized_text':
        return render_template("error.html", message="⚠️ Text summarization not implemented yet."), 400

    elif summarization_type == 'summarized_audio':
        return render_template("error.html", message="⚠️ Audio summarization not implemented yet."), 400

    else:
        return render_template("error.html", message="⚠️ Unsupported summarization type."), 400


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
