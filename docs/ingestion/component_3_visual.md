# Component 3: Visual Pipeline (Faces, Characters, and Actors)

## Purpose

Detect and track faces, cluster them into characters, and identify actors across different series.

## Process

### 1. Face Detection and Tracking
For each chunk's full video:
- Run **face detection** to identify all faces across all frames
- Use **face tracking** across frames to build continuous **face tracks**
- Track the same person across multiple frames/seconds within a chunk
- Processing the full video ensures no faces are missed and tracking is more robust
- Handle occlusions, profile views, and partial faces

### 2. Face Embedding and Clustering
For each face track:
- Compute **face embeddings** (vector representations of appearance)
- Extract embeddings at multiple points in the track for robustness
- Cluster embeddings across episode or entire series
- Generate **anonymous character clusters** (Cluster A, Cluster B, etc.)
- Handle variations in lighting, angle, age, makeup, etc.
- Store cluster IDs and embeddings for later labeling

**Note:** Character and actor IDs are assigned in the [Curation/Labeling Pipeline](../curation/overview.md), not during ingestion. This allows the ingestion pipeline to run continuously without manual intervention.

## Output per Chunk

- **Face tracks**: 
  - Face track ID
  - Time ranges within chunk
  - Bounding boxes and positions
  - Frame indices
- **Anonymous character clusters**: Cluster IDs (Cluster A, B, C, etc.) - no character names yet
- **Face embeddings**: Vector representations for each face track
- **Cluster associations**: Which anonymous clusters appear in the chunk

**Note:** Character IDs and Actor IDs are assigned later in the [Curation/Labeling Pipeline](../curation/overview.md). The ingestion pipeline only produces anonymous clusters to avoid blocking on manual labeling.

## Key Considerations

### Face Tracking Challenges
- Occlusions and partial visibility
- Profile views vs. frontal views
- Lighting variations
- Fast motion and blur
- Multiple people in frame

### Character Clustering Challenges
- Age progression across seasons
- Makeup and costume changes
- Weight changes
- Facial hair changes
- Twins or similar-looking characters

### Actor Recognition Challenges
- Different roles with different appearances
- Age differences between shows
- Makeup and prosthetics
- Facial hair and hairstyle changes

## Related Documentation

- [Ingestion Pipeline Overview](./overview.md)
- [Component 4: Speaker-Face Linking](./component_4_linking.md)
- [Data Flow](./data_flow.md)
- [Curation/Labeling Pipeline](../curation/overview.md) - Character and actor ID assignment

