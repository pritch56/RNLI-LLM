# transcriber.py

import warnings
import numpy as np
import whisper
import librosa
import json

warnings.filterwarnings("ignore")

# Dummy LLM call (replace with actual API integration)
def call_mistral(transcript: str) -> str:
    return f"LLM analysis of transcript (length {len(transcript)} chars)."

def load_audio_with_librosa(file_path: str, sr: int = 16000) -> np.ndarray:
    """Load audio file using librosa (no ffmpeg dependency)"""
    audio, _ = librosa.load(file_path, sr=sr, mono=True)
    return audio

def transcribe_audio(input_audio_path: str, model_size: str = 'base', language: str = None) -> str:
    """Transcribe audio using Whisper + librosa. Returns plain transcript string."""
    model = whisper.load_model(model_size)
    print(f"Loaded Whisper model: {model_size}")

    audio = load_audio_with_librosa(input_audio_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    if language is None:
        _, probs = model.detect_language(mel)
        language = max(probs, key=probs.get)
        print(f"Detected language: {language}")

    options = whisper.DecodingOptions(language=language, fp16=False)
    result = whisper.decode(model, mel, options)
    return result.text.strip()

def transcribe_and_analyze(input_audio_path: str, output_json_path: str, model_size: str = 'base', language: str = None):
    """Transcribes the audio, analyzes with LLM, and writes to JSON"""
    transcript = transcribe_audio(input_audio_path, model_size, language)
    llm_result = call_mistral(transcript)

    output = {
        "transcript": transcript,
        "llm_result": llm_result
    }

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Saved output to {output_json_path}")
    return output
