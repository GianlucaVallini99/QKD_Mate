#!/usr/bin/env python3
"""
Esempio: Alice interroga lo status del link QKD con Bob.
Alice (master) chiama GET /api/v1/keys/Bob2/status sul suo KME.
"""
from src.alice_client import alice_client

if __name__ == "__main__":
    # Alice client interroga il suo KME per lo status del link con Bob
    client = alice_client()
    
    try:
        # Alice chiede lo status del link con Bob (slave_id = "Bob2")
        resp = client.get_status("Bob2")
        print("Status del link QKD Alice->Bob:")
        print(f"  - source_KME_ID: {resp.get('source_KME_ID', 'N/A')}")
        print(f"  - target_KME_ID: {resp.get('target_KME_ID', 'N/A')}")
        print(f"  - master_SAE_ID: {resp.get('master_SAE_ID', 'N/A')}")
        print(f"  - slave_SAE_ID: {resp.get('slave_SAE_ID', 'N/A')}")
        print(f"  - key_size: {resp.get('key_size', 'N/A')}")
        print(f"  - stored_key_count: {resp.get('stored_key_count', 'N/A')}")
        print(f"  - max_key_count: {resp.get('max_key_count', 'N/A')}")
        print(f"  - max_key_per_request: {resp.get('max_key_per_request', 'N/A')}")
        print(f"  - max_key_size: {resp.get('max_key_size', 'N/A')}")
        print(f"  - min_key_size: {resp.get('min_key_size', 'N/A')}")
        print(f"  - max_SAE_ID_count: {resp.get('max_SAE_ID_count', 'N/A')}")
        if 'status_extension' in resp:
            print(f"  - status_extension: {resp['status_extension']}")
    except Exception as e:
        print(f"Errore: {e}")