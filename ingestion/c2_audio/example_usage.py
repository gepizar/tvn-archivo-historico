#!/usr/bin/env python3
"""Example usage of the audio transcription and diarization component.

This script demonstrates how to use the AudioProcessor to process audio files.
"""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.audio_config import AudioConfig
from process_audio import AudioProcessor


def example_single_file():
    """Example: Process a single audio file."""
    print("=" * 60)
    print("Example 1: Processing a single audio file")
    print("=" * 60)
    
    # Create configuration
    config = AudioConfig(
        att_context_size=[70, 13]  # 1.12s latency
    )
    
    # Initialize processor
    processor = AudioProcessor(config)
    
    # Process audio file (replace with your audio file path)
    audio_file = "path/to/your/audio.wav"
    
    if not Path(audio_file).exists():
        print(f"\nNote: Audio file not found: {audio_file}")
        print("Please update the audio_file path in this script.")
        return
    
    result = processor.process_audio_file(
        audio_file,
        output_path="example_transcript.json"
    )
    
    print(f"\nProcessed {len(result['segments'])} segments")
    print(f"First segment: {result['segments'][0] if result['segments'] else 'No segments'}")


def example_batch_processing():
    """Example: Process multiple audio files."""
    print("\n" + "=" * 60)
    print("Example 2: Batch processing multiple audio files")
    print("=" * 60)
    
    # Create configuration
    config = AudioConfig()
    
    # Initialize processor
    processor = AudioProcessor(config)
    
    # List of audio files to process
    audio_files = [
        "path/to/audio1.wav",
        "path/to/audio2.wav",
    ]
    
    # Filter to only existing files
    existing_files = [f for f in audio_files if Path(f).exists()]
    
    if not existing_files:
        print("\nNote: No audio files found.")
        print("Please update the audio_files list in this script.")
        return
    
    # Process batch
    results = processor.process_batch(
        existing_files,
        output_dir="./example_transcripts"
    )
    
    print(f"\nProcessed {len(results)} audio files")
    for result in results:
        print(f"  {Path(result['audio_file']).name}: {len(result['segments'])} segments")


def example_from_chunking_output():
    """Example: Process audio files from c1_chunking output."""
    print("\n" + "=" * 60)
    print("Example 3: Processing audio from c1_chunking output")
    print("=" * 60)
    
    # Path to audio directory from chunking component
    audio_dir = Path("../c1_chunking/chunks/audio")
    
    if not audio_dir.exists():
        print(f"\nNote: Audio directory not found: {audio_dir}")
        print("Please run c1_chunking first to generate audio files.")
        return
    
    # Find all audio files
    audio_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
    
    if not audio_files:
        print(f"\nNo audio files found in {audio_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files")
    
    # Create configuration
    config = AudioConfig()
    
    # Initialize processor
    processor = AudioProcessor(config)
    
    # Process first few files as example
    example_files = [str(f) for f in audio_files[:3]]  # Process first 3 files
    
    results = processor.process_batch(
        example_files,
        output_dir=str(audio_dir.parent / "transcripts")
    )
    
    print(f"\nProcessed {len(results)} audio files")
    for result in results:
        print(f"  {Path(result['audio_file']).name}: {len(result['segments'])} segments")


if __name__ == '__main__':
    print("Audio Transcription & Diarization - Example Usage")
    print("=" * 60)
    
    # Run examples (comment out ones you don't want to run)
    try:
        example_single_file()
    except Exception as e:
        print(f"Error in example_single_file: {e}")
    
    try:
        example_batch_processing()
    except Exception as e:
        print(f"Error in example_batch_processing: {e}")
    
    try:
        example_from_chunking_output()
    except Exception as e:
        print(f"Error in example_from_chunking_output: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
