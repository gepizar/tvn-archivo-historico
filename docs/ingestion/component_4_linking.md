# Component 4: Speaker-Face Linking

## Purpose

Associate audio speakers (from Component 2) with visual characters (from Component 3) to create character-dialogue mappings.

## Process

### 1. Temporal Alignment
- For each **speaker segment** (from diarization), examine the same time interval in the video
- Identify which face tracks are visible during that period
- Align audio timestamps with video timestamps precisely

### 2. Speaker-Face Association
Apply heuristics to link speakers to faces:

**Simple case**: If only one character's face is on screen → assume that's the active speaker

**Complex case**: If multiple faces → use heuristics:
- **Historical cluster associations**: If audio cluster X has been linked to visual cluster Y in many previous chunks, prefer that association (weighted by frequency and confidence)
- **Foreground/background position**: Foreground faces more likely to be speaking
- **Mouth movement detection**: Detect lip movement to identify active speaker
- **Center of frame positioning**: Characters in center more likely to be speaking
- **Face size/zoom level**: Larger/close-up faces more likely to be speaking
- **Temporal consistency**: Prefer links that are consistent across multiple segments

### 3. Character Attribution
- Once a speaker is linked to a face track:
  - Attach the corresponding **character ID** to that speaker segment
  - Build robust mapping: "Speaker 2" in audio → "Character X" in visuals
  - Refine associations over time as more data accumulates
  - Handle cases where speaker is off-screen (voice-over, narration)

### 4. Learning from Historical Cluster Associations
- **Maintain association database**: Track which audio clusters have been linked to which visual clusters across all processed chunks
- **Association confidence**: Calculate confidence scores based on:
  - Frequency of association (how many chunks have this link)
  - Consistency of association (percentage of times this link appears when both clusters are present)
  - Recency weighting (more recent associations weighted higher)
- **Apply as prior knowledge**: When linking speakers to faces:
  - If audio cluster A has strong historical association with visual cluster B, boost confidence for that link
  - Use historical associations to break ties when multiple heuristics conflict
  - Still validate against temporal alignment and other heuristics
- **Incremental learning**: Update association database as new chunks are processed
- **Handle edge cases**: 
  - Don't over-rely on historical associations (characters can change, new characters appear)
  - Weight historical associations appropriately relative to other heuristics
  - Allow for corrections when new evidence contradicts historical patterns

## Output per Chunk

- **Character-dialogue mappings**: 
  - Which characters appear visually
  - Which characters actually speak
  - Exact dialogue delivered by each speaking character
  - Confidence scores for each link
- **Temporal alignment**: 
  - Precise alignment between speech and visual presence
  - Time ranges for each character's dialogue
  - Visual presence time ranges

## Key Considerations

### Linking Challenges
- Off-screen speakers (voice-over, narration, background dialogue)
- Multiple people speaking simultaneously
- Overlapping speech
- Characters speaking while not visible (back turned, profile)
- Background characters speaking

### Confidence Scoring
- Assign confidence scores to each speaker-face link
- Lower confidence for ambiguous cases
- Allow manual review and correction
- Use confidence scores in retrieval ranking

### Edge Cases
- Narrators and voice-overs
- Background dialogue
- Group conversations
- Phone calls and radio communication

## Related Documentation

- [Ingestion Pipeline Overview](./overview.md)
- [Component 2: Audio Pipeline](./component_2_audio.md)
- [Component 3: Visual Pipeline](./component_3_visual.md)
- [Data Flow](./data_flow.md)

