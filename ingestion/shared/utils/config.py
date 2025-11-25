"""Configuration utilities."""
import os
from pathlib import Path
from typing import Optional


def load_env_file(env_path: Optional[str] = None) -> None:
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        if env_path:
            load_dotenv(env_path)
        else:
            # Look for .env in project root
            project_root = Path(__file__).parent.parent.parent.parent
            env_file = project_root / ".env"
            if env_file.exists():
                load_dotenv(env_file)
    except ImportError:
        # dotenv not installed, skip
        pass


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable."""
    return os.getenv(key, default)

