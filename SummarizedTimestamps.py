from sentence_transformers import SentenceTransformer, util
import json
import os
import torch

# Load sentence embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def match_summary_to_timestamps(summary_file, transcript_file, output_file="downloads/summary_with_timestamps.json"):
    try:
        # Load summary text
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_text = f.read().strip()

        # Split summary into sentences
        summary_sentences = [s.strip() for s in summary_text.split(".") if s.strip()]

        # Load transcript with timestamps
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = json.load(f)

        transcript_texts = [seg["text"] for seg in transcript]

        # Encode sentences
        transcript_embeddings = embedder.encode(transcript_texts, convert_to_tensor=True)
        summary_embeddings = embedder.encode(summary_sentences, convert_to_tensor=True)

        results = []
        used_indices = set()  # Track used transcript indices

        # Match each summary sentence to closest transcript sentence
        for i, summ_sent in enumerate(summary_sentences):
            cosine_scores = util.cos_sim(summary_embeddings[i], transcript_embeddings)[0]

            # Sort transcript indices by similarity score (highest first)
            sorted_indices = torch.argsort(cosine_scores, descending=True)

            best_idx = None
            for idx in sorted_indices:
                if int(idx) not in used_indices:
                    best_idx = int(idx)
                    used_indices.add(best_idx)
                    break

            if best_idx is None:
                # Fallback: if everything is used, just take the highest one
                best_idx = int(sorted_indices[0])

            match = transcript[best_idx]

            results.append({
                "summary_sentence": summ_sent,
                "timestamp": f"{match['start']} --> {match['end']}",
                "matched_text": match["text"]
            })

        # Save results
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        print(f"✅ Summary with unique timestamps saved at {output_file}")
        return results

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None

