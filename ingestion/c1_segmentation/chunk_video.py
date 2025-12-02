#!/usr/bin/env python3
"""Simple script to chunk a video into overlapping segments.

Usage:
    python chunk_video.py <video_path> [--output-dir OUTPUT_DIR] [--chunk-duration SECONDS] [--overlap SECONDS]

Example:
    python chunk_video.py video.mp4 --output-dir ./chunks --chunk-duration 120 --overlap 15
"""
import argparse
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.chunking_config import ChunkingConfig
from services.video_chunker import VideoChunker


def main():
    parser = argparse.ArgumentParser(
        description="Chunk a video into overlapping segments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'video_path',
        type=str,
        help='Path to the input video file'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./chunks',
        help='Base output directory. Video chunks will be saved to output_dir/video/ and audio to output_dir/audio/ (default: ./chunks)'
    )
    
    parser.add_argument(
        '--chunk-duration',
        type=int,
        default=120,
        help='Duration of each chunk in seconds (default: 120 = 2 minutes)'
    )
    
    parser.add_argument(
        '--overlap',
        type=int,
        default=15,
        help='Overlap between chunks in seconds (default: 15)'
    )
    
    parser.add_argument(
        '--chunk-prefix',
        type=str,
        default='chunk',
        help='Prefix for chunk filenames (default: chunk)'
    )
    
    parser.add_argument(
        '--re-encode',
        action='store_true',
        help='Re-encode video chunks (slower but more compatible). Default is to copy codecs (faster).'
    )
    
    parser.add_argument(
        '--no-extract-audio',
        dest='extract_audio',
        action='store_false',
        default=True,
        help='Disable audio extraction from chunks. By default, audio is extracted and saved to output_dir/audio/.'
    )
    
    parser.add_argument(
        '--audio-dir',
        type=str,
        default=None,
        help='Optional directory where extracted audio files will be saved. '
             'If not provided, audio files are saved to output_dir/audio/.'
    )
    
    parser.add_argument(
        '--audio-extension',
        type=str,
        default='wav',
        help='File extension for extracted audio files (default: wav).'
    )
    
    args = parser.parse_args()
    
    # Validate video file exists
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)
    
    # Create configuration
    config = ChunkingConfig(
        chunk_duration_seconds=args.chunk_duration,
        overlap_seconds=args.overlap
    )
    
    try:
        config.validate()
    except ValueError as e:
        print(f"Error: Invalid configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create chunker and process video
    chunker = VideoChunker(config)
    
    # Set up directory structure
    video_output_dir = os.path.join(args.output_dir, "video")
    audio_output_dir = args.audio_dir if args.audio_dir is not None else os.path.join(args.output_dir, "audio")
    
    print(f"Processing video: {video_path}")
    print(f"Chunk duration: {config.chunk_duration_seconds}s")
    print(f"Overlap: {config.overlap_seconds}s")
    print(f"Output directory: {args.output_dir}")
    print(f"  Video chunks: {video_output_dir}")
    if args.extract_audio:
        print(f"  Audio files: {audio_output_dir}")
    print()
    
    try:
        chunks = chunker.chunk_video(
            str(video_path),
            video_output_dir,
            chunk_prefix=args.chunk_prefix,
            copy_codec=not args.re_encode
        )
        
        print(f"Successfully created {len(chunks)} chunks:")
        print()
        for chunk in chunks:
            print(f"  {chunk.chunk_id}: {chunk.start_time:.2f}s - {chunk.end_time:.2f}s")
            print(f"    Output: {chunk.output_path}")
        
        if args.extract_audio:
            print()
            print("Extracting audio from chunks...")
            audio_paths = chunker.extract_audio_from_chunks(
                chunks,
                audio_output_dir=audio_output_dir,
                audio_extension=args.audio_extension,
                # Codec and copy behavior are automatically determined based on format
            )
            print(f"Successfully extracted audio for {len(audio_paths)} chunks:")
            for path in audio_paths:
                print(f"  Audio: {path}")
        
        # Generate metadata JSON
        print()
        print("Generating metadata JSON...")
        metadata_path = os.path.join(args.output_dir, "metadata.json")
        chunker.generate_metadata_json(
            chunks,
            metadata_path,
            video_dir=video_output_dir,
            audio_dir=audio_output_dir if args.extract_audio else None,
            audio_extension=args.audio_extension if args.extract_audio else "wav",
        )
        print(f"Metadata saved to: {metadata_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
