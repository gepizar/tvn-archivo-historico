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

#### Persons, Characters, and Roles
- `personsPresent`: List of person IDs that appear visually (always present)
- `personsSpeaking`: List of person IDs that speak (always present)
- `charactersPresent`: List of character IDs that appear visually (optional, for fictional content)
- `charactersSpeaking`: List of character IDs that speak (optional, for fictional content)
- `actors`: List of actor IDs (optional, for fictional content)
- `personDetails`: Per-person information (always present)
  - `personId`: Person identifier
  - `characterId`: Associated character ID (if applicable, for fictional content)
  - `actorId`: Associated actor ID (if applicable, for fictional content)
  - `role`: Role name (if applicable, for non-fictional content, e.g., "news anchor", "reporter")
  - `presenceTimeRanges`: Array of {start, end} time ranges
  - `speakingTimeRanges`: Array of {start, end} time ranges
- `characterDetails`: Per-character information (optional, for fictional content, maintained for backward compatibility)

#### Dialogue
- `dialogueSegments`: List of dialogue segments with person attribution
  - `personId`: Person who spoke (always present)
  - `characterId`: Character who spoke (optional, for fictional content)
  - `text`: Dialogue text
  - `startTime`: Start timestamp within chunk
  - `endTime`: End timestamp within chunk
  - `confidence`: Confidence score for person attribution
- `fullTranscript`: Complete transcript (optional)

#### Visual Situation (from VLM)
- `location`: Location/environment tags
- `actions`: List of main actions
- `objects`: Notable objects present
- `visualContext`: Camera style, distance, perspective, etc.
- `mood`: Emotional tone/atmosphere
- `caption`: Natural language scene description

#### Face Information
- `faceTracks`: List of face tracks with person/character/actor associations
  - `faceTrackId`: Unique identifier for the track
  - `personId`: Person ID (if known)
  - `characterId`: Character ID (if applicable, for fictional content)
  - `actorId`: Actor ID (if applicable, for fictional content)
  - `timeRanges`: Array of {start, end} time ranges
  - `boundingBoxes`: Array of bounding box coordinates
  - `clusterId`: Person cluster ID (for labeling)
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

### Design Approach

The database schema is designed to support efficient storage and retrieval of chunk objects while maintaining flexibility for different storage implementations (relational databases, document stores, or hybrid approaches).

**Key Design Principles:**
- **Chunk-centric**: Chunk objects are the primary data structure
- **Query-optimized**: Schema supports the query patterns defined in [Query Patterns](../retrieval/query_patterns.md)
- **State-aware**: Tracks chunk lifecycle from ingestion through labeling to approval
- **Overlap-aware**: Efficiently handles overlapping chunks for deduplication

### Table Summary

The database schema consists of six main tables/collections:

1. **Chunks** - Primary storage for chunk objects containing all multimodal data (audio, visual, dialogue, scene context). Each chunk represents a 2-3 minute segment of video with overlapping boundaries.

2. **Cluster Labels** - Stores person, character, and actor labels for anonymous clusters created during ingestion. Enables efficient label updates without modifying all chunk objects. Used by the [Curation Pipeline](../curation/overview.md).

3. **Persons Directory** - Master registry of all persons across all content types. Provides canonical person information, enables cross-content queries, and maintains data integrity for person IDs. Replaces and extends the Actors Directory concept.

4. **Actors Directory** - Master registry of actors (persons with `profession: ["actor"]`). Maintained for backward compatibility and specialized actor queries. Links to Persons Directory.

5. **Characters Directory** - Master registry of all characters (for fictional content only). Links characters to actors/persons and shows, provides character metadata, and maintains data integrity for character IDs.

6. **Shows/Episodes Metadata** - Reference table for show/program and episode metadata. Includes content type classification. Can be denormalized into chunks if preferred.

### Core Tables/Collections

#### Chunks Table/Collection

Primary storage for chunk objects. Each row/document represents a single chunk with all its multimodal data.

**Primary Key:**
- `chunkId` (string, unique): Unique identifier for the chunk (e.g., `"show_got_s01e05_chunk_003"`)

**Basic Metadata Fields:**
- `showId` (string, indexed): Show/program identifier
- `contentType` (enum, indexed): Type of content (denormalized from Shows/Episodes Metadata)
  - `tv_series`: Scripted TV shows (has actors/characters)
  - `news`: News programs (has persons with roles)
  - `talk_show`: Talk shows (has hosts/guests)
  - `documentary`: Documentaries (has subjects/narrators)
  - `sports`: Sports programs
  - `variety`: Variety shows
  - `other`: Other program types
- `season` (integer, indexed, nullable): Season number (for episodic content)
- `episode` (integer, indexed, nullable): Episode number (for episodic content)
- `startTime` (float, indexed): Start timestamp in seconds from program/episode start
- `endTime` (float, indexed): End timestamp in seconds from program/episode start
- `duration` (float): Chunk duration in seconds
- `schemaVersion` (string): Schema version for migration support (e.g., `"1.0"`)
- `createdAt` (timestamp): When chunk was created
- `updatedAt` (timestamp): Last update timestamp

**State Management:**
- `status` (enum, indexed): Chunk lifecycle state
  - `pending_labeling`: Has anonymous clusters, awaiting labels
  - `labeled`: Has character/actor IDs assigned, pending approval
  - `approved`: Labels verified, ready for retrieval
  - `needs_review`: Auto-labeling flagged for verification
  - `archived`: Deprecated or removed chunks

**Overlap Metadata:**
- `overlapMetadata` (object/JSON): Information about overlapping chunks
  - `overlapsWith`: Array of chunkIds that overlap with this chunk
  - `overlapStart`: Start time of overlap region (if applicable)
  - `overlapEnd`: End time of overlap region (if applicable)
  - `overlapType`: Type of overlap (temporal, content-based, etc.)

**Person, Character, and Role Data:**
- `personsPresent` (array of strings, indexed): Person IDs that appear visually (always present)
- `personsSpeaking` (array of strings, indexed): Person IDs that speak (always present)
- `charactersPresent` (array of strings, indexed, nullable): Character IDs that appear visually (optional, for fictional content)
- `charactersSpeaking` (array of strings, indexed, nullable): Character IDs that speak (optional, for fictional content)
- `actors` (array of strings, indexed, nullable): Actor IDs associated with characters (optional, for fictional content)
- `personDetails` (array of objects): Per-person information (always present)
  - `personId`: Person identifier
  - `characterId`: Associated character ID (if applicable, for fictional content)
  - `actorId`: Associated actor ID (if applicable, for fictional content)
  - `role`: Role name (if applicable, for non-fictional content, e.g., "news anchor", "reporter", "guest")
  - `presenceTimeRanges`: Array of {start, end} time ranges
  - `speakingTimeRanges`: Array of {start, end} time ranges
- `characterDetails` (array of objects, nullable): Per-character information (optional, for fictional content, maintained for backward compatibility)
  - `characterId`: Character identifier
  - `actorId`: Associated actor ID (if known)
  - `presenceTimeRanges`: Array of {start, end} time ranges
  - `speakingTimeRanges`: Array of {start, end} time ranges

**Dialogue Data:**
- `dialogueSegments` (array of objects): Dialogue segments with person attribution
  - `personId`: Person who spoke (always present)
  - `characterId`: Character who spoke (optional, for fictional content)
  - `text`: Dialogue text
  - `startTime`: Start timestamp within chunk
  - `endTime`: End timestamp within chunk
  - `confidence`: Confidence score for person attribution
- `fullTranscript` (text, full-text indexed): Complete transcript for the chunk (optional)
- `speakerToPersonMappings` (object): Links between anonymous speakers and persons
- `speakerToCharacterMappings` (object, nullable): Links between anonymous speakers and characters (optional, for fictional content, maintained for backward compatibility)

**Visual Situation (VLM Data):**
- `location` (array of strings, indexed): Location/environment tags (e.g., ["forest", "night"])
- `actions` (array of strings, indexed): List of main actions (e.g., ["driving", "talking"])
- `objects` (array of strings): Notable objects present
- `visualContext` (object): Camera style, distance, perspective
  - `cameraStyle`: String (e.g., "close-up", "wide shot")
  - `distance`: String (e.g., "medium", "long")
  - `perspective`: String (e.g., "eye-level", "bird's-eye")
  - `crowdSize`: String (e.g., "solo", "small group", "crowd")
- `mood` (string, indexed): Emotional tone/atmosphere (e.g., "tense", "calm")
- `caption` (text, full-text indexed): Natural language scene description

**Face Information:**
- `faceTracks` (array of objects): List of face tracks in this chunk
  - `faceTrackId`: Unique identifier for the track
  - `personId`: Person ID (if known)
  - `characterId`: Character ID (if applicable, for fictional content)
  - `actorId`: Actor ID (if applicable, for fictional content)
  - `timeRanges`: Array of {start, end} time ranges
  - `boundingBoxes`: Array of bounding box coordinates
  - `clusterId`: Person cluster ID (for labeling)
- `faceEmbeddings` (array of objects): Vector representations for similarity search
  - `faceTrackId`: Associated face track ID
  - `embeddingId`: Reference to embedding storage (see [Embedding Storage](#embedding-storage))
  - `embeddingVector`: Optional inline vector (if small dimensions)
- `faceClusterIds` (array of strings): Person cluster IDs associated with this chunk

**Audio Information:**
- `audioEmbeddings` (array of objects): Speaker embeddings
  - `speakerSegmentId`: Identifier for the speaker segment
  - `embeddingId`: Reference to embedding storage
  - `embeddingVector`: Optional inline vector (if small dimensions)
- `audioClusters` (array of strings): Cluster IDs for voice similarity
- `audioQualityMetrics` (object, optional): Quality indicators
  - `snr`: Signal-to-noise ratio
  - `clarity`: Audio clarity score

**Embedding References:**
- `embeddingRefs` (object): References to external embedding storage
  - `faceEmbeddings`: Array of embedding IDs
  - `audioEmbeddings`: Array of embedding IDs
  - `textEmbeddings`: Array of embedding IDs (if used for semantic search)

#### Cluster Labels Table/Collection

Stores person, character, and actor labels for anonymous clusters. Enables efficient label updates without modifying all chunk objects.

**Primary Key:**
- `clusterId` (string, unique): Unique cluster identifier (e.g., `"show_got_face_cluster_A"`)

**Fields:**
- `clusterType` (enum, indexed): Type of cluster (modality)
  - `face`: Face cluster (visual modality)
  - `audio`: Audio cluster (audio modality)
- `showId` (string, indexed): Show/program this cluster belongs to
- `label` (string, indexed): Assigned label (e.g., "Jon Snow", "Kit Harington", "Maria Rodriguez", "News Anchor")
- `personId` (string, indexed, nullable): Person ID if cluster represents a person (always set when labeled)
- `characterId` (string, indexed, nullable): Character ID if cluster represents a character (for fictional content)
- `actorId` (string, indexed, nullable): Actor ID if cluster represents an actor (for fictional content)
- `role` (string, indexed, nullable): Role name if cluster represents a person with a role (for non-fictional content, e.g., "news anchor", "reporter")
- `confidence` (float): Confidence score (0.0-1.0) if auto-labeled
- `status` (enum, indexed): Label status
  - `pending`: Awaiting assignment
  - `approved`: Label verified and active
  - `rejected`: Label rejected, needs reassignment
- `source` (enum): Label source
  - `manual`: Assigned by human curator
  - `auto_transcript`: Extracted from transcript analysis
  - `auto_external_db`: Matched from external database (IMDb, etc.)
  - `auto_cross_modal`: Linked via cross-modal hints
  - `auto_cross_series`: Matched across series for actor identification
  - `auto_cross_content`: Matched across content types for person identification
- `createdAt` (timestamp): When label was created
- `updatedAt` (timestamp): Last update timestamp
- `createdBy` (string, nullable): User ID of curator who created/approved label

#### Shows/Episodes Metadata Table/Collection

Reference table for show/program and episode metadata. Can be denormalized into chunks if preferred.

**Primary Key:**
- `showId` (string, unique): Show/program identifier

**Fields:**
- `showName` (string): Display name of the show/program
- `description` (text): Show/program description
- `contentType` (enum, indexed, required): Type of content
  - `tv_series`: Scripted TV shows (has actors/characters)
  - `news`: News programs (has persons with roles)
  - `talk_show`: Talk shows (has hosts/guests)
  - `documentary`: Documentaries (has subjects/narrators)
  - `sports`: Sports programs
  - `variety`: Variety shows
  - `other`: Other program types
- `totalSeasons` (integer, nullable): Total number of seasons (for episodic content)
- `episodes` (array of objects, nullable): Episode metadata (for episodic content)
  - `season`: Season number
  - `episode`: Episode number
  - `episodeName`: Episode title
  - `duration`: Episode duration in seconds
  - `airDate`: Original air date
- `metadata` (object): Additional metadata (genre, year, network, etc.)

#### Persons Directory Table/Collection

Master registry of all persons across all content types. Provides canonical person information, enables cross-content queries, and maintains data integrity for person IDs referenced in chunks and cluster labels. This is the primary directory for all people appearing in content, regardless of whether they are actors, characters, or have roles.

**Primary Key:**
- `personId` (string, unique): Canonical person identifier (e.g., `"person_kit_harington"`, `"person_maria_rodriguez"`)

**Identity Fields:**
- `displayName` (string, indexed): Full display name (e.g., "Kit Harington", "Maria Rodriguez")
- `aliases` (array of strings, indexed): Alternative names, nicknames, stage names, professional names
- `sortName` (string, indexed): Name for sorting (e.g., "Harington, Kit", "Rodriguez, Maria")

**Content Type Associations:**
- `professions` (array of strings, indexed): Professions or roles across content types
  - Examples: `["actor", "news_anchor", "reporter", "host", "guest", "narrator", "commentator"]`
- `isActor` (boolean, indexed): Whether this person is an actor (has `profession: ["actor"]` or similar)
- `actorId` (string, indexed, nullable): Reference to Actors Directory if this person is also an actor (for backward compatibility and specialized queries)

**External References:**
- `externalIds` (object): External database references for data enrichment
  - `imdb`: IMDb person ID (e.g., `"nm3229685"`)
  - `tmdb`: The Movie Database person ID
  - `wikipedia`: Wikipedia URL or page title
  - `wikidata`: Wikidata entity ID
- `externalUrls` (object): Additional external links
  - `officialWebsite`: Official website URL
  - `socialMedia`: Object with social media handles/URLs

**Media and Presentation:**
- `photoUrl` (string, nullable): URL to primary profile photo
- `photoUrls` (array of strings): Additional photo URLs
- `thumbnailUrl` (string, nullable): URL to thumbnail image for UI

**Biographical Information:**
- `bio` (text, nullable): Biography or description
- `birthDate` (date, nullable): Date of birth
- `birthPlace` (string, nullable): Place of birth
- `nationality` (string, nullable): Nationality
- `gender` (string, nullable): Gender identity

**Metadata:**
- `metadata` (object): Additional metadata
  - `knownFor`: Array of notable works or roles across content types
  - `awards`: Array of awards or nominations
  - `customFields`: Any additional custom fields
- `tags` (array of strings, indexed): User-defined or system tags for categorization

**Lifecycle:**
- `status` (enum, indexed): Person record status
  - `active`: Person is active and verified
  - `inactive`: Person record exists but may be deprecated
  - `merged`: Person record was merged into another (see `mergedInto`)
  - `pending`: Person record pending verification
- `mergedInto` (string, nullable, indexed): If status is `merged`, reference to the personId this was merged into
- `createdAt` (timestamp): When person record was created
- `updatedAt` (timestamp): Last update timestamp
- `createdBy` (string, nullable): User ID who created the record
- `verifiedAt` (timestamp, nullable): When person information was verified

**Usage Statistics (Denormalized):**
- `appearanceCount` (integer): Total number of chunks where this person appears (denormalized for performance)
- `contentTypeCount` (integer): Number of different content types this person appears in
- `showCount` (integer): Number of different shows/programs this person appears in
- `lastSeenAt` (timestamp, nullable): Timestamp of most recent appearance in any chunk

#### Actors Directory Table/Collection

Master registry of all actors (persons with `profession: ["actor"]` or `isActor: true`). Maintained for backward compatibility and specialized actor queries. Links to Persons Directory via `personId`. For new implementations, prefer querying Persons Directory with `isActor: true` filter.

**Note:** This table is maintained for backward compatibility. The Persons Directory is the primary source of truth, and Actors Directory entries should reference Persons Directory entries.

**Primary Key:**
- `actorId` (string, unique): Canonical actor identifier (e.g., `"actor_kit_harington"`)

**Person Association:**
- `personId` (string, indexed, nullable): Reference to Persons Directory (foreign key). If null, this is a legacy actor record.

**Identity Fields:**
- `displayName` (string, indexed): Full display name (e.g., "Kit Harington")
- `aliases` (array of strings, indexed): Alternative names, nicknames, stage names
- `sortName` (string, indexed): Name for sorting (e.g., "Harington, Kit")

**External References:**
- `externalIds` (object): External database references for data enrichment
  - `imdb`: IMDb person ID (e.g., `"nm3229685"`)
  - `tmdb`: The Movie Database person ID
  - `wikipedia`: Wikipedia URL or page title
  - `wikidata`: Wikidata entity ID
- `externalUrls` (object): Additional external links
  - `officialWebsite`: Official website URL
  - `socialMedia`: Object with social media handles/URLs

**Media and Presentation:**
- `photoUrl` (string, nullable): URL to primary profile photo
- `photoUrls` (array of strings): Additional photo URLs
- `thumbnailUrl` (string, nullable): URL to thumbnail image for UI

**Biographical Information:**
- `bio` (text, nullable): Biography or description
- `birthDate` (date, nullable): Date of birth
- `birthPlace` (string, nullable): Place of birth
- `nationality` (string, nullable): Nationality
- `gender` (string, nullable): Gender identity

**Metadata:**
- `metadata` (object): Additional metadata
  - `profession`: Array of professions (e.g., ["actor", "producer"])
  - `knownFor`: Array of notable works or roles
  - `awards`: Array of awards or nominations
  - `customFields`: Any additional custom fields
- `tags` (array of strings, indexed): User-defined or system tags for categorization

**Lifecycle:**
- `status` (enum, indexed): Actor record status
  - `active`: Actor is active and verified
  - `inactive`: Actor record exists but may be deprecated
  - `merged`: Actor record was merged into another (see `mergedInto`)
  - `pending`: Actor record pending verification
- `mergedInto` (string, nullable, indexed): If status is `merged`, reference to the actorId this was merged into
- `createdAt` (timestamp): When actor record was created
- `updatedAt` (timestamp): Last update timestamp
- `createdBy` (string, nullable): User ID who created the record
- `verifiedAt` (timestamp, nullable): When actor information was verified

**Usage Statistics (Denormalized):**
- `appearanceCount` (integer): Total number of chunks where this actor appears (denormalized for performance)
- `showCount` (integer): Number of different shows this actor appears in
- `lastSeenAt` (timestamp, nullable): Timestamp of most recent appearance in any chunk

#### Characters Directory Table/Collection

Master registry of all characters (for fictional content only). Links characters to actors/persons and shows, provides character metadata, and maintains data integrity for character IDs referenced in chunks. This directory is only populated for content types where characters exist (e.g., `tv_series`).

**Primary Key:**
- `characterId` (string, unique): Character identifier (e.g., `"got_jon_snow"`)

**Identity Fields:**
- `characterName` (string, indexed): Character name (e.g., "Jon Snow")
- `aliases` (array of strings, indexed): Alternative names, nicknames, titles
- `fullName` (string, nullable): Full character name if different from characterName

**Show Association:**
- `showId` (string, indexed): Show this character belongs to
- `showName` (string, indexed): Denormalized show name for quick display

**Person/Actor Association:**
- `personId` (string, indexed, nullable): Associated person ID (foreign key to Persons Directory)
- `actorId` (string, indexed, nullable): Associated actor ID (foreign key to Actors Directory, for backward compatibility)
- `actorDisplayName` (string, nullable): Denormalized actor name for quick display
- `personDisplayName` (string, nullable): Denormalized person name for quick display

**Character Information:**
- `description` (text, nullable): Character description or biography
- `role` (enum, indexed): Character role importance
  - `main`: Main character
  - `supporting`: Supporting character
  - `recurring`: Recurring character
  - `guest`: Guest appearance
  - `background`: Background character
- `firstAppearance` (object, nullable): First appearance information
  - `season`: Season number
  - `episode`: Episode number
  - `chunkId`: First chunk ID where character appears
- `lastAppearance` (object, nullable): Last appearance information
  - `season`: Season number
  - `episode`: Episode number
  - `chunkId`: Last chunk ID where character appears

**External References:**
- `externalIds` (object): External database references
  - `imdb`: IMDb character ID
  - `wikipedia`: Wikipedia URL or page title
  - `wikidata`: Wikidata entity ID
- `externalUrls` (object): Additional external links

**Media:**
- `photoUrl` (string, nullable): URL to character photo
- `thumbnailUrl` (string, nullable): URL to thumbnail image

**Metadata:**
- `metadata` (object): Additional character metadata
  - `occupation`: Character's occupation or role in the story
  - `relationships`: Array of character relationships
  - `characterTraits`: Array of notable traits
  - `customFields`: Any additional custom fields
- `tags` (array of strings, indexed): User-defined or system tags

**Lifecycle:**
- `status` (enum, indexed): Character record status
  - `active`: Character is active
  - `inactive`: Character record exists but may be deprecated
  - `merged`: Character record was merged into another
  - `pending`: Character record pending verification
- `mergedInto` (string, nullable, indexed): If status is `merged`, reference to the characterId this was merged into
- `createdAt` (timestamp): When character record was created
- `updatedAt` (timestamp): Last update timestamp
- `createdBy` (string, nullable): User ID who created the record
- `verifiedAt` (timestamp, nullable): When character information was verified

**Usage Statistics (Denormalized):**
- `appearanceCount` (integer): Total number of chunks where this character appears
- `speakingCount` (integer): Total number of chunks where this character speaks
- `lastSeenAt` (timestamp, nullable): Timestamp of most recent appearance in any chunk

### Indexes

#### Primary Indexes

1. **chunkId** (unique): Primary key lookup
2. **status** (non-unique): Filter chunks by lifecycle state
3. **contentType** (non-unique): Filter by content type
4. **showId + season + episode** (composite): Filter by show/episode
5. **startTime + endTime** (composite): Temporal range queries
6. **personsPresent** (array index): Filter by person presence (always present)
7. **personsSpeaking** (array index): Filter by speaking persons (always present)
8. **charactersPresent** (array index): Filter by character presence (for fictional content)
9. **charactersSpeaking** (array index): Filter by speaking characters (for fictional content)
10. **actors** (array index): Filter by actor (for fictional content)
11. **location** (array index): Filter by location tags
12. **actions** (array index): Filter by action tags
13. **mood** (non-unique): Filter by mood/atmosphere

#### Full-Text Indexes

1. **fullTranscript**: Full-text search on dialogue
2. **caption**: Full-text search on scene descriptions
3. **dialogueSegments.text**: Full-text search on individual dialogue segments

#### Composite Indexes for Common Query Patterns

1. **showId + status**: Filter approved chunks for a show
2. **contentType + status**: Filter approved chunks by content type
3. **showId + season + episode + startTime**: Temporal queries within episodes
4. **personsPresent + location**: Combined person and location filtering
5. **personsSpeaking + mood**: Person dialogue in specific moods
6. **charactersPresent + location**: Combined character and location filtering (for fictional content)
7. **charactersSpeaking + mood**: Character dialogue in specific moods (for fictional content)
8. **status + updatedAt**: Find chunks needing review, sorted by update time

#### Cluster Labels Indexes

1. **clusterId** (unique): Primary key lookup
2. **clusterType + showId**: Filter clusters by type and show
3. **personId** (non-unique): Find all clusters for a person
4. **characterId** (non-unique): Find all clusters for a character (for fictional content)
5. **actorId** (non-unique): Find all clusters for an actor (for fictional content)
6. **role** (non-unique): Filter by role (for non-fictional content)
7. **status** (non-unique): Filter by label status
8. **label** (non-unique, text index): Search labels by name

#### Persons Directory Indexes

1. **personId** (unique): Primary key lookup
2. **displayName** (non-unique, text index): Search persons by name
3. **aliases** (array index): Search by alternative names
4. **sortName** (non-unique): Sort persons alphabetically
5. **isActor** (non-unique): Filter by whether person is an actor
6. **professions** (array index): Filter by profession/role
7. **actorId** (non-unique): Reference to Actors Directory (for backward compatibility)
8. **status** (non-unique): Filter by person status (active, inactive, etc.)
9. **externalIds.imdb** (non-unique): Lookup by IMDb ID
10. **externalIds.tmdb** (non-unique): Lookup by TMDB ID
11. **tags** (array index): Filter by tags
12. **contentTypeCount** (non-unique): Sort by number of content types (for analytics)
13. **showCount** (non-unique): Sort by number of shows (for analytics)
14. **appearanceCount** (non-unique): Sort by total appearances (for analytics)
15. **mergedInto** (non-unique): Find merged person records

#### Actors Directory Indexes

1. **actorId** (unique): Primary key lookup
2. **personId** (non-unique): Reference to Persons Directory
3. **displayName** (non-unique, text index): Search actors by name
4. **aliases** (array index): Search by alternative names
5. **sortName** (non-unique): Sort actors alphabetically
6. **status** (non-unique): Filter by actor status (active, inactive, etc.)
7. **externalIds.imdb** (non-unique): Lookup by IMDb ID
8. **externalIds.tmdb** (non-unique): Lookup by TMDB ID
9. **tags** (array index): Filter by tags
10. **showCount** (non-unique): Sort by number of shows (for analytics)
11. **appearanceCount** (non-unique): Sort by total appearances (for analytics)
12. **mergedInto** (non-unique): Find merged actor records

#### Characters Directory Indexes

1. **characterId** (unique): Primary key lookup
2. **characterName** (non-unique, text index): Search characters by name
3. **aliases** (array index): Search by alternative names
4. **showId** (non-unique): Filter characters by show
5. **showId + characterName** (composite): Filter characters within a show
6. **personId** (non-unique): Find all characters played by a person
7. **actorId** (non-unique): Find all characters played by an actor (for backward compatibility)
8. **role** (non-unique): Filter by character role (main, supporting, etc.)
9. **status** (non-unique): Filter by character status
10. **tags** (array index): Filter by tags
11. **appearanceCount** (non-unique): Sort by total appearances (for analytics)
12. **mergedInto** (non-unique): Find merged character records

### Query Performance Considerations

#### Structured Filtering

The schema supports efficient structured filtering for common query patterns:

- **Person queries**: Use `personsPresent` and `personsSpeaking` array indexes in Chunks, join with Persons Directory for metadata (works across all content types)
- **Character queries**: Use `charactersPresent` and `charactersSpeaking` array indexes in Chunks, join with Characters Directory for metadata (for fictional content)
- **Actor queries**: Use `actors` array index in Chunks, join with Actors Directory for cross-series queries (for fictional content)
- **Role queries**: Filter by `role` field in personDetails or cluster labels (for non-fictional content)
- **Cross-content person queries**: Query Persons Directory by `personId`, then join to Chunks across multiple shows and content types
- **Cross-series actor queries**: Query Actors Directory by `actorId`, then join to Characters Directory, then to Chunks across multiple shows
- **Content type queries**: Use `contentType` index to filter by content type
- **Temporal queries**: Use `startTime` and `endTime` with range queries
- **Location/action queries**: Use `location` and `actions` array indexes
- **Show/episode queries**: Use composite index on `showId + season + episode`

#### Overlap Handling

Overlap metadata enables efficient deduplication:
- Query chunks by time range
- Use `overlapMetadata.overlapsWith` to find related chunks
- Group results by temporal proximity
- Merge metadata from overlapping chunks when needed

#### State-Based Filtering

The `status` field enables:
- Retrieval pipeline to query only `approved` chunks
- Curation pipeline to find `pending_labeling` chunks
- Review workflows to find `needs_review` chunks

### Data Types and Constraints

#### String Fields
- Use appropriate length limits for IDs (e.g., 255 characters for chunkId)
- Character/actor IDs should follow consistent naming conventions
- Show IDs should be URL-safe identifiers

#### Array Fields
- Arrays should have reasonable size limits (e.g., max 100 characters per chunk)
- Consider separate junction tables for very large arrays if using relational DB
- Document stores handle arrays natively

#### Timestamp Fields
- Store timestamps in UTC
- Use appropriate precision (milliseconds recommended)
- Index timestamps for time-based queries

#### JSON/Object Fields
- Use structured objects for complex nested data (characterDetails, visualContext)
- Consider extracting frequently queried fields to top-level indexed fields
- Balance between normalization and query performance

### Schema Versioning

#### Version Field
- Each chunk includes `schemaVersion` field
- Version format: `"major.minor"` (e.g., `"1.0"`, `"1.1"`)
- Major version changes require migration
- Minor version changes are backward compatible

#### Migration Strategy
- **Backward compatibility**: New fields are optional, old fields remain supported
- **Gradual migration**: Migrate chunks during read/write operations
- **Version-aware queries**: Query layer handles version differences
- **Migration scripts**: Separate scripts for major version migrations

#### Version History
- Track schema versions in a separate `schema_versions` table
- Document field additions, removals, and type changes
- Maintain migration scripts for each version transition

### Normalization Considerations

#### Denormalization Strategy

The schema uses a **mostly denormalized** approach:
- Chunk objects contain all data needed for queries
- Reduces join operations for common queries
- Trade-off: Larger storage, but better query performance

#### When to Normalize

The schema uses normalization for reference data:
- **Actors Directory**: Normalized to enable cross-series queries and maintain actor metadata
- **Characters Directory**: Normalized to link characters to actors and shows, maintain character metadata
- **Show/episode metadata**: Optional normalization if metadata is large and rarely changes
- **Embedding storage**: Always stored separately (see [Embedding Storage](#embedding-storage))

#### Referential Integrity

- **Persons Directory**: Person IDs in Chunks and Cluster Labels must reference valid persons
- **Actors Directory**: Actor IDs in Chunks and Cluster Labels must reference valid actors (for backward compatibility)
- **Characters Directory**: Character IDs in Chunks and Cluster Labels must reference valid characters (for fictional content)
- **Person-Actor relationships**: Actors Directory `personId` should reference valid Persons Directory entry
- **Person-Character relationships**: Characters Directory `personId` should reference valid Persons Directory entry
- **Actor-Character relationships**: Characters Directory `actorId` must reference valid Actors Directory entry (for backward compatibility)
- **Cluster labels**: Maintain referential integrity between cluster labels and chunks
- **Chunk overlaps**: Validate overlap references point to existing chunks
- **Content type consistency**: Chunks must have `contentType` matching their show's `contentType`

### Storage Implementation Notes

The schema is designed to be **implementation-agnostic** and can be adapted to:

- **Relational databases** (PostgreSQL, MySQL): Use JSON columns for nested objects, array types for lists
- **Document stores** (MongoDB, CouchDB): Native support for nested objects and arrays
- **Hybrid approaches**: Store chunk metadata in relational DB, embeddings in vector DB

See [Storage Interface](./storage_interface.md) for the abstraction layer that hides implementation details.

## Embedding Storage

_To be documented..._

## Index Structures

_To be documented..._

## Related Documentation

- [Component 6: Unification](../ingestion/component_6_unification.md)
- [Storage Interface](./storage_interface.md)
- [Retrieval Pipeline](../retrieval/overview.md)

