from pathlib import Path
from .client import QKDClient

def bob_client() -> QKDClient:
    # Trova il percorso del file di configurazione relativo a questo modulo
    config_path = Path(__file__).parent.parent / "config" / "bob.yaml"
    return QKDClient(config_path)