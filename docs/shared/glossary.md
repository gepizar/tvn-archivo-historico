# Glossary

## Terms and Definitions

### Chunk
A time-based segment of video content, typically 2-3 minutes in duration, with 15-30 seconds of overlap with adjacent chunks. Each chunk receives a unique **chunk ID** and is enriched with multimodal data.

### Chunk ID
A unique identifier for each chunk, serving as the central join key that unifies all components in the ingestion pipeline and enables efficient retrieval. Format: `{show_id}_{season}_{episode}_{chunk_index}`.

### Chunk Object
The unified data structure that contains all enriched information for a chunk, including audio transcripts, visual character data, scene descriptions, and metadata. Created by Component 6 (Unification) and consumed by the retrieval pipeline.

### Speaker Diarization
The process of segmenting audio into contiguous speaker segments, identifying "who spoke when" without initially knowing character identities.

### Speaker Segment
A contiguous segment of audio attributed to a single speaker, with start/end timestamps. Initially anonymous (Speaker 1, Speaker 2, etc.) until linked to characters.

### Audio Cluster
A group of speaker segments with similar voice characteristics, identified through clustering of audio embeddings. Used to identify recurring speakers across episodes.

### Face Track
A continuous sequence of face detections across multiple frames, tracking the same person within a chunk.

### Character Cluster
A group of face tracks with similar appearance, identified through clustering of face embeddings. Used to identify recurring characters.

### Character ID
A named identifier for a character (e.g., "Jon Snow", "Walter White"). Assigned to character clusters through manual labeling or automated identification.

### Actor ID
An identifier for an actor that can span multiple series. Used for cross-series actor recognition.

### VLM (Vision-Language Model)
A model that processes video and generates natural language descriptions of visual content. Used in Component 5 for scene understanding.

### Overlap
The intentional overlap between consecutive chunks (15-30 seconds) to ensure no dialogue or visual context is lost at boundaries.

### Multimodal
Combining multiple types of data: audio (transcripts, speakers), visual (faces, characters), and contextual (scene descriptions).

## Related Documentation

- [Architecture Overview](../architecture.md)
- [Ingestion Pipeline](../ingestion/overview.md)
- [Retrieval Pipeline](../retrieval/overview.md)

