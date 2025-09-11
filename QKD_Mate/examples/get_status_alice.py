#!/usr/bin/env python3
"""
ETSI GS QKD 014 compliant example: Bob queries Alice's status
Bob (client) calls get_status("Alice2") to check Alice's status
"""
from src.bob_client import bob_client

if __name__ == "__main__":
    # Bob client queries Alice's status
    client = bob_client()
    try:
        resp = client.get_status("Alice2")
        print("Alice status (queried by Bob):", resp)
    except Exception as e:
        print(f"Error querying Alice status: {e}")