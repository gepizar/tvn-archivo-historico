"""Configuration for video chunking."""
from dataclasses import dataclass


@dataclass
class ChunkingConfig:
    """Configuration for video chunking parameters."""
    
    chunk_duration_seconds: int = 120  # 2 minutes
    overlap_seconds: int = 15  # 15 seconds overlap
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.chunk_duration_seconds <= 0:
            raise ValueError("chunk_duration_seconds must be positive")
        if self.overlap_seconds < 0:
            raise ValueError("overlap_seconds must be non-negative")
        if self.overlap_seconds >= self.chunk_duration_seconds:
            raise ValueError("overlap_seconds must be less than chunk_duration_seconds")
