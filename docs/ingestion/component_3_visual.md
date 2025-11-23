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

### 3. Assign Character IDs
- Manually label major recurring clusters at the beginning (e.g., "Cluster A = Jon Snow")
- Propagate labels across all chunks where that cluster appears
- Maintain character identity throughout the series
- Handle character appearance changes (aging, makeup, costume changes)
- Support for minor/recurring characters

### 4. Assign Actor IDs (cross-series)
- Compare face embeddings across different shows
- When a cluster from Show 1 is extremely similar to a cluster from Show 2, treat them as the same actor
- Assign shared actor ID for cross-series actor recognition
- Enable queries like "all scenes where this actor appears in any series"

## Output per Chunk

- **Face tracks**: 
  - Face track ID
  - Time ranges within chunk
  - Bounding boxes and positions
  - Frame indices
- **Character IDs**: Which characters appear in the chunk
- **Actor IDs**: Which actors are present (if cross-series matching is enabled)
- **Face embeddings**: Vector representations for each face track
- **Cluster associations**: Character cluster and actor cluster assignments

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

