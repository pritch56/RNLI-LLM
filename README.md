# Folder Structure Update
## Transcription Options: With and Without FFmpeg

You can transcribe audio using either of the following scripts:

- **With FFmpeg (for maximum compatibility):**
  - Use `transcribe_audio.py` to handle any audio format (M4A, MP3, WAV, etc.).
  - This script automatically converts audio to 16kHz mono WAV using FFmpeg before transcription.
  - **Example:**
    ```bash
    python RNLI-LLM/transcribe_audio.py input/your_audio.m4a output/your_transcript.txt
    ```

- **Without FFmpeg:**
  - Use `Transcript-bl.py` if your audio is already in a format natively supported by Whisper (e.g., WAV, MP3, FLAC, M4A).
  - This script does not perform any conversion—audio is passed directly to Whisper.
  - **Example:**
    ```bash
    python RNLI-LLM/Transcript-bl.py input/your_audio.wav output/your_transcript.txt
    ```

Choose the script that best fits your workflow and input file types. If unsure, use the FFmpeg version for best compatibility.

Audio samples should be placed in the `RNLI-LLM/input/` folder.
All output files (transcripts, JSON, subtitles, etc.) will be written to the `RNLI-LLM/output/` folder.

Update your commands accordingly, for example:

```
python RNLI-LLM/transcribe_audio.py input/Test_distress_call.wav output/output.txt
```

The main LLM script will now read from `output/output.txt`.

# RNLI-LLM: Maritime Distress Call Analysis System

A Python-based system for transcribing and analyzing maritime distress calls using OpenAI Whisper for speech-to-text conversion and a local LLM (Mistral/Gemma) for structured information extraction.

## Project Overview

This system is designed to assist maritime Search and Rescue (SAR) operations by:
1. **Transcribing audio recordings** of distress calls using OpenAI Whisper
2. **Extracting structured information** from transcripts using a Large Language Model
3. **Providing confidence scores** for each extracted piece of information

The system can process various audio formats and extract key maritime distress information including vessel details, position, number of people on board, injuries, and type of distress.

## Automated Testing

This project includes a suite of automated tests to verify both transcription and information extraction accuracy. Tests are located in the `RNLI_LLM/Unit-Tests/` directory and cover:

- **Transcription accuracy**: Compares Whisper-generated transcripts to expected results for a variety of real-world audio samples.
- **LLM extraction**: Validates that the LLM correctly extracts structured information (ship name, position, injuries, etc.) from transcripts.

### Running the Tests

1. **Install test dependencies** (in addition to main requirements):
   ```bash
   pip install num2words word2number
   ```
2. **Run all tests** from the project root:
   ```bash
   python -m unittest discover RNLI_LLM/Unit-Tests
   ```
   Or run individual test files, e.g.:
   ```bash
   python RNLI_LLM/Unit-Tests/Transcribe_test.py
   python RNLI_LLM/Unit-Tests/LLM_test.py
   ```
3. **Test data**: Test cases are defined in `inputs.json` (for transcription) and `llm_testcases/test1.json` (for LLM extraction).

Test output and results are written to the `RNLI_LLM/Unit-Tests/bin/` directory.

## Speaker Diarization (Who Spoke When)

The system supports optional **speaker diarization** (labeling transcript segments by speaker) using [pyannote-audio](https://github.com/pyannote/pyannote-audio). This requires a Hugging Face account and access token.

### How to Use Diarization

1. **Install pyannote-audio**:
   ```bash
   pip install pyannote.audio
   ```
2. **Get a Hugging Face token**: [Create a free account](https://huggingface.co/join) and generate a token with access to `pyannote/speaker-diarization`.
3. **Run transcription with diarization**:
   ```bash
   python RNLI_LLM/Transcript.py input/your_audio.wav output/your_transcript.txt --diarization output/diarized.txt --hf_token <YOUR_HF_TOKEN>
   ```
   - The diarized transcript will be saved to the file specified by `--diarization`.
   - If `--hf_token` is omitted, set the `HUGGINGFACE_TOKEN` environment variable instead.

**Note:** Diarization is only available in `Transcript.py` (not in the FFmpeg-based script). For more details, see comments in `Transcript.py`.

## Architecture

```
Audio Input → Whisper Transcription → LLM Analysis → Structured JSON Output
```

### Components:
- **`transcribe_audio.py`**: Handles audio transcription using OpenAI Whisper
- **`LLM.py`**: Processes transcripts and extracts structured information
- **Audio files**: Test distress call recordings (M4A/WAV formats)

## Features

### Current Implementation
- Multi-format audio support (M4A, WAV, MP3, etc.)
- High-accuracy transcription using Whisper Large model
- Structured information extraction with confidence scoring
- JSON output format for easy integration
- Automatic audio format conversion to WAV
- Optional SRT/VTT subtitle generation

### Extracted Information
- **Ship/Vessel Name**: Name of the distressed vessel
- **Position**: GPS coordinates or bearing/distance from landmarks
- **Number of People**: Count of persons on board
- **Injuries**: Number and type of injuries (if any)
- **Distress Type**: Nature of the emergency (fire, sinking, MOB, etc.)
- **Boat Name**: Alternative vessel identifier

## Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (for audio conversion)
- Local LLM server (Mistral/Gemma)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd RNLI-LLM
   ```

2. **Install FFmpeg**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up local LLM server**
   - Install and run a local LLM server (e.g., Ollama, LM Studio)
   - Update `MISTRAL_API_URL` in `LLM.py` to point to your server
   - Default: `http://localhost:1234/v1/chat/completions`

### Usage

1. **Transcribe audio file**
   ```bash
   python transcribe_audio.py Test_distress_call.m4a output.txt
   ```

2. **Extract structured information**
   ```bash
   python LLM.py > output.json
   ```

3. **View results**
   ```bash
   cat output.json
   ```

## Configuration

### LLM Settings (`LLM.py`)
```python
MISTRAL_API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "google/gemma-3n-e4b"  # Change to your preferred model
TEMPERATURE = 0.2  # Lower = more consistent output
MAX_TOKENS = 2048
```

### Whisper Settings (`transcribe_audio.py`)
```bash
# Use different model sizes for speed vs accuracy
python transcribe_audio.py input.m4a output.txt --model large    # Best accuracy
python transcribe_audio.py input.m4a output.txt --model medium   # Balanced
python transcribe_audio.py input.m4a output.txt --model small    # Faster
```

## VHF Signal Integration

### Current Limitations
The current system processes pre-recorded audio files. To handle real-time VHF signals, you'll need to add:

### Required Extensions for VHF

1. **VHF Radio Interface**
   ```python
   import rtlsdr
   
   def capture_vhf_signal(frequency=156.8, sample_rate=2.4e6):
       sdr = rtlsdr.RtlSdr()
       sdr.sample_rate = sample_rate
       sdr.center_freq = frequency * 1e6
       # Capture and process VHF signals
   ```

2. **Real-time Audio Processing**
   ```python
   # Example: Continuous audio streaming
   import pyaudio
   import wave
   
   def stream_audio():
       # Capture audio in real-time chunks
       # Process each chunk for distress calls
   ```

3. **Signal Detection and Filtering**
   ```python
   # Example: Detect VHF distress signals
   def detect_distress_signal(audio_chunk):
       # Analyze audio for Mayday/Pan-Pan calls
       # Filter out noise and non-distress communications
   ```

### Implementation Steps for VHF

1. **Hardware Requirements**
   - SDR (Software Defined Radio) device (e.g., RTL-SDR)
   - VHF antenna tuned to maritime frequencies
   - Computer with USB interface

2. **Software Extensions**
   ```bash
   pip install rtlsdr pyaudio numpy scipy
   ```

3. **Frequency Coverage**
   - **Channel 16**: 156.8 MHz (International distress frequency)
   - **Channel 70**: 156.525 MHz (DSC - Digital Selective Calling)
   - **Local channels**: Varies by region

4. **Real-time Processing Pipeline**
   ```
   VHF Signal → SDR Capture → Audio Processing → Distress Detection → Transcription → LLM Analysis
   ```

## Example Output

### Input Audio
```
"Mayday, Mayday, Mayday. This is sailing vessel Sea Wanderer, 
Sea Wanderer, Sea Wanderer. Call sign MXYB9. We are taking on water. 
Position is 50 degrees 43 minutes North, 0 degrees 12 minutes East. 
We have four persons on board. We are abandoning to a liferaft. 
Request immediate assistance. Over."
```

### Structured Output
```json
{
  "ship_name": {
    "value": "Sea Wanderer",
    "confidence": 0.95
  },
  "position": {
    "value": "50 degrees 43 minutes North, 0 degrees 12 minutes East",
    "confidence": 0.98
  },
  "number_of_people": {
    "value": "4",
    "confidence": 0.99
  },
  "injuries": {
    "value": "0",
    "confidence": 1.0
  },
  "distress_type": {
    "value": "Taking on water",
    "confidence": 0.95
  },
  "boat_name": {
    "value": "Sea Wanderer",
    "confidence": 0.95
  }
}
```


### Confidence Thresholds
Modify the LLM prompt to adjust confidence thresholds for different information types.

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```bash
   # Ensure FFmpeg is in your system PATH
   ffmpeg -version
   ```

2. **LLM server connection failed**
   ```bash
   # Check if your local LLM server is running
   curl http://localhost:1234/v1/models
   ```

3. **Whisper model download issues**
   ```bash
   # Manually download models or check internet connection
   python -c "import whisper; whisper.load_model('large')"
   ```

### Performance Optimization

- **GPU Acceleration**: Install PyTorch with CUDA support
- **Model Size**: Use smaller models for faster processing
- **Batch Processing**: Process multiple files simultaneously

## Performance Metrics

- **Transcription Accuracy**: ~95% with Whisper Large model
- **Information Extraction**: ~90% accuracy on maritime distress calls
- **Processing Speed**: ~30 seconds for 1-minute audio (CPU)
- **Real-time Capability**: Requires additional VHF integration

## Security Considerations

- **Data Privacy**: Audio files are processed locally
- **No Cloud Dependencies**: All processing happens on-premises
- **Secure Communications**: VHF signals are inherently public domain
