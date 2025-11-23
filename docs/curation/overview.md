# Curation/Labeling Pipeline Overview

## Purpose

The Curation/Labeling Pipeline assigns character IDs and actor IDs to anonymous clusters created by the ingestion pipeline. This phase runs **asynchronously** after ingestion, allowing continuous GPU processing while labeling happens separately, eliminating bottlenecks.

## Key Design Principles

### Asynchronous Processing

- **Ingestion Pipeline** runs continuously, producing chunk objects with anonymous clusters
- **Curation Pipeline** runs independently, labeling clusters at any time
- No blocking: GPU stays busy processing new content while labeling happens separately

### Decoupled from Ingestion

- Labels can be assigned, updated, or corrected without reprocessing video
- Iterative refinement: Labels can be improved over time
- Batch operations: Label entire seasons or series together

### Manual + Auto-labeling

- **Manual labeling**: Human curators assign character/actor IDs
- **Auto-labeling**: System suggests labels from transcripts, external databases, cross-modal hints
- **Hybrid approach**: Auto-labeling provides suggestions, humans approve/reject

## Pipeline Phases

### Phase 1: Automated Processing (Ingestion Pipeline)
Runs without manual intervention, producing chunk objects with anonymous clusters.

**Output:** Chunk objects in `pending_labeling` state

### Phase 2: Manual Labeling (Curation Pipeline)
Human curators assign character and actor IDs to clusters.

**Process:**
- Review cluster representatives (best face images per cluster)
- Assign character IDs (e.g., "Cluster A = Jon Snow")
- Assign actor IDs (e.g., "Cluster A = Kit Harington")
- Cross-series actor linking (e.g., "Show 1 Cluster A = Show 2 Cluster B = Same Actor")

**Interface:**
- Labeling UI showing cluster representatives
- Batch operations for efficiency
- Label propagation across episodes/seasons

### Phase 3: Auto-labeling (Optional Enhancement)
System suggests labels to accelerate the process.

**Sources:**
- **Transcript analysis**: Extract character names from dialogue ("I'm Jon Snow")
- **External databases**: Match clusters to IMDb/cast lists
- **Cross-modal hints**: Link speaker clusters to face clusters
- **Cross-series matching**: Compare clusters across shows for actor identification

**Confidence levels:**
- High confidence: Auto-label and flag for review
- Medium confidence: Suggest to human curator
- Low confidence: Flag for manual review

### Phase 4: Finalization
After labels are approved, update chunk objects and prepare for retrieval.

**Process:**
- Propagate labels to all chunks containing the cluster
- Update chunk objects with character/actor IDs
- Change status from `pending_labeling` to `approved`
- Trigger retrieval pipeline indexing (if needed)

## Data Flow

```
Chunk Objects (pending_labeling)
    ├── Anonymous Face Clusters (Cluster A, B, C...)
    ├── Anonymous Audio Clusters (Audio Cluster A, B, C...)
    └── Speaker-Face Mappings (anonymous)
    ↓
[Labeling Interface]
    ├── Manual Labeling
    │   ├── Character ID Assignment
    │   ├── Actor ID Assignment
    │   └── Cross-series Actor Linking
    └── Auto-labeling Suggestions
    ↓
[Label Approval]
    ├── Review suggestions
    ├── Approve/reject labels
    └── Propagate labels
    ↓
[Finalization]
    ├── Update chunk objects
    ├── Change status to approved
    └── Prepare for retrieval
    ↓
Chunk Objects (approved, ready for retrieval)
```

## Cluster Label Storage

Labels are stored separately from chunk objects to enable efficient updates:

### Cluster Labels Table
- `clusterId`: Unique cluster identifier (e.g., "show_1_face_cluster_A")
- `clusterType`: Type of cluster (character/actor)
- `label`: Assigned label (e.g., "Jon Snow" or "Kit Harington")
- `confidence`: Confidence score (if auto-labeled)
- `status`: `pending` / `approved` / `rejected`
- `source`: `manual` / `auto_transcript` / `auto_external_db` / etc.
- `updatedAt`: Timestamp of last update

### Label Propagation

When a cluster is labeled:
1. Find all chunks containing that cluster
2. Update chunk objects with the label
3. Maintain referential integrity

## Workflow Benefits

### Hardware Utilization
- **GPU stays busy**: Ingestion pipeline runs continuously
- **No blocking**: Labeling doesn't interrupt processing
- **Parallel processing**: Process multiple episodes/seasons simultaneously

### Efficiency
- **Batch labeling**: Label entire seasons at once
- **Iterative refinement**: Update labels without reprocessing
- **Incremental deployment**: Start with manual, add auto-labeling later

### Quality Control
- **Human oversight**: All labels reviewed by curators
- **Versioning**: Track label changes for audit/debugging
- **Confidence tracking**: Monitor auto-labeling accuracy

## Status States

Chunk objects progress through these states:

1. **`pending_labeling`**: Has anonymous clusters, needs labels
2. **`labeled`**: Has character/actor IDs assigned, pending approval
3. **`approved`**: Labels verified, ready for retrieval
4. **`needs_review`**: Auto-labeling flagged for verification

## Related Documentation

- [Ingestion Pipeline Overview](../ingestion/overview.md)
- [Component 3: Visual Pipeline](../ingestion/component_3_visual.md)
- [Data Models](../shared/data_models.md)
- [Storage Interface](../shared/storage_interface.md)

