#!/usr/bin/env python3
"""
Esempio: Bob interroga lo status del link QKD con Alice.
Bob (slave) chiama GET /api/v1/keys/Alice2/status sul suo KME.
"""
from src.bob_client import bob_client

if __name__ == "__main__":
    # Bob client interroga il suo KME per lo status del link con Alice
    client = bob_client()
    
    try:
        # Bob chiede lo status del link con Alice (slave_id = "Alice2")
        resp = client.get_status("Alice2")
        print("Status del link QKD Bob->Alice:")
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