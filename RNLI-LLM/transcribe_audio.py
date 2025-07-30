#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import tempfile

try:
    import whisper
except ImportError:
    print("The 'whisper' package is not installed. Please see the instructions below.")
    sys.exit(1)

# Optional: For SRT/VTT output
try:
    from whisper.utils import write_srt, write_vtt
except ImportError:
    write_srt = None
    write_vtt = None

def convert_to_wav(input_path, output_path):
    """Convert any audio file to 16kHz mono WAV using ffmpeg."""
    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def transcribe_audio(input_audio, output_txt, output_srt=None, output_vtt=None, model_size='large', language=None):
    model = whisper.load_model(model_size)
    print(f"Loaded Whisper model: {model_size}")
    result = model.transcribe(input_audio, language=language, verbose=True, task='transcribe')
    
    # Write plain text output
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(result['text'].strip() + '\n')
    print(f"Transcription saved to {output_txt}")

    # Write SRT
    if output_srt and write_srt:
        with open(output_srt, 'w', encoding='utf-8') as f:
            write_srt(result['segments'], file=f)
        print(f"SRT subtitles saved to {output_srt}")
    # Write VTT
    if output_vtt and write_vtt:
        with open(output_vtt, 'w', encoding='utf-8') as f:
            write_vtt(result['segments'], file=f)
        print(f"VTT subtitles saved to {output_vtt}")

    # Language detection
    print(f"Detected language: {result['language']}")

    # Speaker diarization placeholder
    print("[Placeholder] Speaker diarization is not implemented. See README for extension options.")

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI Whisper (commercial-grade accuracy)")
    parser.add_argument('input_audio', help="Path to input audio file (any format)")
    parser.add_argument('output_txt', help="Path to output .txt file for transcription")
    parser.add_argument('--srt', help="Optional: Output SRT subtitle file")
    parser.add_argument('--vtt', help="Optional: Output VTT subtitle file")
    parser.add_argument('--model', default='large', help="Whisper model size: tiny, base, small, medium, large (default: large)")
    parser.add_argument('--language', default=None, help="Force language (e.g., 'en'). Default: auto-detect.")
    args = parser.parse_args()

    # Convert input to WAV if needed
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, 'converted.wav')
        try:
            convert_to_wav(args.input_audio, wav_path)
        except Exception as e:
            print(f"FFmpeg conversion failed: {e}")
            sys.exit(1)
        transcribe_audio(
            wav_path,
            args.output_txt,
            output_srt=args.srt,
            output_vtt=args.vtt,
            model_size=args.model,
            language=args.language
        )

if __name__ == '__main__':
    main()

# ----------------------
# INSTALLATION INSTRUCTIONS
#
# 1. Install ffmpeg:
#    - Windows: Download from https://ffmpeg.org/download.html and add to PATH
#    - Mac: brew install ffmpeg
#    - Linux: sudo apt install ffmpeg
#
# 2. Install Python packages:
#    pip install openai-whisper torch
#    # Optionally: pip install pydub faster-whisper
#
# 3. (Optional) For SRT/VTT: whisper >= 20230314
#
# EXAMPLE USAGE:
#    python transcribe_audio.py input_audio.m4a output.txt --srt output.srt --vtt output.vtt
#
# For commercial-grade accuracy, use the 'large' model (default). For faster but less accurate, try 'medium' or 'small'.
#
# For speaker diarization, see pyannote.audio or similar libraries for future extension. 