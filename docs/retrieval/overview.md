# Retrieval Pipeline Overview

## Purpose

The retrieval pipeline enables queryable access to the enriched chunk objects created by the ingestion pipeline. It supports flexible query patterns including semantic search, structured filtering, and combined queries.

## Design Principles

### Stable Interface, Flexible Implementation

- **Interface**: The retrieval API contract remains stable regardless of implementation
- **Implementation**: Can evolve from simple indexing to advanced techniques (GraphRAG, context-aware retrieval, etc.)
- **Chunk Objects**: The chunk object structure remains stable regardless of retrieval strategy

### Separation of Concerns

- **Never force the VLM to guess character identities** - Character data comes from face recognition
- **Chunk ID as hub**: The chunk ID unifies audio, visual, and contextual data
- **Retrieval is separate from ingestion**: Can be developed and optimized independently

## Retrieval Capabilities

The retrieval pipeline supports multiple query patterns:

1. **Semantic and Text-based Queries** - Natural language search over dialogue and descriptions
2. **Structured Filtering** - Filter by character, actor, show, location, time, etc.
3. **Combined Queries** - Mix semantic search with structured filters
4. **Overlap Handling** - Deduplication and merging of overlapping chunks

See [Query Patterns](./query_patterns.md) for detailed examples.

## Architecture

```
Chunk Objects (from Storage)
    ↓
Indexing Layer (vector search, keyword search, etc.)
    ↓
Query Processing
    ├── Semantic Search
    ├── Structured Filtering
    └── Result Ranking & Deduplication
    ↓
API Response
```

## Implementation Flexibility

The retrieval implementation can evolve over time:

- **Initial**: Traditional search indexing (vector search, keyword search)
- **Future**: GraphRAG, context-aware retrieval, advanced ranking algorithms
- **Interface**: Remains stable regardless of implementation

## Overlap Handling

Overlapping chunks require special handling in retrieval:

- **Temporal deduplication**: Group results by time ranges
- **Ranking**: Prioritize chunks with higher relevance or more complete data
- **Merging**: Optionally merge metadata from overlapping chunks
- **User control**: Allow users to request "all overlapping chunks" for comprehensive coverage

See [Overlap Handling](./overlap_handling.md) for detailed strategies.

## API Contract

The retrieval API provides a stable interface for querying chunk objects. See [API Contract](./api_contract.md) for the complete specification.

## Related Documentation

- [Query Patterns](./query_patterns.md)
- [API Contract](./api_contract.md)
- [Overlap Handling](./overlap_handling.md)
- [Chunk Object Schema](../shared/data_models.md)
- [Storage Interface](../shared/storage_interface.md)

