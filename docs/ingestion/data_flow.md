# Ingestion Pipeline Data Flow

## Overview

This document describes how data flows through the ingestion pipeline, including dependencies, parallelization opportunities, and data transformations.

## Sequential Flow

```
Video File
    ↓
[1] Episode Ingestion and Segmentation
    ├── Output: Chunk IDs, temporal boundaries, audio segments, video segments
    └── Creates: Foundation for all subsequent processing
    ↓
[2] Audio Pipeline (ASR + Diarization + Clustering)
    ├── Input: Audio segments from Component 1
    ├── Output: Transcripts, speaker segments, audio embeddings, audio clusters
    └── Can run in parallel with Components 3 and 5
    ↓
[3] Visual Pipeline (Face Detection + Tracking + Clustering)
    ├── Input: Video segments from Component 1
    ├── Output: Face tracks, character IDs, actor IDs, face embeddings
    └── Can run in parallel with Components 2 and 5
    ↓
[4] Speaker-Face Linking
    ├── Input: Speaker segments (Component 2) + Face tracks (Component 3)
    ├── Output: Character-dialogue mappings
    └── Depends on: Components 2 and 3
    ↓
[5] Scene Understanding (VLM)
    ├── Input: Video segments from Component 1
    ├── Output: Scene descriptions, location, actions, objects, mood
    └── Can run in parallel with Components 2-3
    ↓
[6] Chunk Object Unification
    ├── Input: All outputs from Components 1-5
    ├── Output: Unified chunk objects
    └── Depends on: All previous components
    ↓
Storage
    └── Chunk objects ready for retrieval
```

## Component Dependencies

### Dependency Graph

```
Component 1 (Segmentation)
    ├──→ Component 2 (Audio) [parallel with 3]
    ├──→ Component 3 (Visual) [parallel with 2]
    └──→ Component 5 (Scene Understanding) [parallel with 2-3]

Component 2 (Audio)  ──┐
                       ├──→ Component 4 (Linking)
Component 3 (Visual) ──┘

Component 2 (Audio)   ──┐
Component 3 (Visual)  ──┤
Component 4 (Linking)  ─┤
Component 5 (Scene)  ───┼──→ Component 6 (Unification)
Component 1 (Metadata) ─┘
```

### Parallelization Opportunities

1. **Components 2 and 3** can run in parallel after Component 1 completes
2. **Component 5** can run in parallel with Components 2-3 (only depends on Component 1)
3. **Component 4** must wait for both Components 2 and 3
4. **Component 6** must wait for all previous components

## Data Transformations

### Component 1 → Component 2
- **Input**: Raw video file
- **Output**: Audio segments per chunk
- **Transformation**: Extract audio, segment by time boundaries

### Component 1 → Component 3
- **Input**: Raw video file
- **Output**: Video segments per chunk
- **Transformation**: Extract video segments, optionally downsample

### Component 2 → Component 4
- **Input**: Speaker segments with timestamps
- **Output**: Speaker segments with character attributions
- **Transformation**: Link speakers to faces, assign character IDs

### Component 3 → Component 4
- **Input**: Face tracks with timestamps
- **Output**: Face tracks linked to speakers
- **Transformation**: Temporal alignment, speaker-face association

### Components 1-5 → Component 6
- **Input**: All enriched data from previous components
- **Output**: Unified chunk objects
- **Transformation**: Aggregate, structure, and validate all data

## Chunk ID Propagation

The **chunk ID** from Component 1 propagates through all components:
- Component 1: Creates chunk ID
- Components 2-5: Attach data to chunk ID
- Component 6: Unifies all data under chunk ID
- Storage: Chunk ID is the primary key

## Overlap Handling

Overlapping chunks create duplicate data that must be handled:
- **During ingestion**: Each chunk processes its full time range independently
- **During storage**: All chunk objects are stored, including overlaps
- **During retrieval**: Deduplication and merging handled by retrieval pipeline

## Error Handling and Recovery

- **Component failures**: Can retry individual components without reprocessing entire pipeline
- **Partial data**: Chunk objects can be stored with partial data if some components fail
- **Data validation**: Component 6 validates data completeness before storage
- **Idempotency**: Components should be idempotent (can be rerun safely)

## Performance Considerations

- **Parallelization**: Maximize parallel execution of independent components
- **Caching**: Cache intermediate results (embeddings, clusters) for reuse
- **Batch processing**: Process multiple chunks in batches where possible
- **Resource management**: Balance CPU, GPU, and I/O resources across components

## Related Documentation

- [Ingestion Pipeline Overview](./overview.md)
- [Storage Interface](../shared/storage_interface.md)
- [Retrieval Pipeline](../retrieval/overview.md)

