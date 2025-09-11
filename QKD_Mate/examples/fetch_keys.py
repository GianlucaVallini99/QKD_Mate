#!/usr/bin/env python3
"""
ETSI GS QKD 014 compliant example: Complete master/slave key exchange flow

This script demonstrates the complete key exchange flow:
1. Alice (master) requests a key from Bob (slave) using get_key()
2. Bob (slave) retrieves the key using the key_ID with get_key_with_ids()
"""
import argparse
from src.alice_client import alice_client
from src.bob_client import bob_client

def main():
    parser = argparse.ArgumentParser(description="ETSI GS QKD 014 compliant key fetch example")
    parser.add_argument("--mode", choices=["full", "alice-only", "bob-only"], default="full",
                       help="Mode: full (complete flow), alice-only (master request), bob-only (slave retrieve)")
    parser.add_argument("--key-id", type=str, help="Key ID for bob-only mode")
    parser.add_argument("--number", type=int, default=1, help="Number of keys to request")
    parser.add_argument("--size", type=int, default=256, help="Key size in bits (must be multiple of 8)")
    
    args = parser.parse_args()
    
    if args.mode == "full":
        print("=== ETSI GS QKD 014 Complete Key Exchange Flow ===")
        print()
        
        # Step 1: Alice (master) requests key from Bob (slave)
        print("Step 1: Alice (master) requests key from Bob (slave)")
        alice = alice_client()
        try:
            alice_resp = alice.get_key("Bob2", number=args.number, size=args.size)
            print(f"Alice response: {alice_resp}")
            
            # Extract key_ID from response
            if isinstance(alice_resp, dict) and "key_ID" in alice_resp:
                key_id = alice_resp["key_ID"]
                print(f"Received key_ID: {key_id}")
                
                # Step 2: Bob (slave) retrieves key using key_ID
                print("\nStep 2: Bob (slave) retrieves key using key_ID")
                bob = bob_client()
                try:
                    bob_resp = bob.get_key_with_ids("Alice2", [key_id])
                    print(f"Bob response: {bob_resp}")
                    print("\n✅ Key exchange completed successfully!")
                    
                except Exception as e:
                    print(f"❌ Error in Bob's key retrieval: {e}")
            else:
                print("❌ No key_ID found in Alice's response")
                
        except Exception as e:
            print(f"❌ Error in Alice's key request: {e}")
            
    elif args.mode == "alice-only":
        print("=== Alice (Master) Key Request ===")
        alice = alice_client()
        try:
            resp = alice.get_key("Bob2", number=args.number, size=args.size)
            print(f"Alice response: {resp}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    elif args.mode == "bob-only":
        if not args.key_id:
            print("❌ Error: --key-id is required for bob-only mode")
            return
            
        print("=== Bob (Slave) Key Retrieval ===")
        bob = bob_client()
        try:
            resp = bob.get_key_with_ids("Alice2", [args.key_id])
            print(f"Bob response: {resp}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()