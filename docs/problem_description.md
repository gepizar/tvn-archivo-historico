# **Problem Description**

You want to build a system capable of automatically **understanding and indexing large collections of video content** from a TV media organization. This includes:
- **TV series** (scripted shows with actors and characters)
- **News programs** (anchors, reporters, guests)
- **Talk shows** (hosts, guests, panelists)
- **Documentaries** (subjects, narrators)
- **Sports programs** (commentators, athletes)
- **Variety shows** and other program types

The goal is to enable **advanced semantic search** over persons, dialogue, roles, characters, actors, and visual situations across all content types.

The system must:

### **1. Identify who is speaking at each moment**

* Extract audio from every program/episode.
* Transcribe all dialogue.
* Perform speaker diarization to segment speech into speakers.
* Link each speech segment to a specific **person** on screen.
* For fictional content: Link persons to **characters** and **actors**.
* For non-fictional content: Link persons to **roles** (e.g., "news anchor", "reporter", "guest").
* Track persons across different programs and content types.

---

### **2. Associate persons with audio, text, and appearance**

For every moment in the video, the system should know:

* Which person(s) appear on screen.
* Which person(s) are speaking.
* What they said (text).
* What they look like (face embeddings).
* For fictional content: Which character they play and which actor plays that character.
* For non-fictional content: What role they have (e.g., "news anchor", "reporter").

This enables queries such as:

* *"Show me every scene where this person talks about betrayal."*
* *"Show me all scenes where Person X and Person Y speak together."*
* *"Show me every scene where this face appears but does not speak."*
* *"Show me all news segments where this anchor appears."*
* *"Show me all appearances of this actor across TV series and news programs."*

This requires **multimodal alignment** between:

* Audio
* Transcript
* Speaker diarization
* Face tracking
* Person identity (with optional character/role/actor associations)

---

### **3. Understand the **scene context**, not just the characters**

You also want to support **situation-based queries**, such as:

* *“Scenes in a forest with several people.”*
* *“Scenes driving in the desert.”*
* *“Scenes inside a car at night.”*

To achieve this, the system must incorporate **visual scene understanding**, extracting information about:

* Location (forest, desert, city street, interior car, etc.)
* Environment (night/day, sunset, lighting)
* Actions (running, driving, talking)
* Objects (cars, weapons, trees)
* Mood (tense, calm)
* Camera type (close-up, wide shot)

This is typically done by:

* Running a **Vision-Language Model (VLM)** such as Qwen3-VL to generate **deep captions** or structured scene metadata.

---

### **4. Address the challenge you identified: aligning scene descriptions with persons**

Scene descriptions from a VLM are **not person-aware** (the VLM does not know that a face is "Walter White" or "News Anchor Maria").
Meanwhile, person identity comes from **face recognition** and **speaker linking**.

The challenge you identified is how to combine:

* **Person metadata** (who appears, who speaks, their role/character if applicable)
* **Scene metadata** (forest, desert, car interior, news studio, etc.)
* **Dialogue metadata** (what is being said)

without the VLM needing to know person names or identities.

The solution is to use **scene/shot IDs** as the common alignment key, merging person data and scene data at a higher semantic level rather than trying to force token-level alignment.

---

# **Final Problem Statement (Concise)**

You are building a system for **full multimodal video understanding** that can:

1. Detect persons (faces and voices), identify them, and track them across programs, episodes, and content types.
2. For fictional content: Associate persons with characters and actors.
3. For non-fictional content: Associate persons with roles (e.g., "news anchor", "reporter", "guest").
4. Perform speaker diarization and align dialogue text with specific persons.
5. Understand the **visual context** of each scene (location, setting, actions, environment) through VLM-based deep captioning.
6. Combine person-aware information with scene-aware information to support rich semantic queries such as:

   * *"Show me all scenes where this person talks about betrayal."*
   * *"Scenes where Person X and Person Y appear together."*
   * *"Scenes where this face appears but doesn't speak."*
   * *"All news segments with this anchor."*
   * *"All appearances of this actor across TV series and news programs."*
   * *"Scenes in the forest with several people."*
   * *"Scenes driving in the desert at sunset."*

The core technical challenge is **aligning person data (faces/voices) with scene descriptions (visual captions)** in a robust and scalable way—without requiring the VLM itself to know person identities. The system must work **content-type agnostic** during ingestion, with content-specific associations (characters, roles, actors) assigned during curation.

---