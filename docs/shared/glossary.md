# Glossary

## Terms and Definitions

### Chunk
A time-based segment of video content, typically 2-3 minutes in duration, with 15-30 seconds of overlap with adjacent chunks. Each chunk receives a unique **chunk ID** and is enriched with multimodal data.

### Chunk ID
A unique identifier for each chunk, serving as the central join key that unifies all components in the ingestion pipeline and enables efficient retrieval. Format: `{show_id}_{season}_{episode}_{chunk_index}`.

### Chunk Object
The unified data structure that contains all enriched information for a chunk, including audio transcripts, visual person/character data, scene descriptions, and metadata. Created by Component 6 (Unification) and consumed by the retrieval pipeline. Content-type agnostic during ingestion; person/character/role associations added during curation.

### Speaker Diarization
The process of segmenting audio into contiguous speaker segments, identifying "who spoke when" without initially knowing character identities.

### Speaker Segment
A contiguous segment of audio attributed to a single speaker, with start/end timestamps. Initially anonymous (Speaker 1, Speaker 2, etc.) until linked to persons during curation.

### Audio Cluster
A group of speaker segments with similar voice characteristics, identified through clustering of audio embeddings. Used to identify recurring speakers across episodes/programs. Initially anonymous until labeled as persons during curation.

### Face Track
A continuous sequence of face detections across multiple frames, tracking the same person within a chunk.

### Person Cluster
A group of face tracks or audio segments with similar characteristics, identified through clustering of embeddings. Used to identify recurring persons across content. Initially anonymous until labeled during curation.

### Person ID
A canonical identifier for a person appearing in content (e.g., "person_kit_harington", "person_maria_rodriguez"). Always assigned during curation. Works across all content types.

### Character Cluster
A group of face tracks with similar appearance, identified through clustering of face embeddings. Used to identify recurring characters. (For fictional content only.)

### Character ID
A named identifier for a character (e.g., "Jon Snow", "Walter White"). Assigned to character clusters through manual labeling or automated identification. Only used for fictional content (TV series).

### Actor ID
An identifier for an actor that can span multiple series. Used for cross-series actor recognition. Only used for fictional content (TV series). Links to Person ID.

### In-Content Role
The function or position a person has *within a specific piece of content* (e.g., "news anchor" in a news program, "reporter" in a news segment, "guest" in a talk show, "host" in a variety show). Assigned during curation for non-fictional content types. Stored in chunk objects and cluster labels.

**Example**: A person who was a tennis player in their career might appear as a "guest" in a talk show - "guest" is their in-content role for that specific appearance.

### Career/Life Role
The professions and careers a person has had throughout their life (e.g., "tennis player", "singer", "congressional candidate", "actor", "news anchor"). Stored in Persons Directory with temporal information (start/end dates). Distinct from in-content roles.

**Example**: A person might have career roles: tennis player (2000-2005), singer (2005-2010), congressional candidate (2010-2012), news anchor (2013-present). When they appear in a talk show as a "guest", "guest" is their in-content role for that appearance, while their career roles remain in their biographical record.

### Content Type
Classification of video content into categories such as:
- `tv_series`: Scripted TV shows (has actors/characters)
- `news`: News programs (has persons with roles)
- `talk_show`: Talk shows (has hosts/guests)
- `documentary`: Documentaries (has subjects/narrators)
- `sports`: Sports programs
- `variety`: Variety shows
- `other`: Other program types

### VLM (Vision-Language Model)
A model that processes video and generates natural language descriptions of visual content. Used in Component 5 for scene understanding.

### Overlap
The intentional overlap between consecutive chunks (15-30 seconds) to ensure no dialogue or visual context is lost at boundaries.

### Multimodal
Combining multiple types of data: audio (transcripts, speakers), visual (faces, characters), and contextual (scene descriptions).

## Related Documentation

- [Architecture Overview](../architecture.md)
- [Ingestion Pipeline](../ingestion/overview.md)
- [Retrieval Pipeline](../retrieval/overview.md)

