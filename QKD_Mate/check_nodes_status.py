#!/usr/bin/env python3
"""
Script per verificare lo stato di entrambi i nodi QKD (Alice e Bob)
dopo aver inserito i certificati.
"""

import sys
import os
import time
from datetime import datetime

# Aggiungi il path del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.alice_client import alice_client
from src.bob_client import bob_client

def check_certificates():
    """Verifica che tutti i certificati necessari siano presenti"""
    print("🔍 Verifica certificati...")
    
    required_certs = [
        "certs/client_Alice2.crt",
        "certs/client_Alice2.key", 
        "certs/client_Bob2.crt",
        "certs/client_Bob2.key",
        "certs/ca.crt"
    ]
    
    missing_certs = []
    for cert in required_certs:
        if not os.path.exists(cert):
            missing_certs.append(cert)
    
    if missing_certs:
        print("❌ Certificati mancanti:")
        for cert in missing_certs:
            print(f"   - {cert}")
        print("\n💡 Assicurati di aver copiato tutti i certificati nella directory certs/")
        return False
    else:
        print("✅ Tutti i certificati sono presenti")
        return True

def check_node_status(node_name, client_func):
    """Verifica lo stato di un singolo nodo"""
    print(f"\n🔗 Connessione al nodo {node_name}...")
    
    try:
        client = client_func()
        start_time = time.time()
        
        # Prova a ottenere lo status
        response = client.get("status")
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)
        
        print(f"✅ {node_name} è ATTIVO")
        print(f"   📊 Status: {response}")
        print(f"   ⏱️  Tempo di risposta: {response_time}ms")
        
        return True, response
        
    except Exception as e:
        print(f"❌ {node_name} NON è raggiungibile")
        print(f"   🚫 Errore: {str(e)}")
        return False, None

def main():
    """Funzione principale per verificare lo stato dei nodi"""
    print("=" * 60)
    print("🔐 VERIFICA STATO NODI QKD")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Verifica certificati
    if not check_certificates():
        print("\n⚠️  Inserisci prima i certificati e riprova.")
        return False
    
    # 2. Verifica Alice
    alice_active, alice_response = check_node_status("Alice", alice_client)
    
    # 3. Verifica Bob  
    bob_active, bob_response = check_node_status("Bob", bob_client)
    
    # 4. Riepilogo finale
    print("\n" + "=" * 60)
    print("📋 RIEPILOGO STATO NODI")
    print("=" * 60)
    
    print(f"Alice (78.40.171.143:443): {'🟢 ATTIVO' if alice_active else '🔴 INATTIVO'}")
    print(f"Bob   (78.40.171.144:443): {'🟢 ATTIVO' if bob_active else '🔴 INATTIVO'}")
    
    if alice_active and bob_active:
        print("\n✅ Entrambi i nodi sono attivi e raggiungibili!")
        print("🔑 Puoi procedere con le operazioni di scambio chiavi.")
    elif alice_active or bob_active:
        print("\n⚠️  Solo un nodo è attivo. Verifica la configurazione dell'altro nodo.")
    else:
        print("\n❌ Nessun nodo è raggiungibile.")
        print("💡 Suggerimenti:")
        print("   - Verifica che i certificati siano corretti")
        print("   - Controlla la connettività di rete")
        print("   - Verifica che i servizi QKD siano avviati sui server")
    
    print("=" * 60)
    return alice_active and bob_active

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)