
import argparse
import sys

# Try to import Whisper for speech-to-text
try:
    import whisper
except ImportError:
    print("The 'whisper' package is not installed. Please see the instructions below.")
    sys.exit(1)

# Optional: For SRT/VTT subtitle output
try:
    from whisper.utils import write_srt, write_vtt
except ImportError:
    write_srt = None
    write_vtt = None


def transcribe_audio(
    input_audio,
    output_txt,
    output_srt=None,
    output_vtt=None,
    model_size='large',
    language=None,
    diarization_txt=None,
    hf_token=None
):
    """
    Transcribe audio using OpenAI Whisper and save results in text, SRT, and VTT formats.
    Optionally, perform speaker diarization using pyannote-audio and output a speaker-labeled transcript.
    Args:
        input_audio (str): Path to the input audio file (any format supported by Whisper)
        output_txt (str): Path to save the plain text transcript
        output_srt (str, optional): Path to save SRT subtitles
        output_vtt (str, optional): Path to save VTT subtitles
        model_size (str): Whisper model size (tiny, base, small, medium, large)
        language (str, optional): Language code (e.g., 'en') or None for auto-detect
        diarization_txt (str, optional): Path to save speaker-labeled transcript (if None, diarization not run)
        hf_token (str, optional): Hugging Face token for pyannote-audio (can also use env var HUGGINGFACE_TOKEN)
    """
    model = whisper.load_model(model_size)
    print(f"Loaded Whisper model: {model_size}")
    # Transcribe the audio file directly (no ffmpeg conversion)
    result = model.transcribe(input_audio, language=language, verbose=True, task='transcribe')

    transcript = result['text'].strip()

    # Write plain text output if output_txt is provided
    if output_txt:
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(transcript + '\n')
        print(f"Transcription saved to {output_txt}")

    # Write SRT subtitles if requested and supported
    if output_srt and write_srt:
        with open(output_srt, 'w', encoding='utf-8') as f:
            write_srt(result['segments'], file=f)
        print(f"SRT subtitles saved to {output_srt}")
    # Write VTT subtitles if requested and supported
    if output_vtt and write_vtt:
        with open(output_vtt, 'w', encoding='utf-8') as f:
            write_vtt(result['segments'], file=f)
        print(f"VTT subtitles saved to {output_vtt}")

    # Print detected language
    print(f"Detected language: {result['language']}")

    # Speaker diarization using pyannote-audio if requested
    if diarization_txt:
        try:
            from pyannote.audio import Pipeline
        except ImportError:
            print("pyannote.audio is not installed. Please install it with 'pip install pyannote.audio'.")
            return transcript
        # Get Hugging Face token
        if not hf_token:
            import os
            hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        if not hf_token:
            print("Hugging Face token required for pyannote-audio. Set HUGGINGFACE_TOKEN env var or pass as argument.")
            return transcript
        print("Running speaker diarization with pyannote-audio...")
        try:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization",
                use_auth_token=hf_token
            )
        except Exception as e:
            print(f"Failed to load pyannote-audio pipeline: {e}")
            return transcript
        if pipeline is None:
            print("pyannote Pipeline could not be loaded (returned None). Check your token and internet connection.")
            return transcript
        try:
            diarization = pipeline(input_audio)
        except Exception as e:
            print(f"Error running diarization pipeline: {e}")
            return transcript
        # Write speaker-labeled transcript to diarization_txt
        with open(diarization_txt, 'w', encoding='utf-8') as f:
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                f.write(f"{turn.start:.1f}s - {turn.end:.1f}s: Speaker {speaker}\n")
        print(f"Speaker diarization saved to {diarization_txt}")

    return transcript

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI Whisper (no ffmpeg conversion)")
    parser.add_argument('input_audio', help="Path to input audio file")
    parser.add_argument('output_txt', help="Path to output .txt file for transcription")
    parser.add_argument('--srt', help="Optional: Output SRT subtitle file")
    parser.add_argument('--vtt', help="Optional: Output VTT subtitle file")
    parser.add_argument('--model', default='large', help="Whisper model size: tiny, base, small, medium, large (default: large)")
    parser.add_argument('--language', default=None, help="Force language (e.g., 'en'). Default: auto-detect.")
    parser.add_argument('--diarization', help="Optional: Output speaker-labeled transcript file (requires pyannote.audio and Hugging Face token)")
    parser.add_argument('--hf_token', default=None, help="Optional: Hugging Face token for pyannote-audio (or set HUGGINGFACE_TOKEN env var)")
    args = parser.parse_args()

    import time
    start_time = time.time()
    transcribe_audio(
        args.input_audio,
        args.output_txt,
        output_srt=args.srt,
        output_vtt=args.vtt,
        model_size=args.model,
        language=args.language,
        diarization_txt=args.diarization,
        hf_token=args.hf_token
    )
    elapsed = time.time() - start_time
    print(f"\n[Timer] Transcription process took {elapsed:.2f} seconds.")

if __name__ == '__main__':
    main()
