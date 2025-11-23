# Storage Interface

## Overview

This document defines the storage layer interface for reading and writing chunk objects. This interface serves as the contract between the ingestion pipeline (writes) and the retrieval pipeline (reads).

## Design Principles

- **Simple interface**: Basic read/write operations for chunk objects
- **Implementation agnostic**: Interface doesn't prescribe storage technology (database, object storage, etc.)
- **Idempotency**: Write operations should be idempotent
- **Consistency**: Ensure data consistency across reads and writes

## Core Operations

### Write Operations

#### `storeChunk(chunkId, chunkObject)`
Store a chunk object with the given chunk ID.

- **Input**: 
  - `chunkId`: Unique chunk identifier
  - `chunkObject`: Complete chunk object (see [Data Models](./data_models.md))
- **Behavior**: 
  - Overwrites existing chunk if chunkId already exists (idempotent)
  - Validates chunk object structure
- **Returns**: Success/failure status

#### `storeChunks(chunkObjects[])`
Batch store multiple chunk objects.

- **Input**: Array of chunk objects (each with chunkId)
- **Behavior**: Batch write for efficiency
- **Returns**: Success/failure status for each chunk

### Read Operations

#### `getChunk(chunkId)`
Retrieve a specific chunk object by chunk ID.

- **Input**: `chunkId`: Unique chunk identifier
- **Returns**: Chunk object or null if not found

#### `listChunks(filters)`
List chunks matching filter criteria.

- **Input**: Filter object (showId, season, episode, timeRange, etc.)
- **Returns**: Array of chunk objects matching filters

#### `chunkExists(chunkId)`
Check if a chunk exists.

- **Input**: `chunkId`: Unique chunk identifier
- **Returns**: Boolean

## Filter Object Structure

_To be detailed..._

Example filters:
```javascript
{
  showId: "got",
  season: 1,
  episode: 5,
  startTime: 0,
  endTime: 600
}
```

## Implementation Notes

- Storage implementation details (database choice, indexing, etc.) are separate from this interface
- The interface can be implemented using various technologies (PostgreSQL, MongoDB, S3, etc.)
- Performance optimizations (caching, indexing) are implementation concerns

## Error Handling

- Handle storage failures gracefully
- Validate chunk objects before storage
- Provide clear error messages for invalid operations

## Related Documentation

- [Data Models](./data_models.md)
- [Ingestion Pipeline](../ingestion/overview.md)
- [Retrieval Pipeline](../retrieval/overview.md)

