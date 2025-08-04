import unittest
import os
import json
from typing import Dict, Any

# Import the function under test
from Large_Language_Model import extract_distress_info

class TestLLMExtraction(unittest.TestCase):
    def test_llm_extraction_cases(self):
        test_dir = os.path.join(os.path.dirname(__file__), 'llm_testcases')
        test_files = [f for f in os.listdir(test_dir) if f.endswith('.json')]
        all_passed = True
        for fname in test_files:
            with open(os.path.join(test_dir, fname), 'r', encoding='utf-8') as f:
                case = json.load(f)
            transcript = case['transcript']
            expected = case['expected']
            print(f"\nRunning test: {fname}")
            result = extract_distress_info(transcript)
            for field in expected:
                actual_value = result.get(field, {}).get('value', None)
                expected_value = expected[field]
                if (actual_value or '').strip().lower() == (expected_value or '').strip().lower():
                    print(f"  {field}: PASS ({actual_value})")
                else:
                    print(f"  {field}: FAIL (expected: {expected_value}, got: {actual_value})")
                    all_passed = False
                self.assertEqual((actual_value or '').strip().lower(), (expected_value or '').strip().lower())

if __name__ == '__main__':
    unittest.main()
