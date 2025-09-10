from pathlib import Path
from .client import QKDClient

def alice_client() -> QKDClient:
    # Trova il percorso del file di configurazione relativo a questo modulo
    config_path = Path(__file__).parent.parent / "config" / "alice.yaml"
    return QKDClient(config_path)