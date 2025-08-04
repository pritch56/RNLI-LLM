
import unittest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Transcript import transcribe_audio

class TestAudioTranscriberFromJson(unittest.TestCase):
    def test_transcription_matches_expected(self):
        # Load test cases from inputs.json
        json_path = os.path.join(os.path.dirname(__file__), 'inputs.json')
        with open(json_path, 'r', encoding='utf-8') as jf:
            test_cases = json.load(jf)

        outputs_path = os.path.join(os.path.dirname(__file__), 'bin', 'outputs.txt')
        os.makedirs(os.path.dirname(outputs_path), exist_ok=True)

        with open(outputs_path, 'w', encoding='utf-8') as outf:
            for case in test_cases:
                audio_path = case['audio_path']
                expected_transcript = case['expected_transcript']

                # Transcribe the audio file and get the transcript directly
                actual_transcript = transcribe_audio(audio_path, None, None, None, 'large', None)

                # Write the actual transcript to outputs.txt
                outf.write(f"AUDIO: {audio_path}\nTRANSCRIPT: {actual_transcript.strip()}\n\n")

                # Compare to expected
                self.assertEqual(actual_transcript.strip(), expected_transcript)

        # Clear the outputs.txt file after the test
        with open(outputs_path, 'w', encoding='utf-8') as outf:
            outf.write("")

if __name__ == '__main__':
    unittest.main()
