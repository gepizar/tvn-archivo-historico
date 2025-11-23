# System Architecture

## Overview

This system processes video content by breaking it down into overlapping time-based chunks and enriching each chunk with multimodal data. The **chunk ID** serves as the central join key that unifies all components.

## System Phases

The system consists of three main phases:

### 1. Ingestion Pipeline
Processes raw video content and enriches it with multimodal data (audio, visual, and contextual information).

**Components:**
1. Episode ingestion and segmentation
2. Audio pipeline (ASR, speaker diarization, clustering)
3. Visual pipeline (face detection, tracking, character/actor identification)
4. Speaker-face linking
5. Scene understanding (VLM-based)
6. Chunk object unification

**Documentation:** [Ingestion Pipeline](./ingestion/overview.md)

### 2. Retrieval Pipeline
Enables queryable access to the enriched chunk objects, supporting semantic search, structured filtering, and combined queries.

**Capabilities:**
- Semantic and text-based queries
- Structured filtering (by character, actor, show, location, etc.)
- Combined queries (semantic + structured)
- Overlap handling and deduplication

**Documentation:** [Retrieval Pipeline](./retrieval/overview.md)

### 3. UI Layer
Provides the user interface for searching, browsing, and exploring the enriched video content.

**Documentation:** [UI Layer](./ui/overview.md)

## Key Design Principles

### Chunk ID as Central Join Key

The **chunk ID** serves as the central join key that:
- Unifies all components in the ingestion pipeline
- Enables efficient retrieval and querying
- Ensures data consistency across all processing stages

### Overlapping Chunks

- **Chunk duration**: 2-3 minutes (configurable)
- **Overlap**: 15-30 seconds between consecutive chunks (configurable)
- Overlap ensures no dialogue or visual context is lost at boundaries
- Overlap metadata is stored for deduplication in retrieval

### Separation of Concerns

- **Ingestion**: Produces chunk objects (stable data contract)
- **Retrieval**: Consumes chunk objects (flexible implementation)
- **UI**: Consumes retrieval API (independent development)

### Never Force VLM to Guess Character Identities

The VLM focuses on visual understanding (location, actions, objects, mood). Character identification comes from face recognition and speaker linking, ensuring reliable character data.

## System Flow

```
Video File
    ↓
[Ingestion Pipeline]
    ├── [1] Time-based Segmentation → Overlapping Chunk IDs
    ├── [2] Audio Pipeline → Speakers + Transcripts + Audio Clusters
    ├── [3] Visual Pipeline → Faces + Character Clusters + Actor IDs
    ├── [4] Speaker-Face Linking → Character-Dialogue Mapping
    ├── [5] VLM Analysis → Chunk Descriptions (location, actions, mood)
    └── [6] Chunk Object Unification → Rich Multimodal Records
    ↓
Storage → Chunk Objects
    ↓
[Retrieval Pipeline]
    └── Query Processing → Searchable Database
    ↓
[UI Layer]
    └── User Interface → Search, Browse, Explore
```

## Documentation Structure

### Domain-Specific Documentation

- **[Ingestion Pipeline](./ingestion/)** - Detailed documentation for all ingestion components
- **[Retrieval Pipeline](./retrieval/)** - Retrieval design, query patterns, and API contract
- **[UI Layer](./ui/)** - UI architecture, user flows, and data presentation

### Shared Documentation

- **[Data Models](./shared/data_models.md)** - Chunk object schema and data contracts
- **[Storage Interface](./shared/storage_interface.md)** - Storage layer interface
- **[Glossary](./shared/glossary.md)** - Terms and definitions

### Technical Documentation

- **[Technical Architecture](./technical_architecture/)** - Technology stack, deployment, performance

## Related Documentation

- [Problem Description](./problem_description.md) - System requirements and goals
- [Ingestion Pipeline Overview](./ingestion/overview.md)
- [Retrieval Pipeline Overview](./retrieval/overview.md)
- [UI Layer Overview](./ui/overview.md)
- [Chunk Object Schema](./shared/data_models.md)
