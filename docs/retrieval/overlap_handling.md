# Overlap Handling in Retrieval

## Overview

Since chunks overlap by design (15-30 seconds), retrieval results may contain multiple chunks covering the same time period. This document describes strategies for handling overlaps in query results.

## Status

**To be detailed** - This document will be expanded as overlap handling strategies are designed and implemented.

## Design Principles

- **User control**: Users can choose how overlaps are handled
- **Relevance**: Prioritize chunks with higher relevance or more complete data
- **Completeness**: Option to show all overlapping chunks for comprehensive coverage
- **Deduplication**: Default behavior should reduce redundancy

## Planned Strategies

### 1. Temporal Deduplication

Group results by time ranges, showing the most relevant chunk per time period.

### 2. Ranking and Selection

Prioritize chunks with:
- Higher relevance scores
- More complete data
- Better match to query criteria

### 3. Merging

Merge metadata from overlapping chunks to create richer results.

### 4. User Options

Allow users to:
- Request "all overlapping chunks" for comprehensive coverage
- Choose deduplication strategy
- Control overlap handling per query

## Related Documentation

- [Retrieval Pipeline Overview](./overview.md)
- [Query Patterns](./query_patterns.md)
- [Chunk Object Schema](../shared/data_models.md)

