#!/usr/bin/env python3
"""
Script per verificare lo stato di entrambi i nodi QKD (Alice e Bob)
"""
import sys
from src.alice_client import alice_client
from src.bob_client import bob_client
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def check_node_status(node_name, client_func):
    """Verifica lo stato di un singolo nodo"""
    try:
        start_time = time.time()
        client = client_func()
        response = client.get("status")
        elapsed_time = time.time() - start_time
        
        return {
            "node": node_name,
            "status": "ATTIVO ✓",
            "response": response,
            "response_time": f"{elapsed_time:.2f}s",
            "error": None
        }
    except Exception as e:
        return {
            "node": node_name,
            "status": "NON ATTIVO ✗",
            "response": None,
            "response_time": None,
            "error": str(e)
        }

def print_node_result(result):
    """Stampa il risultato del check di un nodo"""
    print(f"\n{'='*50}")
    print(f"NODO: {result['node']}")
    print(f"STATO: {result['status']}")
    
    if result['error']:
        print(f"ERRORE: {result['error']}")
        if "certificate" in result['error'].lower():
            print("  → Verifica che i certificati siano nella cartella certs/")
            print("  → File richiesti: ca.crt, client_Alice2.crt/key, client_Bob2.crt/key")
        elif "connection" in result['error'].lower():
            print("  → Possibile problema di rete o firewall")
            print("  → Verifica che gli IP siano raggiungibili")
    else:
        print(f"TEMPO RISPOSTA: {result['response_time']}")
        print(f"RISPOSTA: {result['response']}")

def main():
    print("Verifica stato nodi QKD")
    print("="*50)
    
    # Controlla se i certificati esistono
    import os
    cert_files = ["ca.crt", "client_Alice2.crt", "client_Alice2.key", 
                  "client_Bob2.crt", "client_Bob2.key"]
    missing_certs = []
    
    for cert in cert_files:
        if not os.path.exists(f"certs/{cert}"):
            missing_certs.append(cert)
    
    if missing_certs:
        print("\n⚠️  ATTENZIONE: Certificati mancanti nella cartella certs/:")
        for cert in missing_certs:
            print(f"  - {cert}")
        print("\nAssicurati di copiare tutti i certificati prima di continuare.")
        response = input("\nVuoi continuare comunque? (s/n): ")
        if response.lower() != 's':
            sys.exit(1)
    
    # Verifica entrambi i nodi in parallelo
    nodes = [
        ("Alice", alice_client),
        ("Bob", bob_client)
    ]
    
    print("\nVerifica connessione ai nodi...")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(check_node_status, name, func): name 
            for name, func in nodes
        }
        
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    # Mostra i risultati
    for result in sorted(results, key=lambda x: x['node']):
        print_node_result(result)
    
    # Riepilogo finale
    print(f"\n{'='*50}")
    print("RIEPILOGO:")
    active_nodes = [r for r in results if r['status'] == "ATTIVO ✓"]
    print(f"Nodi attivi: {len(active_nodes)}/2")
    
    if len(active_nodes) == 2:
        print("✓ Entrambi i nodi sono attivi e funzionanti!")
    elif len(active_nodes) == 1:
        print(f"⚠️  Solo il nodo {active_nodes[0]['node']} è attivo")
    else:
        print("✗ Nessun nodo è attivo")
    
    print("="*50)

if __name__ == "__main__":
    main()