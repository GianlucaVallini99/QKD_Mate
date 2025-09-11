#!/usr/bin/env python3
"""
Esempio avanzato di richiesta chiavi con parametri opzionali ETSI GS QKD 014.
Dimostra l'uso di additional_slave_SAE_IDs e extension parameters.
"""
from src.alice_client import alice_client
from src.utils import QKDClientError

def main():
    client = alice_client()
    
    print("=== Esempio richiesta chiavi avanzata ===\n")
    
    # Esempio 1: Richiesta semplice
    print("1. Richiesta semplice (1 chiave da 256 bit):")
    try:
        resp = client.get_key(slave_id="Bob2", number=1, size=256)
        print(f"   ✓ Ricevute {len(resp.get('keys', []))} chiavi")
    except QKDClientError as e:
        print(f"   ✗ Errore: {e}")
    
    # Esempio 2: Richieste multiple chiavi
    print("\n2. Richiesta multipla (3 chiavi da 512 bit):")
    try:
        resp = client.get_key(slave_id="Bob2", number=3, size=512)
        print(f"   ✓ Ricevute {len(resp.get('keys', []))} chiavi")
    except QKDClientError as e:
        print(f"   ✗ Errore: {e}")
    
    # Esempio 3: Con SAE ID aggiuntivi (multicast)
    print("\n3. Richiesta con SAE ID aggiuntivi (multicast):")
    try:
        resp = client.get_key(
            slave_id="Bob2",
            number=1,
            size=256,
            additional_slave_SAE_IDs=["Charlie2", "David2"]
        )
        print(f"   ✓ Ricevute {len(resp.get('keys', []))} chiavi per comunicazione multicast")
    except QKDClientError as e:
        print(f"   ✗ Errore: {e}")
    
    # Esempio 4: Con extension parameters
    print("\n4. Richiesta con parametri di estensione:")
    try:
        resp = client.get_key(
            slave_id="Bob2",
            number=1,
            size=256,
            extension_mandatory={"priority": "high"},
            extension_optional={"purpose": "authentication"}
        )
        print(f"   ✓ Ricevute {len(resp.get('keys', []))} chiavi con estensioni")
    except QKDClientError as e:
        print(f"   ✗ Errore: {e}")
    
    # Esempio 5: Errore intenzionale - size non multiplo di 8
    print("\n5. Test validazione - size non multiplo di 8:")
    try:
        resp = client.get_key(slave_id="Bob2", number=1, size=250)
        print(f"   ✗ Inaspettato: richiesta accettata!")
    except QKDClientError as e:
        print(f"   ✓ Validazione corretta: {e}")

if __name__ == "__main__":
    main()