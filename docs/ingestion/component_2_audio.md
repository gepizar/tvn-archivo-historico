# Component 2: Audio Pipeline (ASR + Speaker Diarization + Clustering)

## Purpose

Process audio to extract transcripts, identify speakers, and cluster similar voices across episodes and series.

## Process

### 1. Automatic Speech Recognition (ASR)
- Generate timestamped transcripts for each episode
- Map spoken segments to time ranges
- Handle multiple languages if needed
- Preserve punctuation and capitalization where possible

### 2. Speaker Diarization
- Segment audio into contiguous **speaker segments** (Speaker 1, Speaker 2, etc.)
- Each segment has start and end timestamps
- Speakers are initially anonymous (no character names yet)
- Handle overlapping speech and background noise

### 3. Extract Audio Embeddings
- Use speaker verification models to generate vector representations
- Create embeddings for each speaker segment
- Store embeddings alongside speaker metadata
- Embeddings capture voice characteristics (pitch, tone, accent, etc.)

### 4. Cluster Audio Embeddings
- Cluster embeddings across episode or entire series
- Generate **anonymous audio clusters** (Audio Cluster A, B, etc.)
- Use clustering algorithms (DBSCAN, HDBSCAN, or hierarchical clustering)
- Handle voice variations (emotion, age, accent) within the same speaker
- Account for background noise and audio quality variations

### 5. Map Speakers to Chunks
- Determine which chunk(s) each speaker segment belongs to (based on timestamps)
- A speaker segment may span multiple chunks or fall within chunk overlap regions
- Attach speaker segment (speaker ID + text + audio cluster) to corresponding chunk(s)
- Handle edge cases where speech spans chunk boundaries

## Output per Chunk

- **Transcript segments**: All spoken text with timestamps
- **Speaker segments**: List of anonymous speakers with:
  - Speaker ID (e.g., "Speaker 1", "Speaker 2")
  - Dialogue text
  - Time ranges (start/end within chunk)
  - Audio cluster assignment (e.g., "Audio Cluster A")
- **Audio embeddings**: Vector representations for each speaker segment
- **Audio clusters**: Cluster IDs and metadata

**Note**: Overlapping chunks may contain duplicate speaker segments (handled in retrieval deduplication)

## Key Considerations

### Speaker Clustering Challenges
- Voice variations due to emotion, age progression, or health
- Audio quality differences across episodes
- Background noise and music
- Multiple languages or accents

### Chunk Boundary Handling
- Speaker segments that span multiple chunks
- Segments that fall in overlap regions
- Ensuring all dialogue is captured

## Related Documentation

- [Ingestion Pipeline Overview](./overview.md)
- [Component 4: Speaker-Face Linking](./component_4_linking.md)
- [Data Flow](./data_flow.md)

