import unittest
import os
import json
from typing import Dict, Any

# Import the function under test
import sys
import importlib.util
llm_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'LLM.py'))
spec = importlib.util.spec_from_file_location('LLM', llm_path)
LLM = importlib.util.module_from_spec(spec)
sys.modules['LLM'] = LLM
spec.loader.exec_module(LLM)
extract_distress_info = LLM.call_mistral

class TestLLMExtraction(unittest.TestCase):
    def test_llm_extraction_cases(self):
        # Load all test cases from a single JSON file (array of objects)
        import time
        test_file = os.path.join(os.path.dirname(__file__), 'llm_testcases', 'test1.json')
        with open(test_file, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)

        failures = []
        # If test_cases is a dict (as in your file), iterate over its values
        if isinstance(test_cases, dict):
            cases = list(test_cases.values())
        else:
            cases = test_cases
        for idx, case in enumerate(cases):
            if not isinstance(case, dict):
                print(f"\nTest case {idx+1} is not a dict: {case}")
                failures.append({
                    'case': idx+1,
                    'field': 'ALL',
                    'expected': 'dict with keys transcript/expected',
                    'actual': str(case)
                })
                continue
            transcript = case.get('transcript')
            expected = case.get('expected')
            print(f"\nRunning test case {idx+1}:")
            start = time.time()
            try:
                result = extract_distress_info(transcript)
                elapsed = time.time() - start
                print(f"  LLM returned: {json.dumps(result, indent=2, ensure_ascii=False)}")
                print(f"  Time taken: {elapsed:.2f} seconds")
                for field in expected:
                    actual_value = result.get(field, {}).get('value', None)
                    expected_value = expected[field]
                    def normalize(val):
                        import re
                        from num2words import num2words
                        val = (val or '').strip().lower()
                        val = re.sub(r'[^a-z0-9 ]', '', val)
                        # Accept common synonyms for unknown/none
                        if val in {"", "none", "no", "n/a", "na", "not known", "notknown", "not known", "not specified", "not stated", "0"}:
                            return "0"
                        if val in {"unknown", "unk", "not specified", "notstated"}:
                            return "unknown"
                        try:
                            # Accept both digit and word forms as equivalent
                            from word2number import w2n
                            if val.isdigit():
                                return num2words(int(val))
                            # Try to convert word to number (e.g. 'three' -> '3')
                            as_num = str(w2n.word_to_num(val))
                            return as_num
                        except Exception:
                            return val
                    # For injuries and number_of_people, accept either number or word form as equivalent
                    if field in ("injuries", "number_of_people"):
                        def equiv(val1, val2):
                            norm1 = normalize(val1)
                            norm2 = normalize(val2)
                            # Accept if either matches as number or word
                            if norm1 == norm2:
                                return True
                            # Try cross conversion
                            try:
                                from num2words import num2words
                                from word2number import w2n
                                # Convert both ways
                                if norm1.isdigit() and num2words(int(norm1)) == norm2:
                                    return True
                                if norm2.isdigit() and num2words(int(norm2)) == norm1:
                                    return True
                                # Try word2number both ways
                                if w2n.word_to_num(norm1) == w2n.word_to_num(norm2):
                                    return True
                            except Exception:
                                pass
                            return False
                        if equiv(actual_value, expected_value):
                            print(f"  {field}: PASS ({actual_value})")
                        else:
                            print(f"  {field}: FAIL (expected: {expected_value}, got: {actual_value})")
                            failures.append({
                                'case': idx+1,
                                'field': field,
                                'expected': expected_value,
                                'actual': actual_value
                            })
                    else:
                        actual_norm = normalize(actual_value)
                        expected_norm = normalize(expected_value)
                        if actual_norm == expected_norm:
                            print(f"  {field}: PASS ({actual_value})")
                        else:
                            print(f"  {field}: FAIL (expected: {expected_value}, got: {actual_value})")
                            failures.append({
                                'case': idx+1,
                                'field': field,
                                'expected': expected_value,
                                'actual': actual_value
                            })
            except Exception as e:
                elapsed = time.time() - start
                print(f"  ERROR in test case {idx+1} after {elapsed:.2f} seconds: {e}")
                failures.append({
                    'case': idx+1,
                    'field': 'ALL',
                    'expected': str(expected),
                    'actual': f'Exception: {e}'
                })
        # Print summary
        if failures:
            print("\nSUMMARY OF FAILURES:")
            for fail in failures:
                print(f"Test case {fail['case']} field '{fail['field']}': expected '{fail['expected']}', got '{fail['actual']}'")
            assert False, f"{len(failures)} field(s) did not match expected output. See above."
        else:
            print("\nAll test cases passed!")

if __name__ == '__main__':
    unittest.main()
