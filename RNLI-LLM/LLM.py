#!/usr/bin/env python

import json  # For handling JSON data
import requests  # For making HTTP requests to the LLM API
import sys  # For system exit and error handling

# URL for the local Mistral (or compatible) LLM API endpoint
MISTRAL_API_URL = "http://localhost:1234/v1/chat/completions"  # Change to your endpoint if needed

# Prompt template for instructing the LLM to extract structured SAR information from a transcript
PROMPT_TEMPLATE = """
You are an expert maritime SAR operator. Extract the following details from the transcript below.

Return only valid, indented JSON with the following fields:
- ship_name
- position  # Can be GPS coordinates or bearing/distance from a known landmark
- number_of_people
- injuries  # Number and type, if any
- distress_type  # e.g., fire, sinking, MOB, engine failure
- boat_name  # Same as ship_name, if not explicitly different

For each field, return:
- value: the extracted information or "unknown"
- confidence: a float between 0.0 and 1.0

# Transcript:
# '{transcript}'

# Output only valid, indented JSON with all  categories and subfields.
"""

def call_mistral(transcript):
    """
    Sends the transcript to the local LLM API and returns the extracted structured information as a Python dict.
    Handles API errors and malformed responses robustly.
    """
    # Format the prompt with the transcript
    prompt = PROMPT_TEMPLATE.format(transcript=transcript)
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "google/gemma-3n-e4b",  # Model name; change as needed
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,  # Lower temperature for more deterministic output
        "max_tokens": 2048
    }
    
    # Send the request to the LLM API
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to the Mistral API at {MISTRAL_API_URL}. Is the server running?")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        sys.exit(1)
    
    # Parse the JSON response
    try:
        result = response.json()
    except json.JSONDecodeError:
        print(f"Invalid JSON response from API. Response: {response.text}")
        sys.exit(1)
    
    # Validate the response structure
    if "choices" not in result:
        print(f"Unexpected API response structure. Response: {result}")
        sys.exit(1)
    
    if not result["choices"]:
        print("API returned no choices. Response:", result)
        sys.exit(1)
    
    if "message" not in result["choices"][0]:
        print(f"Unexpected choice structure. Choice: {result['choices'][0]}")
        sys.exit(1)
    
    # Extract the content (model output) from the response
    content = result["choices"][0]["message"]["content"]
    
    # Find and parse the first JSON object in the output
    try:
        json_start = content.index('{')
        json_data = json.loads(content[json_start:])
    except ValueError:
        print("No JSON found in model output. Output was:\n", content)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Model output was not valid JSON. Output was:\n", content)
        sys.exit(1)
    
    return json_data


def main():
    """
    Main entry point: reads the transcript from 'output.txt',
    sends it to the LLM, and prints the structured JSON result.
    """
    # Always use 'output.txt' as the input file
    input_file = 'output.txt'
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            transcript = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}. Please make sure the file exists.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        sys.exit(1)
    
    # Call the LLM and print the result as pretty JSON
    data = call_mistral(transcript)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
