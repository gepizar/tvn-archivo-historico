"""Configuration for audio transcription and diarization."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AudioConfig:
    """Configuration for audio processing parameters."""
    
    # Model paths (will use HuggingFace model IDs if None)
    asr_model_id: str = "nvidia/multitalker-parakeet-streaming-0.6b-v1"
    diar_model_id: str = "nvidia/diar_streaming_sortformer_4spk-v2.1"
    
    # Streaming configuration (latency settings in 80ms frames)
    att_context_size: list = None  # [70, 13] = 1.12s latency
    
    # Audio processing
    sample_rate: int = 16000  # Hz (required by model)
    online_normalization: bool = True
    pad_and_drop_preencoded: bool = True
    
    # Output settings
    output_format: str = "json"  # json or seglst
    
    def __post_init__(self):
        """Set default values after initialization."""
        if self.att_context_size is None:
            self.att_context_size = [70, 13]  # 1.12s latency
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.sample_rate != 16000:
            raise ValueError("sample_rate must be 16000 Hz (model requirement)")
        if not isinstance(self.att_context_size, list) or len(self.att_context_size) != 2:
            raise ValueError("att_context_size must be a list of 2 integers")
        if self.output_format not in ["json", "seglst"]:
            raise ValueError("output_format must be 'json' or 'seglst'")
