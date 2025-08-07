#!/usr/bin/env python3
import sys

import argparse
import json
import os

from simple_transcribe import transcribe_audio
from LLM import call_mistral

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio and analyze with LLM, output JSON.")
    parser.add_argument('input_audio', help="Path to input audio file")
    parser.add_argument('output_json', help="Path to output JSON file")
    parser.add_argument('--model', default='base', help="Whisper model size: tiny, base, small, medium, large")
    parser.add_argument('--language', default='en', help="Force language (e.g., 'en'). Default: auto-detect.")
    parser.add_argument('--hf_token', default=None, help="Optional: Hugging Face token for pyannote-audio")
    args = parser.parse_args()

    # Transcribe audio
    transcript = transcribe_audio(
        args.input_audio,
        output_txt=None,
        model_size=args.model,
        language=args.language
    )

    # Query LLM with transcript
    llm_result = call_mistral(transcript)

    # Compose output JSON
    output = {
        "transcript": transcript,
        "llm_result": llm_result
    }

    # Save to JSON file
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Output saved to {args.output_json}")

if __name__ == '__main__':
    main()
