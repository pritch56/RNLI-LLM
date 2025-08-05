import os
import sys
import json
from pyannote.audio import Pipeline

# Usage: python main.py <audio_path> <output_json> [<hf_token>]
if len(sys.argv) < 3:
    print("Usage: python main.py <audio_path> <output_json> [<hf_token>]")
    sys.exit(1)

audio_path = sys.argv[1]
output_json = sys.argv[2]
hf_token = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("HUGGINGFACE_TOKEN")

if not hf_token or not isinstance(hf_token, str) or not hf_token.strip():
    print("ERROR: Hugging Face token required. Pass as argument or set HUGGINGFACE_TOKEN env var.")
    print("You can get a token at https://huggingface.co/settings/tokens")
    sys.exit(1)

try:
    # Load pretrained diarization pipeline with token
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=hf_token)
except Exception as e:
    print("ERROR: Failed to load pyannote/speaker-diarization pipeline.")
    print("This is usually due to an invalid or expired Hugging Face token, or lack of access to the model.")
    print(f"Details: {e}")
    sys.exit(1)

try:
    # Run on your audio file
    diarization = pipeline(audio_path)
except Exception as e:
    print("ERROR: Failed to run diarization pipeline on the audio file.")
    print(f"Details: {e}")
    sys.exit(1)

# Collect speaker change timestamps and labels
segments = []
for turn, _, speaker in diarization.itertracks(yield_label=True):
    segments.append({
        "start": round(turn.start, 2),
        "end": round(turn.end, 2),
        "speaker": str(speaker)
    })

# Write to JSON file
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(segments, f, indent=2)

print(f"Speaker segments written to {output_json}")
