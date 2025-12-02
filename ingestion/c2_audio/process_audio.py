#!/usr/bin/env python3
"""Process audio files for transcription and speaker diarization.

This script uses NVIDIA NeMo models to transcribe and diarize audio files
generated from the c1_chunking component.
"""
import json
import sys
from pathlib import Path
from typing import List, Optional

import torch
from omegaconf import OmegaConf

# NeMo imports
try:
    from nemo.collections.asr.models import SortformerEncLabelModel, ASRModel
    from nemo.collections.asr.parts.utils.streaming_utils import CacheAwareStreamingAudioBuffer
    from nemo.collections.asr.parts.utils.multispk_transcribe_utils import SpeakerTaggedASR
except ImportError:
    print("Error: NVIDIA NeMo is not installed. Please install it first:")
    print("  pip install Cython packaging")
    print("  pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]")
    sys.exit(1)

from config.audio_config import AudioConfig


class AudioProcessor:
    """Process audio files for transcription and diarization."""
    
    def __init__(self, config: AudioConfig, device: Optional[str] = None):
        """Initialize the audio processor.
        
        Args:
            config: Audio processing configuration
            device: Device to use ('cuda' or 'cpu'). Auto-detects if None.
        """
        self.config = config
        config.validate()
        
        # Auto-detect device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        print("Loading models...")
        
        # Load diarization model
        print(f"Loading diarization model: {config.diar_model_id}")
        self.diar_model = SortformerEncLabelModel.from_pretrained(
            config.diar_model_id
        ).eval().to(self.device)
        
        # Load ASR model
        print(f"Loading ASR model: {config.asr_model_id}")
        self.asr_model = ASRModel.from_pretrained(
            config.asr_model_id
        ).eval().to(self.device)
        
        print("Models loaded successfully!")
    
    def process_audio_file(
        self,
        audio_filepath: str,
        output_path: Optional[str] = None
    ) -> dict:
        """Process a single audio file for transcription and diarization.
        
        Args:
            audio_filepath: Path to the audio file (WAV, 16kHz mono)
            output_path: Optional path to save output JSON. If None, returns dict only.
        
        Returns:
            Dictionary containing transcription and diarization results
        """
        audio_path = Path(audio_filepath)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_filepath}")
        
        print(f"\nProcessing: {audio_path.name}")
        
        # Create configuration for multitalker transcription
        cfg = OmegaConf.create({
            "audio_file": str(audio_path),
            "output_path": output_path or str(audio_path.with_suffix('.json')),
            "att_context_size": self.config.att_context_size,
            "online_normalization": self.config.online_normalization,
            "pad_and_drop_preencoded": self.config.pad_and_drop_preencoded,
        })
        
        # Initialize diarization model with streaming config
        # Try to use MultitalkerTranscriptionConfig if available, otherwise use model directly
        try:
            from nemo.collections.asr.parts.utils.multispk_transcribe_utils import (
                MultitalkerTranscriptionConfig
            )
            diar_model = MultitalkerTranscriptionConfig.init_diar_model(cfg, self.diar_model)
        except (ImportError, AttributeError):
            # Fallback: use diarization model directly
            print("Warning: MultitalkerTranscriptionConfig not available, using model directly")
            diar_model = self.diar_model
        
        # Create streaming audio buffer
        streaming_buffer = CacheAwareStreamingAudioBuffer(
            model=self.asr_model,
            online_normalization=cfg.online_normalization,
            pad_and_drop_preencoded=cfg.pad_and_drop_preencoded,
        )
        streaming_buffer.append_audio_file(audio_filepath=str(audio_path), stream_id=-1)
        streaming_buffer_iter = iter(streaming_buffer)
        
        # Create speaker-tagged ASR streamer
        multispk_asr_streamer = SpeakerTaggedASR(cfg, self.asr_model, diar_model)
        
        # Process audio in streaming chunks
        print("Processing audio stream...")
        for step_num, (chunk_audio, chunk_lengths) in enumerate(streaming_buffer_iter):
            drop_extra_pre_encoded = (
                0
                if step_num == 0 and not cfg.pad_and_drop_preencoded
                else self.asr_model.encoder.streaming_cfg.drop_extra_pre_encoded
            )
            
            with torch.inference_mode():
                with torch.amp.autocast(self.device.type, enabled=True):
                    with torch.no_grad():
                        multispk_asr_streamer.perform_parallel_streaming_stt_spk(
                            step_num=step_num,
                            chunk_audio=chunk_audio,
                            chunk_lengths=chunk_lengths,
                            is_buffer_empty=streaming_buffer.is_buffer_empty(),
                            drop_extra_pre_encoded=drop_extra_pre_encoded,
                        )
        
        # Generate speaker-tagged transcript
        samples = [{'audio_filepath': str(audio_path)}]
        multispk_asr_streamer.generate_seglst_dicts_from_parallel_streaming(samples=samples)
        
        # Get results
        seglst_dict_list = multispk_asr_streamer.instance_manager.seglst_dict_list
        
        # Format output
        result = {
            "audio_file": str(audio_path),
            "segments": self._format_segments(seglst_dict_list)
        }
        
        # Save to file if output_path specified
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Results saved to: {output_path}")
        
        return result
    
    def _format_segments(self, seglst_dict_list: List[dict]) -> List[dict]:
        """Format segments from NeMo output to a simpler structure.
        
        Args:
            seglst_dict_list: List of segment dictionaries from NeMo
        
        Returns:
            List of formatted segment dictionaries
        """
        segments = []
        for seglst_dict in seglst_dict_list:
            for segment in seglst_dict.get('segments', []):
                segments.append({
                    "speaker": segment.get('speaker', 'unknown'),
                    "start_time": segment.get('start', 0.0),
                    "end_time": segment.get('end', 0.0),
                    "text": segment.get('text', ''),
                })
        return segments
    
    def process_batch(
        self,
        audio_files: List[str],
        output_dir: Optional[str] = None
    ) -> List[dict]:
        """Process multiple audio files.
        
        Args:
            audio_files: List of paths to audio files
            output_dir: Optional directory to save output files
        
        Returns:
            List of result dictionaries
        """
        results = []
        for audio_file in audio_files:
            output_path = None
            if output_dir:
                audio_path = Path(audio_file)
                output_path = Path(output_dir) / f"{audio_path.stem}_transcript.json"
            
            result = self.process_audio_file(audio_file, output_path)
            results.append(result)
        
        return results


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Transcribe and diarize audio files using NVIDIA NeMo models",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'audio_file',
        type=str,
        nargs='?',
        help='Path to audio file (WAV, 16kHz mono) or directory containing audio files'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output path for results (JSON file or directory for batch processing)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for batch processing'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        default=None,
        help='Device to use (auto-detected if not specified)'
    )
    
    parser.add_argument(
        '--att-context-size',
        type=int,
        nargs=2,
        default=[70, 13],
        metavar=('LEFT', 'RIGHT'),
        help='Attention context size for streaming [left, right] in 80ms frames (default: 70 13 = 1.12s latency)'
    )
    
    args = parser.parse_args()
    
    if not args.audio_file:
        parser.print_help()
        sys.exit(1)
    
    # Create configuration
    config = AudioConfig(
        att_context_size=args.att_context_size
    )
    
    # Initialize processor
    try:
        processor = AudioProcessor(config, device=args.device)
    except Exception as e:
        print(f"Error initializing processor: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process audio file(s)
    audio_path = Path(args.audio_file)
    
    try:
        if audio_path.is_file():
            # Single file
            output_path = args.output or str(audio_path.with_suffix('.json'))
            result = processor.process_audio_file(str(audio_path), output_path)
            print(f"\nProcessed {len(result['segments'])} segments")
        
        elif audio_path.is_dir():
            # Batch processing
            audio_files = list(audio_path.glob('*.wav')) + list(audio_path.glob('*.mp3'))
            if not audio_files:
                print(f"No audio files found in {audio_path}", file=sys.stderr)
                sys.exit(1)
            
            output_dir = args.output_dir or args.output or str(audio_path / 'transcripts')
            results = processor.process_batch([str(f) for f in audio_files], output_dir)
            print(f"\nProcessed {len(results)} audio files")
        
        else:
            print(f"Error: {audio_path} is not a valid file or directory", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error processing audio: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
