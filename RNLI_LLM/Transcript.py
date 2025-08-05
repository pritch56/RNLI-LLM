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
        if not hf_token or not isinstance(hf_token, str) or not hf_token.strip():
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
            print("Check your Hugging Face token and internet connection.")
            return transcript

        if pipeline is None:
            print("pyannote Pipeline could not be loaded (returned None). Check your token and internet connection.")
            return transcript

        try:
            diarization = pipeline(input_audio)
        except Exception as e:
            print(f"Error running diarization pipeline: {e}")
            print("Check that your audio file is valid and supported.")
            return transcript

        # Check if diarization result is valid and non-empty
        if diarization is None or not hasattr(diarization, "itertracks"):
            print("Diarization result is invalid or empty.")
            return transcript

        segments_written = 0
        try:
            with open(diarization_txt, 'w', encoding='utf-8') as f:
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    # Validate turn and speaker
                    if not hasattr(turn, "start") or not hasattr(turn, "end") or speaker is None:
                        continue
                    f.write(f"{turn.start:.1f}s - {turn.end:.1f}s: Speaker {speaker}\n")
                    segments_written += 1
        except Exception as e:
            print(f"Error writing diarization output: {e}")
            return transcript

        if segments_written == 0:
            print("Warning: No speaker segments found in diarization output.")
        else:
            print(f"Speaker diarization saved to {diarization_txt} ({segments_written} segments)")

    return transcript

def diarize_and_label_transcript(audio_path, transcript_text, hf_token=None):
    """
    Given an audio file and a transcript (without speaker labels), use pyannote-audio
    to assign speaker labels to each segment and return the labeled transcript.
    Args:
        audio_path (str): Path to the audio file.
        transcript_text (str): Transcript with no speaker labels, sentences separated by blank lines.
        hf_token (str, optional): Hugging Face token for pyannote-audio.
    Returns:
        str: Transcript with speaker labels (e.g., 'person 1', 'person 2', ...)
    """
    try:
        from pyannote.audio import Pipeline
    except ImportError:
        print("pyannote.audio is not installed. Please install it with 'pip install pyannote.audio'.")
        return transcript_text

    import os
    import re

    if not hf_token:
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
    if not hf_token or not isinstance(hf_token, str) or not hf_token.strip():
        print("Hugging Face token required for pyannote-audio. Set HUGGINGFACE_TOKEN env var or pass as argument.")
        return transcript_text

    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=hf_token
        )
    except Exception as e:
        print(f"Failed to load pyannote-audio pipeline: {e}")
        return transcript_text

    try:
        diarization = pipeline(audio_path)
    except Exception as e:
        print(f"Error running diarization pipeline: {e}")
        return transcript_text

    # Parse transcript into sentences (split by blank lines)
    sentences = [s.strip() for s in re.split(r'\n\s*\n', transcript_text) if s.strip()]
    if not sentences:
        print("No sentences found in transcript.")
        return transcript_text

    # Get diarization segments as a list
    diar_segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        diar_segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    if not diar_segments:
        print("No diarization segments found.")
        return transcript_text

    # Assign speakers to sentences by dividing transcript duration into segments
    # For simplicity, use Whisper to get segment timestamps if available
    try:
        import whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, task='transcribe', verbose=False)
        whisper_segments = result.get("segments", [])
    except Exception:
        whisper_segments = []

    # If Whisper segments available, use their timestamps to align with diarization
    if whisper_segments and len(whisper_segments) == len(sentences):
        sentence_times = [(seg["start"], seg["end"]) for seg in whisper_segments]
    else:
        # Otherwise, divide audio duration equally among sentences
        try:
            import soundfile as sf
            audio_info = sf.info(audio_path)
            duration = audio_info.duration
        except Exception:
            duration = diar_segments[-1]["end"]
        avg_len = duration / len(sentences)
        sentence_times = [(i * avg_len, (i + 1) * avg_len) for i in range(len(sentences))]

    # For each sentence, find the diarization segment with the most overlap
    labeled_lines = []
    speaker_map = {}
    speaker_count = 0

    for idx, (sent, (start, end)) in enumerate(zip(sentences, sentence_times)):
        # Find overlapping diarization segments
        overlaps = []
        for seg in diar_segments:
            overlap = max(0, min(end, seg["end"]) - max(start, seg["start"]))
            if overlap > 0:
                overlaps.append((overlap, seg["speaker"]))
        if overlaps:
            # Assign the speaker with the largest overlap
            speaker = max(overlaps, key=lambda x: x[0])[1]
        else:
            # Fallback: assign the closest segment
            closest = min(diar_segments, key=lambda seg: abs((seg["start"] + seg["end"]) / 2 - (start + end) / 2))
            speaker = closest["speaker"]
        # Map speaker label to person N
        if speaker not in speaker_map:
            speaker_count += 1
            speaker_map[speaker] = f"person {speaker_count}"
        labeled_lines.append(f"{speaker_map[speaker]}\n{sent}\n")

    return "\n".join(labeled_lines).strip()

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
