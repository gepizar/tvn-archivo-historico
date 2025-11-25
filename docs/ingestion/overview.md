# Ingestion Pipeline Overview

## Purpose

The ingestion pipeline processes raw video content and enriches it with multimodal data (audio, visual, and contextual information) to create rich, queryable chunk objects. The pipeline is **content-type agnostic**—it works identically for TV series, news programs, talk shows, documentaries, and other content types. Content-specific associations (characters, roles, actors) are assigned during the curation/labeling phase.

## Pipeline Components

The ingestion pipeline consists of six sequential components:

1. **Episode Ingestion and Segmentation** - Split video into overlapping time-based chunks
2. **Audio Pipeline** - ASR, speaker diarization, and clustering
3. **Visual Pipeline** - Face detection, tracking, and clustering
4. **Speaker-Face Linking** - Associate audio speakers with visual characters
5. **Scene Understanding** - VLM-based visual context analysis
6. **Chunk Object Unification** - Combine all data into rich chunk records

## Key Design Principles

### Chunk ID as Central Join Key

The **chunk ID** serves as the central join key that unifies all components in the ingestion pipeline. Each chunk receives a unique identifier that enables:
- Efficient data association across all processing stages
- Reliable retrieval and querying
- Overlap handling and deduplication

### Overlapping Chunks

- **Chunk duration**: 2-3 minutes (configurable)
- **Overlap**: 15-30 seconds between consecutive chunks (configurable)
- Overlap ensures no dialogue or visual context is lost at boundaries
- Overlap metadata is stored for deduplication in retrieval

### Multimodal Enrichment

Each chunk is enriched with:
- **Audio**: Transcripts, speaker segments, dialogue, audio embeddings
- **Visual**: Face tracks, person clusters (anonymous), face embeddings
- **Context**: Location, actions, objects, mood, scene descriptions (from VLM)
- **Metadata**: Show/program, episode, season, content type, timestamps, overlap indicators

**Note**: The ingestion pipeline creates **anonymous person clusters** (not character/actor IDs). Person identities, roles, and character associations are assigned during curation.

## Data Flow

```
Video File
    ↓
[1] Time-based Segmentation → Overlapping Chunk IDs (2-3 min chunks, 15-30s overlap)
    ↓
[2] Audio Pipeline → Speakers + Transcripts + Anonymous Audio Clusters
    ↓
[3] Visual Pipeline → Faces + Anonymous Person Clusters
    ↓
[4] Speaker-Face Linking → Anonymous Speaker-Face Mappings
    ↓
[5] VLM Analysis → Chunk Descriptions (location, actions, mood)
    ↓
[6] Chunk Object Unification → Rich Multimodal Records (pending_labeling)
    ↓
Storage → Chunk Objects (pending_labeling state)
    ↓
[Curation/Labeling Pipeline] → Person IDs assigned, with optional:
    ├── Character IDs (for fictional content)
    ├── Actor IDs (for fictional content)
    └── Roles (for non-fictional content, e.g., "news anchor", "reporter")
    ↓
Storage → Chunk Objects (approved, ready for retrieval)
```

## Component Dependencies

- **Component 1** (Segmentation) is independent and must run first
- **Components 2, 3, and 5** (Audio, Visual, and Scene Understanding) can run in parallel after Component 1
- **Component 4** (Linking) depends on both Components 2 and 3
- **Component 6** (Unification) depends on all previous components

## Output

The ingestion pipeline produces **chunk objects** in `pending_labeling` state. These objects contain:
- All multimodal data (audio, visual, contextual)
- **Anonymous person clusters** (no person/character/actor IDs yet)
- Content type metadata (from show/program metadata)
- Ready for the [Curation/Labeling Pipeline](../curation/overview.md)

After labeling, chunk objects move to `approved` state and are available for the retrieval pipeline. The curation layer assigns:
- **Person IDs** (always assigned)
- **Character IDs** (optional, for fictional content like TV series)
- **Actor IDs** (optional, for fictional content)
- **Roles** (optional, for non-fictional content like news programs, e.g., "news anchor", "reporter")

See [Data Models](../shared/data_models.md) for the complete chunk object schema.

## Related Documentation

- [Component 1: Segmentation](./component_1_segmentation.md)
- [Component 2: Audio Pipeline](./component_2_audio.md)
- [Component 3: Visual Pipeline](./component_3_visual.md)
- [Component 4: Speaker-Face Linking](./component_4_linking.md)
- [Component 5: Scene Understanding](./component_5_scene_understanding.md)
- [Component 6: Unification](./component_6_unification.md)
- [Data Flow](./data_flow.md)
- [Chunk Object Schema](../shared/data_models.md)
- [Curation/Labeling Pipeline](../curation/overview.md) - Character and actor ID assignment

