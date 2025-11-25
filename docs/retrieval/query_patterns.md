# Query Patterns

## Overview

This document describes the types of queries the retrieval pipeline should support, with examples. These patterns guide the design of the retrieval API and ensure the chunk object schema includes all necessary fields.

## 1. Semantic and Text-based Queries

Support natural language queries over dialogue and chunk descriptions.

### Examples

- "Chunks where Jon Snow talks about honor"
- "Chunks where characters argue in a kitchen at night"
- "Driving chunks in the desert where the conversation is tense"
- "Scenes where someone mentions betrayal"
- "Chunks with dialogue about family"

### Required Chunk Object Fields

- Dialogue text (per character)
- Scene descriptions (VLM captions)
- Natural language summaries

## 2. Structured Filtering

Filter by specific attributes without semantic search.

### Filter by Person (Universal - Works Across All Content Types)

- "All chunks where Person X appears"
- "All chunks where Person X speaks"
- "All chunks where Person X and Person Y appear together"
- "All chunks where Person X appears but doesn't speak"
- "All chunks where Person X, Person Y, and Person Z appear together"
- "All chunks with at least three specific persons present"
- "All chunks where multiple persons from a specific group appear"
- "All chunks where Person X appears with any two other persons"
- "All chunks where Person X appears across all content types (TV series, news, etc.)"

### Filter by In-Content Role (For Non-Fictional Content)

- "All chunks where a news anchor appears" (in-content role)
- "All chunks where Person X appears as a reporter" (in-content role)
- "All chunks with guests present" (in-content role)
- "All chunks where Person X appears in in-content role Y"
- "All news segments with this anchor" (in-content role)
- "All talk show segments with this host" (in-content role)

**Note**: In-content roles are the roles persons have *within specific pieces of content*, distinct from their career roles.

### Filter by Career Role (Biographical)

- "All chunks where a person who was a tennis player appears"
- "All chunks where a person who was a congressional candidate appears"
- "All chunks where Person X appears during their time as a singer"
- "All chunks where persons with career role 'news anchor' appear"
- "All chunks where Person X appears, filtered by their career role at that time"
- "All chunks where persons who were actors appear"
- "All chunks where Person X appears during their tennis player career (2000-2005)"

**Note**: Career roles are biographical - the professions and careers persons have had throughout their life, stored in Persons Directory with temporal information.

### Filter by Character (For Fictional Content)

- "All chunks where Character X appears"
- "All chunks where Character X speaks"
- "All chunks where Character X and Character Y appear together"
- "All chunks where Character X appears but doesn't speak"
- "All chunks where Character X, Character Y, and Character Z appear together"
- "All chunks with at least three specific characters present"
- "All chunks where multiple characters from a specific group appear"
- "All chunks where Character X appears with any two other characters"

### Filter by Actor (For Fictional Content)

- "All chunks where this actor appears in any series"
- "All chunks where Actor X speaks in Show Y"
- "Cross-series actor queries"

### Filter by Show/Episode/Program

- "All chunks in Season 2, Episode 5"
- "All chunks in a specific show/program"
- "All chunks in a time range (e.g., first 10 minutes of episode)"
- "All chunks in a specific content type (e.g., all news programs)"
- "All chunks in news programs"
- "All chunks in TV series"

### Filter by Location/Environment

- "All forest chunks"
- "All chunks in a car"
- "All nighttime chunks"
- "All desert chunks at sunset"
- "All chunks set in New York"
- "All chunks set in Los Angeles"
- "All chunks in a specific city or place"
- "All chunks set in Albuquerque"
- "All chunks set in King's Landing"
- "All chunks in a specific location from the show's world"

### Filter by Actions

- "All chunks with fighting"
- "All chunks with driving"
- "All chunks with characters hiding"

### Combined Structured Filters

- "Forest chunks with at least three persons, including Person X"
- "All chunks where this person appears in any content type"
- "All chunks where this actor appears in any series"
- "Nighttime car scenes in Season 3"
- "All chunks in New York with Person X and Person Y present"
- "All chunks set in Albuquerque where Walter White and Jesse Pinkman appear together"
- "Chunks in a specific city with multiple persons (3+) present"
- "All chunks in King's Landing with at least four characters"
- "All news segments with this anchor in the studio"
- "All chunks where Person X appears as a reporter in news programs"

### Required Chunk Object Fields

- Character IDs
- Actor IDs
- Show, season, episode
- Location/environment tags
- Action tags
- Time ranges

## 3. Combined Queries

Combine semantic search with structured filters for precise queries.

### Examples

- "All desert driving chunks at sunset where Walter White is present, even if he doesn't speak"
- "Chunks in the forest with people hiding or sneaking, where this actor appears"
- "Kitchen scenes where Character X talks about betrayal"
- "Nighttime car scenes where someone mentions money"
- "All chunks in Albuquerque where Walter White, Jesse Pinkman, and Skyler White appear together"
- "Chunks set in New York where Character X and Character Y discuss betrayal"
- "Scenes in a specific city where multiple characters argue about money"
- "All chunks in King's Landing where at least three main characters appear together"
- "All news segments where this anchor discusses politics"
- "All chunks where Person X appears (across TV series and news programs)"
- "All talk show segments where this guest appears"

### Query Structure

```
Semantic Query + Structured Filters → Combined Results
```

## 4. Complex Multi-modal Queries

Queries that span multiple modalities (audio, visual, context).

### Examples

- "Chunks where Person X appears visually but doesn't speak"
- "Chunks where Character X appears visually but doesn't speak" (for fictional content)
- "Chunks where this face appears in the background"
- "Scenes where Person X talks about Y while in location Z"
- "Scenes where Character X talks about Y while in location Z" (for fictional content)
- "Chunks with tense dialogue in a calm visual setting"
- "News segments where this anchor appears but doesn't speak"

## 5. Temporal Queries

Queries based on time relationships.

### Examples

- "Chunks within the first 10 minutes of Episode 5"
- "All chunks between timestamp X and Y"
- "Chunks in chronological order for a specific character arc"

## Query Requirements Summary

To support these query patterns, chunk objects must include:

### Audio/Text
- Dialogue text per person/character
- Full transcripts
- Speaker-to-person mappings
- Speaker-to-character mappings (for fictional content)

### Visual
- Person IDs (present and speaking) - always present
- Character IDs (present and speaking) - for fictional content
- Actor IDs - for fictional content
- Role information - for non-fictional content
- Face track information

### Context
- Location/environment tags
- Specific place names (cities, locations from the show's world)
- Action tags
- Object tags
- Mood/atmosphere
- Natural language captions

### Metadata
- Show/program, season, episode
- Content type
- Time ranges (start/end)
- Chunk ID
- Overlap indicators

## Future Query Patterns (TBD)

As the system evolves, additional query patterns may be supported:

- **Graph queries**: "Show me the conversation network between characters"
- **Temporal sequences**: "Show me the progression of Character X's dialogue about topic Y"
- **Similarity search**: "Show me chunks similar to this one"
- **Analytics queries**: "How many times does Character X appear in Season 2?"

## Related Documentation

- [Retrieval Pipeline Overview](./overview.md)
- [API Contract](./api_contract.md)
- [Chunk Object Schema](../shared/data_models.md)

