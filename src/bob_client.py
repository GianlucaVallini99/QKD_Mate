from .client import QKDClient

def bob_client() -> QKDClient:
    return QKDClient("config/bob.yaml")
