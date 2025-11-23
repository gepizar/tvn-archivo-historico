# Data Models

## Overview

This document defines the data structures, schemas, and data contracts used throughout the system. The **chunk object** is the central data structure that unifies all multimodal information.

## Chunk Object Schema

The chunk object is the unified data structure created by the ingestion pipeline and consumed by the retrieval pipeline and UI.

### Status

**To be detailed** - This document will be expanded with the complete, formal schema definition (JSON Schema, TypeScript interface, etc.).

### High-Level Structure

Based on [Component 6: Unification](../ingestion/component_6_unification.md), each chunk object contains:

#### Basic Metadata
- `chunkId`: Unique identifier
- `showId`: Show/series identifier
- `season`: Season number
- `episode`: Episode number
- `startTime`: Start timestamp (seconds from episode start)
- `endTime`: End timestamp (seconds from episode start)
- `duration`: Chunk duration in seconds
- `overlapMetadata`: Information about overlapping chunks

#### Characters and Actors
- `charactersPresent`: List of character IDs that appear visually
- `charactersSpeaking`: List of character IDs that speak
- `actors`: List of actor IDs (if available)
- `characterDetails`: Per-character information

#### Dialogue
- `dialogueSegments`: List of dialogue segments with character attribution
- `fullTranscript`: Complete transcript (optional)

#### Visual Situation (from VLM)
- `location`: Location/environment tags
- `actions`: List of main actions
- `objects`: Notable objects present
- `visualContext`: Camera style, distance, perspective, etc.
- `mood`: Emotional tone/atmosphere
- `caption`: Natural language scene description

#### Face Information
- `faceTracks`: List of face tracks with character/actor associations
- `faceEmbeddings`: Vector representations (for similarity search)

#### Audio Information
- `audioEmbeddings`: Speaker embeddings
- `audioClusters`: Cluster IDs for voice similarity

## Schema Definition Format

The complete schema will be defined using:
- **JSON Schema** for validation
- **TypeScript interfaces** for type safety
- **Example objects** for clarity

## Versioning

The chunk object schema may evolve over time. Versioning strategy:
- Schema version included in chunk objects
- Backward compatibility considerations
- Migration strategies for schema changes

## Database Schema

_To be documented..._

## Embedding Storage

_To be documented..._

## Index Structures

_To be documented..._

## Related Documentation

- [Component 6: Unification](../ingestion/component_6_unification.md)
- [Storage Interface](./storage_interface.md)
- [Retrieval Pipeline](../retrieval/overview.md)

