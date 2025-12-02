# System Architecture

## Overview

This system processes video content by breaking it down into overlapping time-based chunks and enriching each chunk with multimodal data. The **chunk ID** serves as the central join key that unifies all components.

## System Phases

The system consists of four main phases:

### 1. Ingestion Pipeline
Processes raw video content and enriches it with multimodal data (audio, visual, and contextual information). The pipeline is **content-type agnostic**—it works identically for TV series, news programs, talk shows, documentaries, and other content types. Produces chunk objects with anonymous person clusters (no person/character/actor/role labels yet).

**Components:**
1. Program/episode ingestion and chunking
2. Audio pipeline (ASR, speaker diarization, clustering)
3. Visual pipeline (face detection, tracking, anonymous person clustering)
4. Speaker-face linking
5. Scene understanding (VLM-based)
6. Chunk object unification

**Output:** Chunk objects in `pending_labeling` state with anonymous person clusters

**Documentation:** [Ingestion Pipeline](./ingestion/overview.md)

### 2. Curation/Labeling Pipeline
Assigns person IDs to anonymous clusters through manual labeling and/or auto-labeling. For fictional content (TV series), it also assigns character IDs and actor IDs. For non-fictional content (news, talk shows, etc.), it assigns roles (e.g., "news anchor", "reporter", "guest"). This phase runs asynchronously after ingestion, allowing continuous GPU processing while labeling happens separately.

**Process:**
1. Manual labeling interface for person assignment (always required)
2. For fictional content: Character and actor ID assignment
3. For non-fictional content: Role assignment
4. Auto-labeling suggestions (from transcripts, external databases, cross-modal hints, cross-content matching)
5. Label approval and propagation
6. Finalization: Update chunk objects and prepare for retrieval

**Output:** Chunk objects in `approved` state with person IDs and optional character/actor/role associations

**Documentation:** [Curation/Labeling Pipeline](./curation/overview.md)

### 3. Retrieval Pipeline
Enables queryable access to the enriched chunk objects, supporting semantic search, structured filtering, and combined queries.

**Capabilities:**
- Semantic and text-based queries
- Structured filtering (by person, character, actor, role, content type, show, location, etc.)
- Combined queries (semantic + structured)
- Cross-content type queries (e.g., find person across TV series and news programs)
- Overlap handling and deduplication

**Documentation:** [Retrieval Pipeline](./retrieval/overview.md)

### 4. UI Layer
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

- **Ingestion**: Produces chunk objects with anonymous person clusters (automated, GPU-intensive, content-type agnostic)
- **Curation**: Assigns person IDs and optional character/actor/role associations to clusters (asynchronous, manual + auto-labeling, content-type aware)
- **Retrieval**: Consumes labeled chunk objects (flexible implementation, supports all content types)
- **UI**: Consumes retrieval API (independent development)

### Content-Type Agnostic Ingestion

The ingestion pipeline works identically for all content types (TV series, news, talk shows, documentaries, etc.), creating anonymous person clusters without knowing identities. Content-specific associations (characters for fictional content, roles for non-fictional content) are assigned during curation, allowing the system to improve through better labeling without reprocessing video.

### Never Force VLM to Guess Person Identities

The VLM focuses on visual understanding (location, actions, objects, mood). Person identification comes from face recognition and speaker linking, ensuring reliable person data. The VLM doesn't need to know whether a person is a character, actor, news anchor, or guest.

## System Flow

```
Video File
    ↓
[Ingestion Pipeline] (Automated, GPU-intensive, Content-Type Agnostic)
    ├── [1] Time-based Chunking → Overlapping Chunk IDs
    ├── [2] Audio Pipeline → Speakers + Transcripts + Anonymous Audio Clusters
    ├── [3] Visual Pipeline → Faces + Anonymous Person Clusters
    ├── [4] Speaker-Face Linking → Anonymous Speaker-Face Mappings
    ├── [5] VLM Analysis → Chunk Descriptions (location, actions, mood)
    └── [6] Chunk Object Unification → Chunk Objects (pending_labeling)
    ↓
Storage → Chunk Objects (pending_labeling state)
    ↓
[Curation/Labeling Pipeline] (Asynchronous, Manual + Auto-labeling, Content-Type Aware)
    ├── Manual Labeling Interface
    │   ├── Person ID Assignment (always required)
    │   ├── Character/Actor Assignment (for fictional content)
    │   └── Role Assignment (for non-fictional content)
    ├── Auto-labeling Suggestions
    ├── Label Approval & Propagation
    └── Finalization → Chunk Objects (approved state)
    ↓
Storage → Chunk Objects (approved, ready for retrieval)
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
- **[Curation/Labeling Pipeline](./curation/)** - Person, character, actor, and role labeling workflow
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
