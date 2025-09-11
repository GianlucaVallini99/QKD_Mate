#!/usr/bin/env python3
"""
ETSI GS QKD 014 compliant example: Alice queries Bob's status
Alice (client) calls get_status("Bob2") to check Bob's status
"""
from src.alice_client import alice_client

if __name__ == "__main__":
    # Alice client queries Bob's status
    client = alice_client()
    try:
        resp = client.get_status("Bob2")
        print("Bob status (queried by Alice):", resp)
    except Exception as e:
        print(f"Error querying Bob status: {e}")