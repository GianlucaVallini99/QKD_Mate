import argparse
from src.alice_client import alice_client
from src.bob_client import bob_client

parser = argparse.ArgumentParser(description="Fetch QKD keys from Alice or Bob")
parser.add_argument("--node", choices=["alice", "bob"], required=True, help="Nodo da interrogare")
parser.add_argument("--count", type=int, default=1, help="Numero di chiavi da richiedere (se supportato)")
args = parser.parse_args()

client = alice_client() if args.node == "alice" else bob_client()

# L'endpoint e il payload possono variare a seconda del vendor:
payload = {"count": args.count}
resp = client.post("keys", payload)
print(resp)
