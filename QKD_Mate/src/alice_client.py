from pathlib import Path
from .client import QKDClient

def alice_client() -> QKDClient:
    base_dir = Path(__file__).resolve().parent.parent
    return QKDClient(str(base_dir / "config/alice.yaml"))