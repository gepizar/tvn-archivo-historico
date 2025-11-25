# Ingestion Pipeline Project Structure

## Overview

This document describes the recommended project structure for the ingestion pipeline codebase. The structure is designed to support component isolation, shared code reuse, and both development and production deployments.

## Directory Structure

```
tvn-archivo-historico/
├── docs/                          # Existing documentation
│   └── ...
│
├── ingestion/                     # Ingestion pipeline code
│   ├── shared/                    # Shared code used by all components
│   │   ├── __init__.py
│   │   ├── storage/               # Storage interface implementation
│   │   │   ├── __init__.py
│   │   │   ├── interface.py       # Abstract storage interface
│   │   │   ├── postgresql.py      # PostgreSQL implementation
│   │   │   └── mongodb.py         # MongoDB implementation (optional)
│   │   ├── messaging/             # Message queue abstractions
│   │   │   ├── __init__.py
│   │   │   ├── client.py          # Message queue client wrapper
│   │   │   ├── rabbitmq.py        # RabbitMQ implementation
│   │   │   └── sqs.py             # AWS SQS implementation (optional)
│   │   ├── models/                # Data models and schemas
│   │   │   ├── __init__.py
│   │   │   ├── chunk.py           # Chunk object models
│   │   │   ├── messages.py        # Message format models
│   │   │   └── schemas.py         # Pydantic/JSON schemas
│   │   └── utils/                 # Shared utilities
│   │       ├── __init__.py
│   │       ├── logging.py         # Logging configuration
│   │       ├── config.py          # Configuration management
│   │       └── errors.py          # Custom exceptions
│   │
│   ├── component_1_segmentation/ # Component 1: API Service
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI/Flask app entry point
│   │   ├── api/                   # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py          # HTTP endpoints
│   │   │   └── schemas.py         # Request/response schemas
│   │   ├── services/              # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── segmentation.py   # Segmentation logic
│   │   │   └── video_processor.py # Video processing
│   │   ├── config/                # Component-specific config
│   │   │   └── settings.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_api.py
│   │   │   └── test_segmentation.py
│   │   ├── requirements.txt       # Component dependencies
│   │   ├── Dockerfile             # Container definition
│   │   └── README.md              # Component documentation
│   │
│   ├── component_2_audio/         # Component 2: Audio Worker
│   │   ├── __init__.py
│   │   ├── worker.py              # Worker entry point
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── asr.py             # ASR service
│   │   │   ├── diarization.py    # Speaker diarization
│   │   │   └── clustering.py     # Audio clustering
│   │   ├── models/                # ML models (if stored locally)
│   │   │   └── .gitkeep
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_audio.py
│   │   ├── requirements.txt       # PyTorch, ASR libs, CUDA 11.8
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── component_3_visual/       # Component 3: Visual Worker
│   │   ├── __init__.py
│   │   ├── worker.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── face_detection.py
│   │   │   ├── face_tracking.py
│   │   │   └── clustering.py
│   │   ├── models/
│   │   │   └── .gitkeep
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_visual.py
│   │   ├── requirements.txt       # TensorFlow, face detection, CUDA 12.0
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── component_4_linking/       # Component 4: Linking Worker
│   │   ├── __init__.py
│   │   ├── worker.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── temporal_alignment.py
│   │   │   ├── speaker_face_linker.py
│   │   │   └── association_db.py  # Historical associations
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_linking.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── component_5_scene/        # Component 5: Scene Understanding Worker
│   │   ├── __init__.py
│   │   ├── worker.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── vlm_client.py      # VLM API client
│   │   │   └── scene_parser.py    # Parse VLM responses
│   │   ├── prompts/               # VLM prompt templates
│   │   │   └── scene_description.txt
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_scene.py
│   │   ├── requirements.txt       # transformers, VLM libs
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── component_6_unification/  # Component 6: Unification Service
│   │   ├── __init__.py
│   │   ├── worker.py              # Worker entry point
│   │   ├── api/                   # Optional HTTP API
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── unifier.py         # Unification logic
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_unification.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── orchestrator/              # Orchestration service
│   │   ├── __init__.py
│   │   ├── main.py                # Orchestrator entry point
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── dependency_tracker.py
│   │   │   ├── dispatcher.py
│   │   │   └── state_manager.py
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_orchestrator.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── scripts/                   # Utility scripts
│   │   ├── setup_dev.sh          # Setup development environments
│   │   ├── run_local.py          # Run all components locally
│   │   └── migrate_schema.py     # Database migrations
│   │
│   ├── docker-compose.yml         # Local development setup
│   ├── docker-compose.prod.yml   # Production setup
│   ├── .env.example              # Environment variable template
│   ├── requirements-dev.txt      # Shared dev dependencies
│   └── README.md                 # Ingestion pipeline overview
│
├── storage/                       # Existing database schema
│   └── schema.sql
│
└── README.md                      # Project root README
```

## Key Design Principles

### 1. Component Isolation

Each component is self-contained with:
- **Own dependencies**: Each component has its own `requirements.txt` with potentially conflicting dependencies
- **Own container**: Each component has its own `Dockerfile` for isolated deployment
- **Own tests**: Component-specific test suites
- **Own configuration**: Component-specific settings

This allows Components 2, 3, and 5 to have different ML framework versions (PyTorch, TensorFlow, etc.) without conflicts.

### 2. Shared Code Abstraction

The `shared/` directory contains:
- **Storage interface**: Abstract storage layer that all components use
- **Messaging**: Queue client abstractions for different queue implementations
- **Models**: Shared data structures (chunk objects, message formats)
- **Utils**: Common utilities (logging, config, error handling)

Components import from `shared/` but don't import from each other, maintaining loose coupling.

### 3. Service/Worker Pattern

- **API components** (1, 6): Use `main.py` as entry point, expose HTTP endpoints
- **Worker components** (2-5): Use `worker.py` as entry point, consume from message queue
- **Business logic**: Separated into `services/` directory within each component

### 4. Configuration Management

- **Component-specific**: Each component has `config/settings.py`
- **Environment variables**: `.env.example` template for all configuration
- **Shared config**: Common configuration in `shared/utils/config.py`

## Directory Descriptions

### `ingestion/shared/`

Shared code used by all components. This directory should be installed as a package or added to Python path.

**Storage Interface** (`shared/storage/`):
- Abstract interface that all components use
- Implementations for different storage backends (PostgreSQL, MongoDB)
- Components don't need to know storage implementation details

**Messaging** (`shared/messaging/`):
- Queue client wrappers
- Standardized message formats
- Support for different queue implementations (RabbitMQ, SQS, Redis)

**Models** (`shared/models/`):
- Chunk object data structures
- Message format definitions
- Pydantic/JSON schemas for validation

**Utils** (`shared/utils/`):
- Logging configuration
- Configuration management
- Custom exception classes
- Common helper functions

### Component Directories

Each component follows a consistent structure:

**Entry Point**:
- `main.py` for API components (FastAPI/Flask app)
- `worker.py` for worker components (message queue consumer)

**Services** (`services/`):
- Business logic separated from infrastructure
- Each service handles a specific responsibility
- Services can be tested independently

**API** (`api/` - for API components only):
- HTTP route definitions
- Request/response schemas
- API-specific middleware

**Config** (`config/`):
- Component-specific settings
- Environment variable loading
- Default configuration values

**Tests** (`tests/`):
- Unit tests for services
- Integration tests for API endpoints
- Test fixtures and utilities

**Dependencies**:
- `requirements.txt`: Component-specific Python dependencies
- `Dockerfile`: Container definition with specific base images and dependencies

### `ingestion/orchestrator/`

The orchestration service that:
- Tracks component dependencies
- Dispatches work to workers when dependencies are satisfied
- Manages pipeline state
- Handles error recovery and retries

### `ingestion/scripts/`

Utility scripts for development and operations:
- **setup_dev.sh**: Creates virtual environments for each component
- **run_local.py**: Runs all components locally for development
- **migrate_schema.py**: Database migration scripts

## File Examples

### Component 1 (API) - Entry Point

```python
# ingestion/component_1_segmentation/main.py
from fastapi import FastAPI
from ingestion.shared.messaging import get_queue_client
from ingestion.shared.storage import get_storage_client
from .api.routes import router
from .config.settings import settings

app = FastAPI(title="Segmentation API")
app.include_router(router)

@app.on_event("startup")
async def startup():
    # Initialize queue and storage clients
    queue_client = get_queue_client()
    storage_client = get_storage_client()
    # Register clients with services
    pass
```

### Component 2 (Worker) - Entry Point

```python
# ingestion/component_2_audio/worker.py
import logging
from ingestion.shared.messaging import get_queue_client
from ingestion.shared.storage import get_storage_client
from .services.asr import ASRService
from .services.diarization import DiarizationService
from .services.clustering import AudioClusteringService
from .config.settings import settings

logger = logging.getLogger(__name__)

def process_audio_message(message):
    """Process audio processing message from queue."""
    chunk_id = message["chunkId"]  # chunkId is a top-level field in the message
    audio_url = message["payload"]["audioSegmentUrl"]
    
    # Initialize services
    asr = ASRService()
    diarization = DiarizationService()
    clustering = AudioClusteringService()
    storage = get_storage_client()
    queue = get_queue_client()
    
    try:
        # Process audio
        transcript = asr.transcribe(audio_url)
        speaker_segments = diarization.diarize(audio_url)
        clusters = clustering.cluster(speaker_segments)
        
        # Store results
        result = {
            "chunkId": chunk_id,
            "transcriptSegments": transcript,
            "speakerSegments": speaker_segments,
            "audioClusters": clusters
        }
        storage.store_component_result(chunk_id, "component2", result)
        
        # Send completion message
        queue.send_message("audio.completed", {
            "chunkId": chunk_id,
            **result
        })
        
    except Exception as e:
        logger.error(f"Error processing audio for {chunk_id}: {e}")
        queue.send_message("audio.failed", {
            "chunkId": chunk_id,
            "error": str(e),
            "retryable": True
        })

if __name__ == "__main__":
    queue_client = get_queue_client()
    queue_client.consume("audio.process", process_audio_message)
```

### Shared Storage Interface

```python
# ingestion/shared/storage/interface.py
from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class StorageInterface(ABC):
    """Abstract storage interface for chunk objects."""
    
    @abstractmethod
    def store_chunk(self, chunk_id: str, chunk_object: Dict) -> bool:
        """Store a complete chunk object."""
        pass
    
    @abstractmethod
    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Retrieve a chunk object by ID."""
        pass
    
    @abstractmethod
    def store_component_result(
        self, 
        chunk_id: str, 
        component: str, 
        result: Dict
    ) -> bool:
        """Store intermediate result from a component."""
        pass
    
    @abstractmethod
    def get_component_result(
        self, 
        chunk_id: str, 
        component: str
    ) -> Optional[Dict]:
        """Retrieve intermediate result from a component."""
        pass
    
    @abstractmethod
    def list_chunks(self, filters: Dict) -> List[Dict]:
        """List chunks matching filter criteria."""
        pass
```

### Shared Messaging Interface

```python
# ingestion/shared/messaging/client.py
from abc import ABC, abstractmethod
from typing import Callable, Dict

class MessageQueueClient(ABC):
    """Abstract message queue client interface."""
    
    @abstractmethod
    def send_message(self, message_type: str, payload: Dict) -> bool:
        """Send a message to the queue."""
        pass
    
    @abstractmethod
    def consume(
        self, 
        queue_name: str, 
        handler: Callable[[Dict], None]
    ) -> None:
        """Consume messages from a queue."""
        pass
    
    @abstractmethod
    def acknowledge(self, message_id: str) -> bool:
        """Acknowledge message processing."""
        pass
```

## Development Workflow

### Initial Setup

1. **Create virtual environments** (development):
   ```bash
   cd ingestion
   ./scripts/setup_dev.sh
   ```
   This creates separate venvs for each component.

2. **Install dependencies**:
   ```bash
   # For each component
   cd component_2_audio
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Local Development

**Option 1: Docker Compose** (recommended):
```bash
cd ingestion
docker-compose up
```

**Option 2: Run components individually**:
```bash
# Terminal 1: Component 1 API
cd component_1_segmentation
source venv/bin/activate
python main.py

# Terminal 2: Component 2 Worker
cd component_2_audio
source venv/bin/activate
python worker.py

# Terminal 3: Orchestrator
cd orchestrator
source venv/bin/activate
python main.py
```

### Testing

Run tests for each component:
```bash
cd component_2_audio
source venv/bin/activate
pytest tests/
```

### Production Deployment

1. **Build Docker images**:
   ```bash
   docker build -t component-2-audio:latest ./component_2_audio
   docker build -t component-3-visual:latest ./component_3_visual
   # ... etc
   ```

2. **Deploy with docker-compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Or deploy to Kubernetes**:
   - Each component as a separate deployment
   - Use shared config maps and secrets
   - Scale components independently

## Benefits of This Structure

1. **Isolation**: Components can have conflicting dependencies without issues
2. **Reusability**: Shared code is centralized and reusable
3. **Testability**: Each component can be tested independently
4. **Scalability**: Components can be deployed and scaled independently
5. **Maintainability**: Clear separation of concerns and organization
6. **Flexibility**: Easy to swap implementations (storage, queue) without changing component code
7. **Development**: Easy to work on individual components without affecting others

## Dependencies Management

### Component-Specific Dependencies

Each component's `requirements.txt` should:
- Pin all dependency versions for reproducibility
- Include only what that component needs
- Be independent of other components' requirements

**Example - Component 2 (Audio)**:
```
torch==2.0.0
torchaudio==2.0.0
transformers==4.30.0
whisper==1.1.10
# ... audio-specific dependencies
```

**Example - Component 3 (Visual)**:
```
tensorflow==2.12.0
opencv-python==4.7.0
face-recognition==1.3.0
# ... visual-specific dependencies
```

### Shared Dependencies

The `shared/` code should have minimal dependencies:
```
pydantic==2.0.0
python-dotenv==1.0.0
# ... minimal shared dependencies
```

Components import shared code, so shared dependencies are inherited.

## Configuration Strategy

### Environment Variables

Use `.env` files for configuration:
```bash
# .env.example
QUEUE_URL=amqp://localhost:5672
STORAGE_URL=postgresql://localhost:5432/tvn_archivo
LOG_LEVEL=INFO

# Component-specific
COMPONENT_2_CUDA_VERSION=11.8
COMPONENT_3_CUDA_VERSION=12.0
```

### Component Settings

Each component loads its own settings:
```python
# component_2_audio/config/settings.py
from pydantic import BaseSettings
from ingestion.shared.utils.config import load_env

class Settings(BaseSettings):
    queue_url: str
    storage_url: str
    cuda_version: str = "11.8"
    model_path: str = "./models"
    
    class Config:
        env_prefix = "COMPONENT_2_"
        env_file = ".env"

settings = Settings()
```

## Related Documentation

- [Component APIs](./component_apis.md) - API specifications and message formats
- [Deployment Architecture](./deployment.md) - Deployment strategies
- [Storage Interface](../shared/storage_interface.md) - Storage layer interface
- [Data Models](../shared/data_models.md) - Chunk object schemas

