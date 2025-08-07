import sys
import os
import argparse
import whisper
import subprocess


def convert_audio_to_wav(input_audio, temp_wav):
    """Convert any audio file to a temporary WAV file using ffmpeg."""
    try:
        subprocess.run(['ffmpeg', '-i', input_audio, '-ar', '16000', '-ac', '1', temp_wav], check=True)
        print(f"Converted {input_audio} to {temp_wav}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio file: {e}")
        sys.exit(1)


def transcribe_audio(input_audio, output_txt, model_size='base', language='en'):
    print("Converting audio to WAV format...")
    
    # Temporary WAV file path
    temp_wav = "temp_audio.wav"
    
    # Convert the input audio to WAV format
    convert_audio_to_wav(input_audio, temp_wav)

    model = whisper.load_model(model_size)
    print(f"Loaded Whisper model: {model_size}")
    
    try:
        # Transcribe the converted WAV file
        result = model.transcribe(temp_wav, language=language, verbose=True, task='transcribe')
    except Exception as e:
        print("Audio loading failed. Make sure your input file is valid.")
        print(f"Error: {e}")
        sys.exit(1)
    
    transcript = result['text'].strip()

    # Write plain text output if output_txt is provided
    if output_txt:
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(transcript + '\n')
        print(f"Transcription saved to {output_txt}")

    # Print detected language
    print(f"Detected language: {result['language']}")

    # Clean up temporary WAV file
    os.remove(temp_wav)

    return transcript


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper.")
    parser.add_argument('input_audio', help="Path to input audio file (any format supported by ffmpeg)")
    parser.add_argument('output_txt', help="Path to output .txt file for transcription")
    args = parser.parse_args()

    transcript = transcribe_audio(
        args.input_audio,
        output_txt=args.output_txt,
        model_size='base',
        language='en'
    )
    print("\nTranscription complete.\n")
    print(transcript)


if __name__ == '__main__':
    main()
