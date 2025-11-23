# Component 5: Scene Understanding with VLM

## Purpose

Use Vision-Language Models (VLMs) to understand the visual context of each chunk, extracting location, actions, objects, and mood information.

## Process

### 1. VLM Input
- For each chunk, use the **full chunk video** (potentially downsampled for efficiency) as input to a **Vision-Language Model (VLM)**
- Modern VLMs (e.g., Qwen) can process longer sequences (tens of minutes), making 2-3 minute chunks well-suited
- Processing the full video captures complete visual dynamics, temporal context, and scene evolution
- Handle video format and resolution requirements

### 2. Structured Scene Description
Prompt the VLM to produce a **rich, structured description** of the scene(s) with a strict focus on visually observable features only (not character names or identities):

**Scene Change Detection:**
- Detect if the chunk contains a single scene or multiple distinct scenes
- Identify scene transitions (location changes, significant visual shifts, time jumps)
- For chunks with multiple scenes, segment and describe each scene separately
- Provide timestamps relative to chunk start for each scene

**For each scene (or single scene if no change detected):**
- **Location/Environment**: forest, desert, city, inside a car, night/day, etc.
- **Main Actions**: walking, driving, fighting, talking, hiding, etc.
- **Notable Objects**: cars, weapons, trees, buildings, props, etc.
- **Visual Context**: camera style, distance, perspective, crowd vs. intimate, number of people visible, rough estimation of group size, physical appearances (e.g., "three adults and a child," "group of people in uniforms").
- **Natural Language Caption**: short, human-readable summary
- **Character Presence**: Do **not** output character names or specific identities; instead, describe the visual presence and count of people in the scene (e.g., "Two people arguing," "A group of four people sitting at a table"). Refer to characters only in terms of visual attributes (e.g., "elderly man," "young woman in red dress") if needed for clarity.
- **Scene Timestamp**: Start and end time within the chunk (relative to chunk start, in seconds)

*Character identification and naming are handled by the visual and linking components, not by the VLM. The VLM's output should remain visually descriptive and general, never guessing at character identities or names.*

### 3. Attach to Chunk
- Link the scene description(s) to the **chunk ID**
- Store as an array of scenes (single-item array if only one scene)
- Each scene includes its temporal boundaries within the chunk
- Create a "semantic fingerprint" of the visual situation(s)
- Store structured fields and natural language captions for each scene
- Note: Overlapping chunks may have similar descriptions (handled in retrieval deduplication)

## Output per Chunk

**Scene Array**: List of scenes detected in the chunk (minimum 1)

For each scene in the array:
- **Scene Index**: Order within chunk (0-based)
- **Scene Timestamp**: Start and end time within chunk (relative to chunk start, in seconds)
- **Location/Environment**: Structured tags (e.g., ["forest", "daytime", "outdoor"])
- **Actions**: List of main actions (e.g., ["walking", "talking"])
- **Objects**: Notable objects present (e.g., ["car", "weapon", "tree"])
- **Visual Context**: 
  - Camera style (close-up, wide shot, etc.)
  - Distance (intimate, medium, wide)
  - Perspective
  - Crowd vs. intimate setting
  - Number of people visible
  - Rough estimation of group size
  - Physical appearances (e.g., "three adults and a child," "group of people in uniforms")
- **Character Presence**: Visual description of people in the scene without character names or specific identities (e.g., "Two people arguing," "A group of four people sitting at a table," "elderly man," "young woman in red dress")
- **Natural Language Caption**: Short summary (e.g., "Driving through a desert at sunset")

**Scene Change Detection**:
- `has_scene_changes`: Boolean indicating if chunk contains multiple distinct scenes
- `scene_count`: Number of scenes detected in the chunk

## Examples

**Single Scene Chunk:**
- Scene 0 (0s - 150s): "Driving through a desert at sunset"

**Multi-Scene Chunk:**
- Scene 0 (0s - 45s): "Walking in a dense forest with several people"
- Scene 1 (45s - 120s): "Two people arguing in a small kitchen at night"
- Scene 2 (120s - 150s): "Large crowd scene in a city square during daytime"

## Important Design Principle

**Never force the VLM to guess character identities.**

The VLM does **not** need to know character names. It only describes **what's visually going on** - the system handles character identification separately through Components 3 and 4.

This separation of concerns ensures:
- VLM focuses on visual understanding, not character recognition
- Character data comes from face recognition (more reliable)
- Scene descriptions remain general and reusable
- System can work with any VLM without character knowledge

## Key Considerations

### VLM Selection
- Choose VLMs that can handle longer video sequences
- Consider processing time and cost
- Balance between detail and efficiency

### Scene Change Detection

Since chunks are time-based (2-3 minutes), a single chunk may contain multiple distinct scenes or scene transitions. The VLM should:

- **Detect significant visual shifts**: Location changes, time of day changes, major setting transitions
- **Identify scene boundaries**: When one scene clearly ends and another begins
- **Handle gradual transitions**: Some chunks may have smooth transitions rather than hard cuts
- **Avoid over-segmentation**: Don't split on minor camera movements or brief cuts; focus on substantial scene changes
- **Timestamp accurately**: Provide precise start/end times for each scene within the chunk

**Benefits:**
- Enables more precise retrieval (can find specific scenes within chunks)
- Better search granularity (query for "kitchen scene" won't match entire chunk if only part is in kitchen)
- Supports temporal navigation within chunks
- Improves retrieval relevance by matching queries to specific scenes rather than entire chunks

### Prompt Engineering
- Design prompts that extract structured information
- Ensure consistent output format
- Handle edge cases (dark scenes, fast motion, etc.)

### Chunk Overlap
- Overlapping chunks may have similar descriptions
- This is expected and handled in retrieval deduplication
- Overlap ensures no scene context is lost

## Related Documentation

- [Ingestion Pipeline Overview](./overview.md)
- [Component 6: Unification](./component_6_unification.md)
- [Data Flow](./data_flow.md)

