#!/usr/bin/env python3
"""
Esempio completo del flusso master/slave per lo scambio di chiavi QKD secondo ETSI GS QKD 014.

1. Alice (master) richiede una chiave al suo KME per comunicare con Bob
2. Alice riceve la chiave e il key_ID
3. Alice comunica il key_ID a Bob attraverso il canale classico
4. Bob (slave) usa il key_ID per recuperare la stessa chiave dal suo KME
"""
import argparse
import json
from src.alice_client import alice_client
from src.bob_client import bob_client
from src.utils import QKDClientError

def fetch_keys_as_master(client, slave_id, number=1, size=256):
    """Alice (master) richiede chiavi per comunicare con Bob (slave)"""
    print(f"\n=== MASTER: Richiesta chiavi per slave {slave_id} ===")
    try:
        # Richiedi chiavi
        resp = client.get_key(
            slave_id=slave_id,
            number=number,
            size=size
        )
        
        print(f"Risposta ricevuta:")
        print(f"  - keys ricevute: {len(resp.get('keys', []))}")
        
        keys_info = []
        for i, key in enumerate(resp.get('keys', [])):
            print(f"\nChiave {i+1}:")
            print(f"  - key_ID: {key['key_ID']}")
            print(f"  - key: {key['key'][:32]}..." if len(key['key']) > 32 else f"  - key: {key['key']}")
            keys_info.append({
                'key_ID': key['key_ID'],
                'key': key['key']
            })
        
        return keys_info
    except QKDClientError as e:
        print(f"Errore nella richiesta master: {e}")
        return []

def fetch_keys_as_slave(client, master_id, key_ids):
    """Bob (slave) recupera le chiavi usando i key_ID forniti da Alice"""
    print(f"\n=== SLAVE: Recupero chiavi dal master {master_id} ===")
    print(f"Key IDs da recuperare: {key_ids}")
    
    try:
        # Recupera le chiavi usando i key_ID
        resp = client.get_key_with_ids(
            master_id=master_id,
            key_IDs=key_ids
        )
        
        print(f"\nRisposta ricevuta:")
        print(f"  - keys recuperate: {len(resp.get('keys', []))}")
        
        for i, key in enumerate(resp.get('keys', [])):
            print(f"\nChiave {i+1}:")
            print(f"  - key_ID: {key['key_ID']}")
            print(f"  - key: {key['key'][:32]}..." if len(key['key']) > 32 else f"  - key: {key['key']}")
        
        return resp.get('keys', [])
    except QKDClientError as e:
        print(f"Errore nella richiesta slave: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="Esempio di scambio chiavi QKD master/slave secondo ETSI GS QKD 014"
    )
    parser.add_argument(
        "--mode", 
        choices=["full", "master", "slave"], 
        default="full",
        help="Modalità: full (esempio completo), master (solo Alice), slave (solo Bob con key_ID)"
    )
    parser.add_argument(
        "--number", 
        type=int, 
        default=1, 
        help="Numero di chiavi da richiedere"
    )
    parser.add_argument(
        "--size", 
        type=int, 
        default=256, 
        help="Dimensione delle chiavi in bit (multiplo di 8)"
    )
    parser.add_argument(
        "--key-ids",
        nargs="+",
        help="Key IDs da usare in modalità slave (richiesto per --mode slave)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        print("=== ESEMPIO COMPLETO FLUSSO MASTER/SLAVE ===")
        
        # Step 1: Alice (master) richiede chiavi
        alice = alice_client()
        keys = fetch_keys_as_master(alice, "Bob2", args.number, args.size)
        
        if not keys:
            print("\nNessuna chiave ricevuta dal master, interruzione.")
            return
        
        # Step 2: Estrai i key_ID
        key_ids = [k['key_ID'] for k in keys]
        print(f"\n>>> Key IDs da comunicare a Bob: {key_ids}")
        
        # Step 3: Bob (slave) recupera le chiavi
        print("\n[Simulazione: Alice comunica i key_ID a Bob via canale classico]")
        bob = bob_client()
        slave_keys = fetch_keys_as_slave(bob, "Alice2", key_ids)
        
        # Step 4: Verifica
        if len(keys) == len(slave_keys):
            print("\n✓ Scambio chiavi completato con successo!")
            print(f"  Alice e Bob ora condividono {len(keys)} chiavi QKD")
        else:
            print("\n✗ Errore: numero di chiavi non corrispondente")
    
    elif args.mode == "master":
        # Solo la parte master
        alice = alice_client()
        keys = fetch_keys_as_master(alice, "Bob2", args.number, args.size)
        if keys:
            key_ids = [k['key_ID'] for k in keys]
            print(f"\n>>> Key IDs da comunicare al slave: {key_ids}")
    
    elif args.mode == "slave":
        # Solo la parte slave
        if not args.key_ids:
            print("Errore: --key-ids richiesto in modalità slave")
            parser.print_help()
            return
        
        bob = bob_client()
        fetch_keys_as_slave(bob, "Alice2", args.key_ids)

if __name__ == "__main__":
    main()