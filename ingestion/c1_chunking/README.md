# Component 1: Video Chunking

Video chunking service that splits videos into overlapping time-based segments.

## Requirements

- Python 3.10+
- `ffmpeg` and `ffprobe` (must be installed on your system)

## Installation

Using `uv`:

```bash
uv sync
```

## Usage

### Command Line

Chunk a video into overlapping segments:

```bash
# Basic usage (2 min chunks, 15 sec overlap)
uv run python chunk_video.py video.mp4

# Custom duration and overlap
uv run python chunk_video.py video.mp4 --chunk-duration 180 --overlap 20

# Specify output directory
uv run python chunk_video.py video.mp4 --output-dir ./chunks

# Custom chunk prefix
uv run python chunk_video.py video.mp4 --chunk-prefix episode_001
```

### Programmatic Usage

```python
from config.chunking_config import ChunkingConfig
from services.video_chunker import VideoChunker

# Create configuration
config = ChunkingConfig(
    chunk_duration_seconds=120,  # 2 minutes
    overlap_seconds=15           # 15 seconds
)

# Create chunker
chunker = VideoChunker(config)

# Chunk video
chunks = chunker.chunk_video(
    video_path="video.mp4",
    output_dir="./chunks",
    chunk_prefix="chunk"
)

# Access chunk metadata
for chunk in chunks:
    print(f"{chunk.chunk_id}: {chunk.start_time}s - {chunk.end_time}s")
```

## Configuration

Default settings:
- **Chunk duration**: 120 seconds (2 minutes)
- **Overlap**: 15 seconds

Both are configurable via `ChunkingConfig` or command-line arguments.

## Output

Each chunk includes:
- Unique chunk ID
- Start/end timestamps
- Extracted video file
