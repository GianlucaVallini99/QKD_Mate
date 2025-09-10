from .client import QKDClient

def alice_client() -> QKDClient:
    return QKDClient("config/alice.yaml")
