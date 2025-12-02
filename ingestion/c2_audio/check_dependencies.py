#!/usr/bin/env python3
"""Check if all required dependencies are installed correctly."""
import sys


def check_dependency(name, import_name=None, install_hint=None):
    """Check if a dependency is available."""
    if import_name is None:
        import_name = name
    
    try:
        __import__(import_name)
        print(f"✓ {name} is installed")
        return True
    except ImportError:
        print(f"✗ {name} is NOT installed")
        if install_hint:
            print(f"  Install with: {install_hint}")
        return False


def main():
    """Check all dependencies."""
    print("Checking dependencies for c2_audio component...")
    print("=" * 60)
    
    all_ok = True
    
    # Core dependencies
    all_ok &= check_dependency("torch", "torch", "pip install torch")
    all_ok &= check_dependency("numpy", "numpy", "pip install numpy")
    all_ok &= check_dependency("omegaconf", "omegaconf", "pip install omegaconf")
    all_ok &= check_dependency("librosa", "librosa", "pip install librosa")
    all_ok &= check_dependency("soundfile", "soundfile", "pip install soundfile")
    
    # NeMo dependencies
    print("\nNeMo dependencies:")
    nemo_ok = check_dependency(
        "NeMo",
        "nemo",
        "pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]"
    )
    
    if nemo_ok:
        # Check specific NeMo modules
        try:
            from nemo.collections.asr.models import SortformerEncLabelModel, ASRModel
            print("  ✓ NeMo ASR models are available")
        except ImportError as e:
            print(f"  ✗ NeMo ASR models not available: {e}")
            nemo_ok = False
        
        try:
            from nemo.collections.asr.parts.utils.streaming_utils import CacheAwareStreamingAudioBuffer
            print("  ✓ NeMo streaming utilities are available")
        except ImportError as e:
            print(f"  ✗ NeMo streaming utilities not available: {e}")
            nemo_ok = False
        
        try:
            from nemo.collections.asr.parts.utils.multispk_transcribe_utils import SpeakerTaggedASR
            print("  ✓ NeMo multitalker utilities are available")
        except ImportError as e:
            print(f"  ✗ NeMo multitalker utilities not available: {e}")
            print("  Note: This might be okay, the code has a fallback")
            # Don't fail on this one
    
    all_ok &= nemo_ok
    
    # CUDA check
    print("\nHardware:")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA is available (device: {torch.cuda.get_device_name(0)})")
        else:
            print("⚠ CUDA is not available (will use CPU - slower)")
    except:
        print("⚠ Could not check CUDA availability")
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ All dependencies are installed!")
        return 0
    else:
        print("✗ Some dependencies are missing. Please install them before using the component.")
        print("\nQuick install:")
        print("  pip install Cython packaging")
        print("  pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
