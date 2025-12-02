# Component APIs

## Overview

This document describes the interfaces, APIs, and communication protocols between system components.

## Service Boundaries

### API Components (HTTP/REST)

These components expose HTTP APIs for external interaction:

1. **Component 1: Episode Ingestion and Chunking** - Entry point for video ingestion
2. **Component 6: Chunk Object Unification** - Optional API for status monitoring and manual triggers

### Internal Worker Components

These components operate as background workers that process tasks from a message queue:

1. **Component 2: Audio Pipeline** - ASR, speaker diarization, and clustering
2. **Component 3: Visual Pipeline** - Face detection, tracking, and clustering
3. **Component 4: Speaker-Face Linking** - Associates audio speakers with visual characters
4. **Component 5: Scene Understanding** - VLM-based visual context analysis

### Communication Patterns

```
External Client
    ↓ (HTTP)
Component 1 API (Chunking)
    ↓ (Message Queue)
Orchestrator/Queue
    ├──→ Component 2 Worker (Audio)
    ├──→ Component 3 Worker (Visual)
    └──→ Component 5 Worker (Scene Understanding)
    ↓ (Message Queue)
Component 4 Worker (Linking) - waits for 2 & 3
    ↓ (Message Queue)
Component 6 Service (Unification)
    ↓ (Storage Interface)
Storage Layer
```

### Rationale

**Why APIs for Component 1?**
- Entry point for external video ingestion
- Needs synchronous response for job submission
- Status tracking and error reporting
- Integration with external systems

**Why Workers for Components 2-5?**
- Long-running, GPU-intensive processing
- Better suited for async processing
- Independent scaling based on resource needs
- Parallel execution (Components 2, 3, 5 can run simultaneously)
- No need for HTTP request/response overhead

**Why Optional API for Component 6?**
- Primarily internal service
- Optional API for status monitoring and manual reprocessing
- Can be triggered automatically via message queue

## Deployment and Isolation

### Overview

Components 2, 3, and 5 run AI models that may have conflicting dependencies (different PyTorch versions, CUDA versions, model libraries, etc.). The message queue architecture is designed to support **complete isolation** between components, allowing each to run in its own environment without conflicts.

### Isolation Requirements

**AI Model Components (2, 3, 5) require isolation because:**
- Different ML frameworks (PyTorch, TensorFlow, JAX, etc.)
- Different CUDA/cuDNN versions
- Different model libraries and dependencies
- Different Python versions
- Different system libraries

**Example conflicts:**
- Component 2 (Audio) might need PyTorch 2.0 with CUDA 11.8
- Component 3 (Visual) might need TensorFlow 2.12 with CUDA 12.0
- Component 5 (Scene) might need transformers 4.30 with specific VLM dependencies

### Deployment Options

#### Option 1: Separate Virtual Environments (Development)

Each worker component runs in its own Python virtual environment:

```
project/
├── component_2_audio/
│   ├── venv/                    # Isolated Python environment
│   ├── requirements.txt         # PyTorch, ASR libs, CUDA 11.8
│   └── worker.py
│
├── component_3_visual/
│   ├── venv/                    # Isolated Python environment
│   ├── requirements.txt         # TensorFlow, face detection, CUDA 12.0
│   └── worker.py
│
└── component_5_scene/
    ├── venv/                    # Isolated Python environment
    ├── requirements.txt         # transformers, VLM libs
    └── worker.py
```

**Benefits:**
- Simple setup for development
- Easy to manage locally
- No container overhead

**Limitations:**
- Still shares OS-level resources
- Can't isolate system libraries
- Less portable

#### Option 2: Docker Containers (Recommended for Production)

Each component runs in its own Docker container with complete isolation:

```dockerfile
# component_2_audio/Dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
RUN pip install torch==2.0.0 torchaudio transformers...
# Component-specific dependencies

# component_3_visual/Dockerfile
FROM nvidia/cuda:12.0.0-runtime-ubuntu22.04
RUN pip install tensorflow==2.12.0 opencv-python...
# Component-specific dependencies

# component_5_scene/Dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
RUN pip install transformers==4.30.0 qwen-vl...
# Component-specific dependencies
```

**Benefits:**
- Complete OS-level isolation
- Reproducible environments
- Easy scaling (run multiple containers)
- Easy deployment (Kubernetes, Docker Compose)
- Can optimize base images per component

**Deployment Example:**
```yaml
# docker-compose.yml
services:
  component-2-audio:
    image: component-2-audio:latest
    environment:
      - QUEUE_URL=rabbitmq://...
      - STORAGE_URL=postgresql://...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
  
  component-3-visual:
    image: component-3-visual:latest
    environment:
      - QUEUE_URL=rabbitmq://...
      - STORAGE_URL=postgresql://...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']
  
  component-5-scene:
    image: component-5-scene:latest
    environment:
      - QUEUE_URL=rabbitmq://...
      - STORAGE_URL=postgresql://...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['2']
```

#### Option 3: Separate Machines/Servers

Each component runs on dedicated hardware:

- **Component 2 Server**: GPU node optimized for audio processing
- **Component 3 Server**: GPU node optimized for visual processing
- **Component 5 Server**: GPU node optimized for VLM processing

**Benefits:**
- Maximum isolation
- Hardware optimization per component
- No resource contention
- Independent scaling

### How Isolation Works with Message Queues

The message queue architecture enables isolation because:

1. **No Direct Code Dependencies**: Components don't import each other's code
2. **JSON Messages**: Communication via standardized JSON messages
3. **Storage Abstraction**: All components write to shared storage (database/object storage), not in-memory
4. **Independent Processes**: Each component runs as a separate process/service

**Communication Flow:**
```
Component 2 (venv with PyTorch 2.0)
    ↓ (reads JSON message from queue)
    ↓ (processes audio)
    ↓ (writes result to storage)
    ↓ (sends JSON completion message to queue)

Component 3 (venv with TensorFlow 2.12)
    ↓ (reads JSON message from queue)
    ↓ (processes video)
    ↓ (writes result to storage)
    ↓ (sends JSON completion message to queue)
```

They never share Python imports, memory, or dependencies.

### Storage Interface Compatibility

All components interact with storage through the [Storage Interface](../shared/storage_interface.md), which:
- Abstracts storage implementation (PostgreSQL, MongoDB, S3, etc.)
- Uses standard protocols (SQL, HTTP, etc.)
- Doesn't require shared Python code
- Works from any environment (Python, Go, Rust, etc.)

### GPU Resource Management

When using GPUs with isolated environments:

**Option A: GPU Sharing (Single Machine)**
- Multiple containers can share GPU if using MIG (Multi-Instance GPU) or time-slicing
- Requires careful resource allocation

**Option B: Dedicated GPUs (Recommended)**
- Each component type gets dedicated GPU(s)
- No conflicts or resource contention
- Better performance isolation

**Example GPU Allocation:**
- Component 2: GPU 0 (optimized for audio models)
- Component 3: GPU 1 (optimized for face detection)
- Component 5: GPU 2 (optimized for VLM)

### Model Storage

Each component can have its own model storage:
- **Local files**: Models stored in component's container/filesystem
- **Shared object storage**: Models in S3/GCS, downloaded per component
- **Model registry**: Centralized model storage with versioning

### Language Independence

Components can even be implemented in different languages:
- Component 2: Python (PyTorch)
- Component 3: Python (TensorFlow)
- Component 5: Python (transformers)
- Component 4: Could be Go/Rust for performance
- Component 6: Python (data aggregation)

As long as they can:
- Read/write JSON messages
- Use the storage interface
- Connect to the message queue

### Best Practices

1. **Use Docker containers in production** for complete isolation
2. **Separate virtual environments in development** for simplicity
3. **Document dependencies clearly** in each component's `requirements.txt`
4. **Version pin all dependencies** to ensure reproducibility
5. **Test isolation** by running components in parallel
6. **Monitor resource usage** per component to optimize allocation
7. **Use dedicated GPUs** when possible to avoid conflicts

## API Specifications

_To be documented..._

## Message Formats

### Message Queue Structure

All worker components consume messages from a shared message queue (e.g., RabbitMQ, AWS SQS, Redis Queue). Messages follow a consistent format:

#### Base Message Format

```json
{
  "messageId": "string (unique)",
  "messageType": "enum",
  "chunkId": "string",
  "jobId": "string (optional)",
  "timestamp": "timestamp",
  "payload": {}
}
```

### Component 1 → Orchestrator

**Message Type:** `chunking.completed`

**Payload:**
```json
{
  "chunkIds": ["string"],
  "chunkMetadata": [
    {
      "chunkId": "string",
      "startTime": "float",
      "endTime": "float",
      "audioSegmentUrl": "string",
      "videoSegmentUrl": "string",
      "overlapMetadata": {
        "overlapsWith": ["string"],
        "overlapStart": "float (nullable)",
        "overlapEnd": "float (nullable)"
      }
    }
  ],
  "showId": "string",
  "season": "integer (nullable)",
  "episode": "integer (nullable)",
  "contentType": "enum"
}
```

### Orchestrator → Component 2 (Audio Pipeline)

**Message Type:** `audio.process`

**Payload:**
```json
{
  "chunkId": "string",
  "audioSegmentUrl": "string",
  "startTime": "float",
  "endTime": "float",
  "showId": "string",
  "dependencies": {
    "component1": "completed"
  }
}
```

### Orchestrator → Component 3 (Visual Pipeline)

**Message Type:** `visual.process`

**Payload:**
```json
{
  "chunkId": "string",
  "videoSegmentUrl": "string",
  "startTime": "float",
  "endTime": "float",
  "showId": "string",
  "dependencies": {
    "component1": "completed"
  }
}
```

### Orchestrator → Component 5 (Scene Understanding)

**Message Type:** `scene.process`

**Payload:**
```json
{
  "chunkId": "string",
  "videoSegmentUrl": "string",
  "startTime": "float",
  "endTime": "float",
  "showId": "string",
  "dependencies": {
    "component1": "completed"
  }
}
```

### Component 2 → Orchestrator

**Message Type:** `audio.completed`

**Payload:**
```json
{
  "chunkId": "string",
  "transcriptSegments": [
    {
      "text": "string",
      "startTime": "float",
      "endTime": "float",
      "speakerId": "string"
    }
  ],
  "speakerSegments": [
    {
      "speakerId": "string",
      "audioClusterId": "string",
      "timeRanges": [
        {
          "start": "float",
          "end": "float"
        }
      ],
      "embeddingId": "string"
    }
  ],
  "audioClusters": ["string"],
  "fullTranscript": "string (optional)"
}
```

### Component 3 → Orchestrator

**Message Type:** `visual.completed`

**Payload:**
```json
{
  "chunkId": "string",
  "faceTracks": [
    {
      "faceTrackId": "string",
      "timeRanges": [
        {
          "start": "float",
          "end": "float"
        }
      ],
      "boundingBoxes": [
        {
          "frame": "integer",
          "x": "float",
          "y": "float",
          "width": "float",
          "height": "float"
        }
      ],
      "clusterId": "string",
      "embeddingId": "string"
    }
  ],
  "faceClusters": ["string"]
}
```

### Component 5 → Orchestrator

**Message Type:** `scene.completed`

**Payload:**
```json
{
  "chunkId": "string",
  "scenes": [
    {
      "sceneIndex": "integer",
      "startTime": "float",
      "endTime": "float",
      "location": ["string"],
      "actions": ["string"],
      "objects": ["string"],
      "visualContext": {
        "cameraStyle": "string",
        "distance": "string",
        "perspective": "string",
        "crowdSize": "string",
        "peopleCount": "string"
      },
      "mood": "string",
      "caption": "string",
      "characterPresence": "string"
    }
  ],
  "hasSceneChanges": "boolean",
  "sceneCount": "integer"
}
```

### Orchestrator → Component 4 (Speaker-Face Linking)

**Message Type:** `linking.process`

**Payload:**
```json
{
  "chunkId": "string",
  "audioData": {
    "speakerSegments": [...],
    "audioClusters": [...]
  },
  "visualData": {
    "faceTracks": [...],
    "faceClusters": [...]
  },
  "dependencies": {
    "component2": "completed",
    "component3": "completed"
  }
}
```

### Component 4 → Orchestrator

**Message Type:** `linking.completed`

**Payload:**
```json
{
  "chunkId": "string",
  "characterDialogueMappings": [
    {
      "personId": "string (nullable, anonymous cluster ID)",
      "characterId": "string (nullable)",
      "dialogueSegments": [
        {
          "text": "string",
          "startTime": "float",
          "endTime": "float",
          "confidence": "float"
        }
      ],
      "presenceTimeRanges": [
        {
          "start": "float",
          "end": "float"
        }
      ],
      "speakingTimeRanges": [
        {
          "start": "float",
          "end": "float"
        }
      ]
    }
  ],
  "speakerToPersonMappings": {
    "speakerId": "personId or clusterId"
  }
}
```

### Orchestrator → Component 6 (Unification)

**Message Type:** `unification.process`

**Payload:**
```json
{
  "chunkId": "string",
  "component1Data": {...},
  "component2Data": {...},
  "component3Data": {...},
  "component4Data": {...},
  "component5Data": {...},
  "dependencies": {
    "component1": "completed",
    "component2": "completed",
    "component3": "completed",
    "component4": "completed",
    "component5": "completed"
  }
}
```

### Component 6 → Storage

**Message Type:** `unification.completed`

**Payload:**
```json
{
  "chunkId": "string",
  "chunkObject": {
    // Complete chunk object as defined in data_models.md
  },
  "status": "pending_labeling"
}
```

### Error Messages

**Message Type:** `{component}.failed`

**Payload:**
```json
{
  "chunkId": "string",
  "component": "string",
  "error": "string",
  "errorCode": "string",
  "retryable": "boolean",
  "retryCount": "integer",
  "details": {}
}
```

## Data Flow Contracts

_To be documented..._

