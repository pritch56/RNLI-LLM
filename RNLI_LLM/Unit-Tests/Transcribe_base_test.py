
import unittest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RNLI_LLM.Main.Transcript import transcribe_audio

class TestAudioTranscriberFromJson(unittest.TestCase):
    def test_transcription_matches_expected(self):
        # Load test cases from inputs.json
        json_path = os.path.join(os.path.dirname(__file__), 'inputs.json')
        with open(json_path, 'r', encoding='utf-8') as jf:
            test_cases = json.load(jf)

        results_path = os.path.join(os.path.dirname(__file__), 'bin', 'Transcribe_test_results.txt')
        os.makedirs(os.path.dirname(results_path), exist_ok=True)

        failures = []
        with open(results_path, 'w', encoding='utf-8') as outf:
            for idx, case in enumerate(test_cases):
                audio_path = case['audio_path']
                expected_transcript = case['expected_transcript']

                try:
                    # Transcribe the audio file and get the transcript directly
                    actual_transcript = transcribe_audio(audio_path, None, None, None, 'base', None)
                    # Write the result to Transcribe_test_results.txt
                    outf.write(f"Test case {idx+1}\n")
                    outf.write(f"AUDIO FILE: {audio_path}\n")
                    outf.write(f"EXPECTED TRANSCRIPT: {expected_transcript.strip()}\n")
                    outf.write(f"ACTUAL TRANSCRIPT: {actual_transcript.strip()}\n\n")
                    # Compare to expected (case-insensitive)
                    if actual_transcript.strip().lower() != expected_transcript.strip().lower():
                        failures.append({
                            'case': idx+1,
                            'audio': audio_path,
                            'expected': expected_transcript,
                            'actual': actual_transcript
                        })
                except Exception as e:
                    outf.write(f"Test case {idx+1}\n")
                    outf.write(f"AUDIO FILE: {audio_path}\n")
                    outf.write(f"EXPECTED TRANSCRIPT: {expected_transcript.strip()}\n")
                    outf.write(f"ACTUAL TRANSCRIPT: Exception: {e}\n\n")
                    failures.append({
                        'case': idx+1,
                        'audio': audio_path,
                        'expected': expected_transcript,
                        'actual': f'Exception: {e}'
                    })

        # Print summary of failures
        if failures:
            print("\nSUMMARY OF FAILURES:")
            for fail in failures:
                print(f"Test case {fail['case']} (audio: {fail['audio']}): expected '{fail['expected']}', got '{fail['actual']}'")
            assert False, f"{len(failures)} test(s) did not match expected output. See above."

if __name__ == '__main__':
    unittest.main()
