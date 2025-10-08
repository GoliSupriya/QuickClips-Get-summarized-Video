from transformers import pipeline
import os

def chunk_text(text, max_chars=1000):
    """Split text into chunks of max_chars length without breaking words."""
    words = text.split()
    chunks = []
    chunk = ""
    for word in words:
        if len(chunk) + len(word) + 1 > max_chars:
            chunks.append(chunk.strip())
            chunk = ""
        chunk += word + " "
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def extract_main_points(transcript_file, output_file="downloads/summary_output.txt", max_length=200, min_length=50):
    try:
        with open(transcript_file, "r", encoding="utf-8") as f:
            text = f.read()

        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        chunks = chunk_text(text, max_chars=1000)  # split long transcript
        summary_list = []

        for chunk in chunks:
            summary = summarizer(
                chunk, max_length=max_length, min_length=min_length, do_sample=False
            )[0]["summary_text"]
            summary_list.append(summary)

        final_summary = " ".join(summary_list)

        # Ensure downloads directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Save summary in file only
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_summary)

        print(f"✅ Main points extracted and saved in: {output_file}")
        return True
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False

if __name__ == "__main__":
    transcript_path = "downloads/transcript.txt"
    output_summary_path = "downloads/main_points_summary.txt"  # <-- New file
    extract_main_points(transcript_path, output_file=output_summary_path)
