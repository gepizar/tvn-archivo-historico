"""Video chunking service for splitting videos into overlapping segments."""
import subprocess
import os
import json
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass, asdict

try:
    from ..config.chunking_config import ChunkingConfig
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config.chunking_config import ChunkingConfig


@dataclass
class VideoChunk:
    """Represents a video chunk with its metadata."""
    chunk_id: str
    start_time: float
    end_time: float
    output_path: str


class VideoChunker:
    """Service for chunking videos into overlapping segments."""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize the video chunker with configuration.
        
        Args:
            config: Chunking configuration. If None, uses default values.
        """
        self.config = config or ChunkingConfig()
        self.config.validate()
    
    def get_video_duration(self, video_path: str) -> float:
        """Get the duration of a video file in seconds.
        
        Args:
            video_path: Path to the video file.
            
        Returns:
            Duration in seconds.
            
        Raises:
            RuntimeError: If ffprobe fails or video duration cannot be determined.
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            duration = float(result.stdout.strip())
            return duration
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get video duration: {e.stderr}")
        except ValueError as e:
            raise RuntimeError(f"Invalid duration value: {e}")
    
    def calculate_chunks(self, video_duration: float) -> List[Tuple[float, float]]:
        """Calculate chunk boundaries with overlap.
        
        Args:
            video_duration: Total duration of the video in seconds.
            
        Returns:
            List of (start_time, end_time) tuples for each chunk.
        """
        chunks = []
        chunk_duration = self.config.chunk_duration_seconds
        overlap = self.config.overlap_seconds
        step = chunk_duration - overlap  # How much to advance for each chunk
        
        start_time = 0.0
        
        while start_time < video_duration:
            end_time = min(start_time + chunk_duration, video_duration)
            chunks.append((start_time, end_time))
            
            # Move to next chunk start (accounting for overlap)
            start_time += step
            
            # If the next chunk would be shorter than overlap, merge with previous
            if start_time + chunk_duration > video_duration and start_time < video_duration:
                # Extend the last chunk to cover the remaining time
                if chunks:
                    chunks[-1] = (chunks[-1][0], video_duration)
                break
        
        return chunks
    
    def extract_chunk(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
        copy_codec: bool = True
    ) -> None:
        """Extract a chunk from the video using ffmpeg.
        
        Args:
            video_path: Path to the input video file.
            start_time: Start time in seconds.
            end_time: End time in seconds.
            output_path: Path where the chunk should be saved.
            copy_codec: If True, copy codecs without re-encoding (faster).
                        If False, re-encode (slower but more compatible).
            
        Raises:
            RuntimeError: If ffmpeg extraction fails.
        """
        duration = end_time - start_time
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-avoid_negative_ts', 'make_zero',
        ]
        
        if copy_codec:
            cmd.extend(['-c', 'copy'])
        else:
            cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
        
        cmd.append(output_path)
        
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract chunk: {e.stderr}")
    
    def extract_audio_from_chunk(
        self,
        chunk: VideoChunk,
        audio_output_path: str,
        audio_extension: str = 'wav'
    ) -> str:
        """Extract audio from a video chunk.
        
        Args:
            chunk: VideoChunk object containing the chunk metadata.
            audio_output_path: Path where the audio file should be saved.
            audio_extension: Audio file extension (default: 'wav').
            
        Returns:
            Path to the extracted audio file.
            
        Raises:
            RuntimeError: If audio extraction fails.
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(audio_output_path) if os.path.dirname(audio_output_path) else '.', exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-i', chunk.output_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le' if audio_extension == 'wav' else 'copy',
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            '-y',  # Overwrite output file
            audio_output_path
        ]
        
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                text=True
            )
            return audio_output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract audio from chunk {chunk.chunk_id}: {e.stderr}")
    
    def extract_audio_from_chunks(
        self,
        chunks: List[VideoChunk],
        audio_output_dir: str,
        audio_extension: str = 'wav'
    ) -> List[str]:
        """Extract audio from multiple video chunks.
        
        Args:
            chunks: List of VideoChunk objects.
            audio_output_dir: Directory where audio files should be saved.
            audio_extension: Audio file extension (default: 'wav').
            
        Returns:
            List of paths to extracted audio files.
        """
        os.makedirs(audio_output_dir, exist_ok=True)
        audio_paths = []
        
        for chunk in chunks:
            audio_filename = f"{chunk.chunk_id}.{audio_extension}"
            audio_path = os.path.join(audio_output_dir, audio_filename)
            self.extract_audio_from_chunk(chunk, audio_path, audio_extension)
            audio_paths.append(audio_path)
        
        return audio_paths
    
    def chunk_video(
        self,
        video_path: str,
        output_dir: str,
        chunk_prefix: str = "chunk",
        copy_codec: bool = True
    ) -> List[VideoChunk]:
        """Chunk a video into overlapping segments.
        
        Args:
            video_path: Path to the input video file.
            output_dir: Directory where chunks should be saved.
            chunk_prefix: Prefix for chunk filenames (default: "chunk").
            copy_codec: If True, copy codecs without re-encoding (faster).
            
        Returns:
            List of VideoChunk objects with metadata for each chunk.
            
        Raises:
            FileNotFoundError: If video file doesn't exist.
            RuntimeError: If video processing fails.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Get video duration
        video_duration = self.get_video_duration(video_path)
        
        # Calculate chunk boundaries
        chunk_boundaries = self.calculate_chunks(video_duration)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract chunks
        video_chunks = []
        video_name = Path(video_path).stem
        
        for idx, (start_time, end_time) in enumerate(chunk_boundaries, start=1):
            chunk_id = f"{chunk_prefix}_{idx:04d}"
            output_filename = f"{chunk_id}_{video_name}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            self.extract_chunk(
                video_path,
                start_time,
                end_time,
                output_path,
                copy_codec=copy_codec
            )
            
            chunk = VideoChunk(
                chunk_id=chunk_id,
                start_time=start_time,
                end_time=end_time,
                output_path=output_path
            )
            video_chunks.append(chunk)
        
        return video_chunks
    
    def generate_metadata_json(
        self,
        chunks: List[VideoChunk],
        metadata_path: str,
        video_dir: Optional[str] = None,
        audio_dir: Optional[str] = None,
        audio_extension: str = 'wav'
    ) -> None:
        """Generate a JSON metadata file for all chunks.
        
        Args:
            chunks: List of VideoChunk objects.
            metadata_path: Path where the metadata JSON file should be saved.
            video_dir: Optional directory where video chunks are stored (for relative paths).
            audio_dir: Optional directory where audio files are stored (for relative paths).
            audio_extension: Audio file extension (default: 'wav').
        """
        metadata = {
            'chunks': [],
            'config': {
                'chunk_duration_seconds': self.config.chunk_duration_seconds,
                'overlap_seconds': self.config.overlap_seconds,
            }
        }
        
        for chunk in chunks:
            chunk_data = {
                'chunk_id': chunk.chunk_id,
                'start_time': chunk.start_time,
                'end_time': chunk.end_time,
                'duration': chunk.end_time - chunk.start_time,
            }
            
            # Add video path (relative if video_dir is provided)
            if video_dir:
                chunk_data['video_path'] = os.path.relpath(chunk.output_path, video_dir)
            else:
                chunk_data['video_path'] = chunk.output_path
            
            # Add audio path if audio_dir is provided
            if audio_dir:
                audio_filename = f"{chunk.chunk_id}.{audio_extension}"
                audio_path = os.path.join(audio_dir, audio_filename)
                if os.path.exists(audio_path):
                    chunk_data['audio_path'] = os.path.relpath(audio_path, audio_dir)
            
            metadata['chunks'].append(chunk_data)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(metadata_path) if os.path.dirname(metadata_path) else '.', exist_ok=True)
        
        # Write metadata to file
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
