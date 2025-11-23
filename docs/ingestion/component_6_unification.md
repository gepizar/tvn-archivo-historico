# Component 6: Chunk Object Unification

## Purpose

Combine all enriched data from previous components into a unified **chunk object** that serves as the complete, queryable record for each chunk.

## Process

For each chunk, aggregate data from:
- Component 1: Basic metadata and temporal boundaries
- Component 2: Audio transcripts, speakers, dialogue
- Component 3: Face tracks, character IDs, actor IDs
- Component 4: Character-dialogue mappings
- Component 5: Scene descriptions and visual context

Create a unified chunk object with all this information.

## Chunk Object Structure

### Basic Metadata
- **Show ID**: Identifier for the show/series
- **Season**: Season number
- **Episode**: Episode number
- **Chunk ID**: Unique identifier for this chunk
- **Time range**: Start and end timestamps (precise)
- **Overlap indicators**: Which adjacent chunks overlap with this one
- **Duration**: Chunk duration in seconds

### Characters and Actors
- **Characters present**: List of character IDs that appear visually in this chunk
- **Characters speaking**: List of character IDs that speak in this chunk
- **Actors**: List of actor IDs associated with characters (if available)
- **Character metadata**: For each character:
  - Character ID
  - Actor ID (if known)
  - Visual presence time ranges
  - Speaking time ranges

### Dialogue
- **Dialogue segments**: For each speaking character:
  - Character ID
  - Dialogue text
  - Start/end timestamps within chunk
  - Confidence score for character attribution
- **Full transcript**: Complete transcript for the chunk (optional, can be reconstructed)
- **Speaker-to-character mappings**: Links between anonymous speakers and characters

### Visual Situation (from VLM)
- **Location/Environment**: Structured tags (forest, desert, city, etc.)
- **Actions**: List of main actions
- **Objects**: Notable objects present
- **Visual Context**: Camera style, distance, perspective, crowd size
- **Mood/Atmosphere**: Emotional tone
- **Natural Language Caption**: Short, human-readable scene summary

### Face Information
- **Face tracks**: List of face tracks in this chunk:
  - Face track ID
  - Character ID (if known)
  - Actor ID (if known)
  - Time ranges
  - Bounding boxes
- **Face embeddings**: Vector representations (for similarity search)
- **Cluster associations**: Character cluster and actor cluster IDs

### Audio Information
- **Audio embeddings**: Speaker embeddings for each speaker segment
- **Audio clusters**: Cluster IDs for voice similarity
- **Audio quality metrics**: Optional quality indicators

## Result

Each chunk becomes a rich, multimodal "record" that fuses:
- **Audio**: Transcripts, speakers, dialogue
- **Video**: Faces, characters, actors
- **Context**: Location, actions, mood, visual description

This unified structure enables:
- Semantic search across all modalities
- Structured filtering by any field
- Combined queries (e.g., "desert scenes where Character X talks about Y")
- Efficient retrieval and ranking

## Storage

Chunk objects are stored using the [Storage Interface](../shared/storage_interface.md) and made available to the [Retrieval Pipeline](../retrieval/overview.md).

## Schema Definition

See [Data Models](../shared/data_models.md) for the complete, formal schema definition of chunk objects.

## Related Documentation

- [Ingestion Pipeline Overview](./overview.md)
- [Data Flow](./data_flow.md)
- [Chunk Object Schema](../shared/data_models.md)
- [Storage Interface](../shared/storage_interface.md)
- [Retrieval Pipeline](../retrieval/overview.md)

