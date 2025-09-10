from pathlib import Path
from .client import QKDClient

def bob_client() -> QKDClient:
    # Get the path relative to this module's location
    module_dir = Path(__file__).parent.parent  # Go up from src/ to QKD_Mate/
    config_path = module_dir / "config" / "bob.yaml"
    return QKDClient(config_path)