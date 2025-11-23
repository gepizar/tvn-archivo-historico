# Component 1: Episode Ingestion and Segmentation

## Purpose

Split raw video content into overlapping time-based chunks, creating the foundation for all subsequent processing. Each chunk receives a unique **chunk ID** that serves as the central join key.

## Process

### 1. Ingest Raw Video
- Load episode or movie file
- Validate video format and metadata
- Extract basic metadata (show, episode, season, duration)

### 2. Create Overlapping Time-based Chunks
Segment video into fixed-duration, overlapping windows:
- **Chunk duration**: 2-3 minutes (configurable)
- **Overlap**: 15-30 seconds between consecutive chunks (configurable)
- Each chunk receives a unique **chunk ID**
- Store precise start/end timestamps for each chunk
- Overlap ensures no dialogue or visual context is lost at boundaries

### 3. Extract Chunk Assets
For each chunk:
- Extract corresponding **audio segment** for each chunk
- Extract the **full chunk video** for visual analysis and VLM processing
- Video may be downsampled (frame rate reduction) for efficiency while preserving temporal continuity

## Rationale

### Why Overlapping Chunks?
- **Robustness**: Avoids dependency on imperfect scene detection algorithms
- **Dialogue continuity**: Prevents cutting words at boundaries, preserves full conversations
- **VLM compatibility**: Modern VLMs (e.g., Qwen) can process longer sequences effectively
- **Simplicity**: More predictable and maintainable than scene detection
- **Trade-off**: Higher compute cost, but more reliable results

### Why Time-based Instead of Scene-based?
- Scene detection is error-prone and inconsistent
- Time-based chunks are deterministic and predictable
- Overlap compensates for boundary issues
- Easier to parallelize and process

## Output

For each chunk:
- **Chunk ID**: Unique identifier (e.g., `show_episode_chunk_001`)
- **Temporal boundaries**: Precise start/end timestamps
- **Audio segment**: Extracted audio file for the chunk time range
- **Full chunk video**: Video segment (potentially downsampled)
- **Overlap metadata**: 
  - Which adjacent chunks overlap with this one
  - Overlap duration and boundaries
  - For deduplication in retrieval

## Chunk ID Format

The chunk ID format should be:
```
{show_id}_{season}_{episode}_{chunk_index}
```

Example: `got_s01_e01_c001`, `bb_s02_e05_c042`

## Configuration Parameters

- `chunk_duration_seconds`: Default 150 (2.5 minutes)
- `overlap_seconds`: Default 20 seconds
- `video_fps`: Optional target frames per second for downsampled video (e.g., 12, 15, 24)
- `audio_sample_rate`: Target audio sample rate for extraction

## Error Handling

- Handle corrupted video files gracefully
- Validate chunk boundaries don't exceed video duration
- Ensure overlap doesn't exceed chunk duration
- Handle edge cases (very short videos, single-frame videos)

## Related Documentation

- [Ingestion Pipeline Overview](./overview.md)
- [Data Flow](./data_flow.md)
- [Storage Interface](../shared/storage_interface.md)

