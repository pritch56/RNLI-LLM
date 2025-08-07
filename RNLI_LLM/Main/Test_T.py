import os
import tempfile
from pydub import AudioSegment
import speech_recognition as sr

def transcribe_audio(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print("File not found.")
        return None

    # Load the audio file
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None

    # Create a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_wav_file:
        audio.export(temp_wav_file.name, format="wav")

        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Transcribe the audio
        with sr.AudioFile(temp_wav_file.name) as source:
            audio_data = recognizer.record(source)  # Read the entire audio file
            try:
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return None

# Example usage
if __name__ == "__main__":
    file_path = "RNLI_LLM/input/LOTTIE.wav"  # Replace with your audio file path
    transcription = transcribe_audio(file_path)
    if transcription:
        print("Transcription:")
        print(transcription)
