import sys
from pathlib import Path

# Aggiungi la directory parent al path per poter importare src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.alice_client import alice_client

if __name__ == "__main__":
    client = alice_client()
    resp = client.get("status")
    print("Alice status:", resp)