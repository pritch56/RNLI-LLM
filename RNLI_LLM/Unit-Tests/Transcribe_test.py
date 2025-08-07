
import unittest
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RNLI_LLM.Main.Transcript import transcribe_audio

class TestAudioTranscriberFromJson(unittest.TestCase):
    def test_transcription_matches_expected(self):
        import time
        # Load test cases from inputs.json
        json_path = os.path.join(os.path.dirname(__file__), 'inputs.json')
        with open(json_path, 'r', encoding='utf-8') as jf:
            test_cases = json.load(jf)

        outputs_path = os.path.join(os.path.dirname(__file__), 'bin', 'outputs.txt')
        os.makedirs(os.path.dirname(outputs_path), exist_ok=True)

        model_sizes = ['tiny', 'base', 'small', 'medium', 'large']


        failures = []
        with open(outputs_path, 'w', encoding='utf-8') as outf:
            for model_size in model_sizes:
                print(f"\n{'='*40}\nTesting Whisper model: {model_size}\n{'='*40}")
                outf.write(f"\n{'='*40}\nTesting Whisper model: {model_size}\n{'='*40}\n")
                start_model = time.time()
                for case in test_cases:
                    audio_path = case['audio_path']
                    expected_transcript = case['expected_transcript']

                    try:
                        start = time.time()
                        actual_transcript = transcribe_audio(audio_path, None, None, None, model_size, None)
                        elapsed = time.time() - start

                        # Write the actual transcript and timing to outputs.txt
                        outf.write(f"AUDIO: {audio_path}\nMODEL: {model_size}\nTIME: {elapsed:.2f} sec\nTRANSCRIPT: {actual_transcript.strip()}\nEXPECTED: {expected_transcript}\n\n")

                        # Print result to console
                        print(f"AUDIO: {audio_path}")
                        print(f"MODEL: {model_size}")
                        print(f"TIME: {elapsed:.2f} sec")
                        print(f"TRANSCRIPT: {actual_transcript.strip()}")
                        print(f"EXPECTED:   {expected_transcript}")
                        actual_clean = actual_transcript.strip().lower()
                        expected_clean = expected_transcript.lower()
                        if actual_clean == expected_clean:
                            print("RESULT: PASS\n")
                        else:
                            print("RESULT: FAIL\n")
                            failures.append((model_size, audio_path, actual_transcript.strip(), expected_transcript))
                    except Exception as e:
                        print(f"ERROR for model {model_size}, audio {audio_path}: {e}")
                        failures.append((model_size, audio_path, str(e), expected_transcript))
                total_model_time = time.time() - start_model
                print(f"Total time for model '{model_size}': {total_model_time:.2f} sec\n")
                outf.write(f"Total time for model '{model_size}': {total_model_time:.2f} sec\n\n")

        # Print summary of failures at the end
        if failures:
            print("\nSUMMARY OF FAILURES:")
            for model_size, audio_path, actual, expected in failures:
                print(f"MODEL: {model_size} | AUDIO: {audio_path}")
                print(f"ACTUAL:   {actual}")
                print(f"EXPECTED: {expected}\n")
            self.fail(f"{len(failures)} transcription(s) did not match expected output. See above.")

        # Clear the outputs.txt file after the test
        with open(outputs_path, 'w', encoding='utf-8') as outf:
            outf.write("")

if __name__ == '__main__':
    unittest.main()
