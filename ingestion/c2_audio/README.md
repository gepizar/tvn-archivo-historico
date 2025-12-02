# Component 2: Audio Transcription & Diarization

Minimalistic proof of concept for transcribing and diarizing audio files using NVIDIA NeMo models.

## Overview

This component processes audio files (generated from `c1_chunking`) to:
- **Transcribe** audio into text with timestamps
- **Diarize** audio to identify different speakers
- Output speaker-tagged transcripts in JSON format

## Requirements

- Python 3.10+
- CUDA-capable GPU (recommended) or CPU
- `ffmpeg` and system audio libraries

## Quick Start

Check if dependencies are installed:

```bash
uv run python check_dependencies.py
```

## Installation

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
apt-get update && apt-get install -y libsndfile1 ffmpeg

# macOS (using Homebrew)
brew install libsndfile ffmpeg
```

### 2. Install Python Dependencies

Using `uv`:

```bash
uv sync
```

Or manually:

```bash
# Install build dependencies
pip install Cython packaging

# Install NeMo (this may take a while)
pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]

# Install other dependencies
pip install -r requirements.txt
```

## Usage

### Command Line

Process a single audio file:

```bash
# Basic usage
uv run python process_audio.py audio.wav

# Specify output file
uv run python process_audio.py audio.wav --output transcript.json

# Process all audio files in a directory
uv run python process_audio.py /path/to/audio/dir --output-dir /path/to/output
```

### Process Audio from c1_chunking

If you have audio files from the chunking component:

```bash
# Process all audio chunks
uv run python process_audio.py ./chunks/audio --output-dir ./chunks/transcripts
```

### Programmatic Usage

```python
from config.audio_config import AudioConfig
from process_audio import AudioProcessor

# Create configuration
config = AudioConfig(
    att_context_size=[70, 13]  # 1.12s latency
)

# Initialize processor
processor = AudioProcessor(config)

# Process single file
result = processor.process_audio_file(
    "audio.wav",
    output_path="transcript.json"
)

# Process multiple files
results = processor.process_batch(
    ["audio1.wav", "audio2.wav"],
    output_dir="./transcripts"
)
```

## Configuration

### Audio Requirements

- **Format**: WAV (recommended) or MP3
- **Sample Rate**: 16,000 Hz (automatically resampled if needed)
- **Channels**: Mono (automatically converted if needed)

### Streaming Configuration

The `att_context_size` parameter controls latency vs accuracy tradeoff (measured in 80ms frames):

- `[70, 0]`: Chunk size = 1 (0.08s latency) - fastest, lower accuracy
- `[70, 6]`: Chunk size = 7 (0.56s latency) - balanced
- `[70, 13]`: Chunk size = 14 (1.12s latency) - default, better accuracy

### Models

- **ASR Model**: `nvidia/multitalker-parakeet-streaming-0.6b-v1`
- **Diarization Model**: `nvidia/diar_streaming_sortformer_4spk-v2.1`

Models are automatically downloaded from HuggingFace on first use.

## Output Format

The output JSON contains:

```json
{
  "audio_file": "path/to/audio.wav",
  "segments": [
    {
      "speaker": "Speaker_0",
      "start_time": 0.0,
      "end_time": 2.5,
      "text": "Hello, this is the first speaker."
    },
    {
      "speaker": "Speaker_1",
      "start_time": 2.5,
      "end_time": 5.0,
      "text": "And this is the second speaker."
    }
  ]
}
```

## Performance Notes

- **GPU**: Significantly faster processing (recommended)
- **CPU**: Works but much slower
- **Memory**: Models require ~2-4GB RAM/VRAM
- **Processing Time**: ~1-2x real-time on GPU, ~10-20x on CPU

## Alternative: Using NeMo Example Script

If the direct API approach doesn't work, you can use the NeMo example script directly:

```bash
# First, clone or ensure NeMo is installed
git clone https://github.com/NVIDIA/NeMo.git
cd NeMo

# Run the example script
python examples/asr/asr_cache_aware_streaming/speech_to_text_multitalker_streaming_infer.py \
    asr_model="nvidia/multitalker-parakeet-streaming-0.6b-v1" \
    diar_model="nvidia/diar_streaming_sortformer_4spk-v2.1" \
    att_context_size="[70,13]" \
    generate_realtime_scripts=False \
    audio_file="/path/to/audio.wav" \
    output_path="/path/to/output.json"
```

## Limitations

This is a **minimalistic POC** with the following limitations:

1. **Single audio file processing**: Processes one file at a time (batch mode processes sequentially)
2. **No audio preprocessing**: Assumes audio is already in correct format
3. **Basic output format**: Simple JSON structure (not full SegLST format)
4. **No clustering**: Speaker IDs are per-file (not clustered across files)
5. **Fixed models**: Uses pre-configured model versions

## Troubleshooting

### CUDA Out of Memory

If you encounter CUDA OOM errors:
- Use CPU mode: `--device cpu`
- Process smaller audio files
- Reduce `att_context_size` to `[70, 6]` or `[70, 0]`

### Audio Format Issues

If audio format is incorrect:
- Use `ffmpeg` to convert: `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav`
- Ensure mono channel and 16kHz sample rate

### NeMo Installation Issues

If NeMo installation fails:
- Ensure you have the latest PyTorch installed
- Try installing Cython and packaging first: `pip install Cython packaging`
- Check CUDA compatibility if using GPU

## Related Documentation

- [Component 2 Documentation](../../docs/ingestion/component_2_audio.md)
- [NVIDIA NeMo Documentation](https://github.com/NVIDIA/NeMo)
- [Model Card](../../ingestion/c2_audio/nvidia_readme.md)
