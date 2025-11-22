# System Architecture

This system processes video content by breaking it down into overlapping time-based chunks and enriching each chunk with multimodal data. The **chunk ID** serves as the central join key that unifies all components.

## Overview

The system consists of two main phases:

### Ingestion Pipeline (Components 1-6)
Processes raw video content and enriches it with multimodal data:

1. **Episode ingestion and segmentation** - Split video into overlapping time-based chunks
2. **Audio pipeline** - ASR, speaker diarization, and clustering
3. **Visual pipeline** - Face detection, tracking, and character/actor identification
4. **Speaker-face linking** - Associate audio speakers with visual characters
5. **Scene understanding** - VLM-based visual context analysis
6. **Chunk object unification** - Combine all data into rich chunk records

### Retrieval Pipeline (Component 7)
Enables queryable access to the enriched chunk objects:

7. **Retrieval pipeline** - Query and retrieve chunk data with support for semantic search, structured filtering, and deduplication

---

The **chunk ID** serves as the central join key that unifies all components in the ingestion pipeline and enables efficient retrieval.

---

## 1. Episode Ingestion and Segmentation

### Process

1. **Ingest raw video** - Load episode or movie file
2. **Create overlapping time-based chunks** - Segment video into fixed-duration, overlapping windows:
   - **Chunk duration**: 2-3 minutes (configurable)
   - **Overlap**: 15-30 seconds between consecutive chunks (configurable)
   - Each chunk receives a unique **chunk ID**
   - Store precise start/end timestamps for each chunk
   - Overlap ensures no dialogue or visual context is lost at boundaries
3. **Extract chunk assets**:
   - Extract corresponding **audio segment** for each chunk
   - Extract the **full chunk video** for visual analysis and VLM processing
   - Video may be downsampled (frame rate reduction) for efficiency while preserving temporal continuity

### Rationale

- **Robustness**: Avoids dependency on imperfect scene detection algorithms
- **Dialogue continuity**: Prevents cutting words at boundaries, preserves full conversations
- **VLM compatibility**: Modern VLMs (e.g., Qwen) can process longer sequences effectively
- **Simplicity**: More predictable and maintainable than scene detection
- **Trade-off**: Higher compute cost, but more reliable results

### Output

- Chunk IDs with precise temporal boundaries
- Audio segments per chunk
- Full chunk video (potentially downsampled for efficiency)
- Overlap metadata (for deduplication in retrieval)

The chunk ID becomes the **central join key** for all subsequent processing.

---

## 2. Audio Pipeline: ASR + Speaker Diarization + Clustering

### Process

1. **Automatic Speech Recognition (ASR)**
   - Generate timestamped transcripts for each episode
   - Map spoken segments to time ranges

2. **Speaker Diarization**
   - Segment audio into contiguous **speaker segments** (Speaker 1, Speaker 2, etc.)
   - Each segment has start and end timestamps
   - Speakers are initially anonymous

3. **Extract Audio Embeddings**
   - Use speaker verification models to generate vector representations
   - Create embeddings for each speaker segment
   - Store embeddings alongside speaker metadata

4. **Cluster Audio Embeddings**
   - Cluster embeddings across episode or entire series
   - Generate **anonymous audio clusters** (Audio Cluster A, B, etc.)
   - Use clustering algorithms (DBSCAN, HDBSCAN, or hierarchical clustering)
   - Handle voice variations (emotion, age, accent) within the same speaker

5. **Map Speakers to Chunks**
   - Determine which chunk(s) each speaker segment belongs to (based on timestamps)
   - A speaker segment may span multiple chunks or fall within chunk overlap regions
   - Attach speaker segment (speaker ID + text + audio cluster) to corresponding chunk(s)

### Output per Chunk

- Transcript segments
- List of anonymous speakers with their dialogue and time ranges
- Audio embeddings and audio clusters for each speaker segment
- Note: Overlapping chunks may contain duplicate speaker segments (handled in retrieval deduplication)

---

## 3. Visual Pipeline: Faces, Characters, and Actors

### Process

1. **Face Detection and Tracking**
   - For each chunk's full video:
     - Run **face detection** to identify all faces across all frames
     - Use **face tracking** across frames to build continuous **face tracks**
     - Track the same person across multiple frames/seconds within a chunk
     - Processing the full video ensures no faces are missed and tracking is more robust

2. **Face Embedding and Clustering**
   - For each face track:
     - Compute **face embeddings** (vector representations of appearance)
     - Cluster embeddings across episode or entire series
     - Generate **anonymous character clusters** (Cluster A, Cluster B, etc.)

3. **Assign Character IDs**
   - Manually label major recurring clusters at the beginning (e.g., "Cluster A = Jon Snow")
   - Propagate labels across all chunks where that cluster appears
   - Maintain character identity throughout the series

4. **Assign Actor IDs** (cross-series)
   - Compare face embeddings across different shows
   - When a cluster from Show 1 is extremely similar to a cluster from Show 2, treat them as the same actor
   - Assign shared actor ID for cross-series actor recognition

### Output per Chunk

- Face tracks that appear in the chunk
- Character IDs (and optionally actor IDs) present in that chunk
- Face embeddings and cluster associations

---

## 4. Linking Speakers to Faces

### Process

1. **Temporal Alignment**
   - For each **speaker segment** (from diarization), examine the same time interval in the video
   - Identify which face tracks are visible during that period

2. **Speaker-Face Association**
   - Apply heuristics to link speakers to faces:
     - If only one character's face is on screen → assume that's the active speaker
     - If multiple faces → use heuristics:
       - Foreground/background position
       - Mouth movement detection
       - Center of frame positioning
       - Face size/zoom level

3. **Character Attribution**
   - Once a speaker is linked to a face track:
     - Attach the corresponding **character ID** to that speaker segment
     - Build robust mapping: "Speaker 2" in audio → "Character X" in visuals
     - Refine associations over time as more data accumulates

### Output per Chunk

- Which characters appear visually
- Which characters actually speak
- Exact dialogue delivered by each speaking character
- Temporal alignment between speech and visual presence

---

## 5. Scene Understanding with VLM

### Process

1. **VLM Input**
   - For each chunk, use the **full chunk video** (potentially downsampled for efficiency) as input to a **Vision-Language Model (VLM)**
   - Modern VLMs (e.g., Qwen) can process longer sequences (tens of minutes), making 2-3 minute chunks well-suited
   - Processing the full video captures complete visual dynamics, temporal context, and scene evolution

2. **Structured Scene Description**
   - Prompt the VLM to output a **rich, structured description**:
     - **Location/Environment**: forest, desert, city, interior car, night/day, etc.
     - **Main Actions**: walking, driving, fighting, talking, hiding, etc.
     - **Notable Objects**: cars, weapons, trees, buildings, props, etc.
     - **Visual Context**: camera style, distance, perspective, crowd vs. intimate
     - **Natural Language Caption**: short, human-readable summary

3. **Attach to Chunk**
   - Link the chunk-level description to the **chunk ID**
   - Create a "semantic fingerprint" of the visual situation
   - Note: Overlapping chunks may have similar descriptions (handled in retrieval deduplication)

### Examples

- "Driving through a desert at sunset"
- "Walking in a dense forest with several people"
- "Two characters arguing in a small kitchen at night"

### Important Note

The VLM does **not** need to know character names. It only describes **what's visually going on** - the system handles character identification separately.

---

## 6. Unifying Everything into a "Chunk Object"

For each chunk, create a unified **chunk object** that contains:

### Basic Metadata
- Show, episode, season
- Time range (start/end timestamps)
- Chunk ID
- Overlap indicators (which adjacent chunks overlap with this one)

### Characters and Actors
- Which characters appear in the chunk
- Which characters speak in this chunk
- Which actors are associated with those characters (if available)

### Dialogue
- What each speaking character says
- Timestamps for each dialogue segment
- Speaker-to-character mappings

### Visual Situation (from VLM)
- Location/setting (forest, desert, city street, interior car, courtroom, etc.)
- Actions, objects, and mood
- Short, human-readable scene caption

### Face Information
- Face tracks that appear in this chunk
- Face clusters and embeddings
- Character/actor associations

### Result

Each chunk becomes a rich, multimodal "record" that fuses:
- Audio (transcripts, speakers, dialogue)
- Video (faces, characters, actors)
- Context (location, actions, mood, visual description)

---

## 7. Retrieval Pipeline

Build a retrieval layer that enables queryable access to the unified chunk objects, supporting flexible query patterns and future retrieval strategies.

### Retrieval Capabilities

1. **Semantic and Text-based Queries**
   - Support natural language queries over dialogue and chunk descriptions
   - Enable semantic search across multimodal content
   - Example queries:
     - "Chunks where Jon Snow talks about honor"
     - "Chunks where characters argue in a kitchen at night"
     - "Driving chunks in the desert where the conversation is tense"

2. **Structured Filtering**
   - Filter by:
     - Character IDs
     - Actor IDs
     - Show, episode, season
     - Location tags
     - Time ranges
   - Example queries:
     - "Forest chunks with at least three characters, including Character X"
     - "All chunks where this actor appears in any series"

3. **Combined Queries**
   - Combine semantic search with structured filters:
     - "All desert driving chunks at sunset where Walter White is present, even if he doesn't speak"
     - "Chunks in the forest with people hiding or sneaking, where this actor appears"

4. **Overlap Handling**
   - Handle overlapping chunks in results:
     - **Temporal deduplication**: Group results by time ranges, showing the most relevant chunk per time period
     - **Ranking**: Prioritize chunks with higher relevance scores or more complete data
     - **Merge results**: Merge metadata from overlapping chunks for richer results
   - Users can optionally request "all overlapping chunks" for comprehensive coverage

### Implementation Flexibility

The retrieval implementation can evolve over time:
- Initial implementation may use traditional search indexing (vector search, keyword search)
- Future implementations may leverage GraphRAG, context-aware retrieval, or other advanced techniques
- The chunk object structure remains stable regardless of retrieval strategy

### Design Principle

**Never force the VLM to guess character identities.**

Instead, the **chunk ID** acts as the hub where:
- Audio (ASR + diarization)
- Visual character/actor recognition
- VLM scene understanding

are all joined together into a single, queryable representation.

Specific retrieval implementation details (indexing strategies, algorithms, technologies) are documented in the technical architecture.

---

## System Flow Summary

```
Video File
    ↓
[1] Time-based Segmentation → Overlapping Chunk IDs (2-3 min chunks, 15-30s overlap)
    ↓
[2] Audio Pipeline → Speakers + Transcripts + Audio Clusters
    ↓
[3] Visual Pipeline → Faces + Character Clusters + Actor IDs
    ↓
[4] Speaker-Face Linking → Character-Dialogue Mapping
    ↓
[5] VLM Analysis → Chunk Descriptions (location, actions, mood)
    ↓
[6] Chunk Object Unification → Rich Multimodal Records
    ↓
[7] Retrieval Pipeline → Queryable Database (with deduplication)
```

Each component enriches the chunk objects, and the chunk ID ensures all data is properly associated and queryable. Overlapping chunks provide robustness and prevent information loss at boundaries.

