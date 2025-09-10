#!/usr/bin/env python3
"""
Monitoraggio continuo dei nodi QKD Alice e Bob
"""
import time
import os
import sys
from datetime import datetime
from src.alice_client import alice_client
from src.bob_client import bob_client
from concurrent.futures import ThreadPoolExecutor, as_completed

# Codici ANSI per i colori
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
CLEAR = '\033[2J\033[H'

def check_node(node_name, client_func):
    """Verifica lo stato di un singolo nodo"""
    try:
        client = client_func()
        start = time.time()
        response = client.get("status")
        latency = int((time.time() - start) * 1000)  # millisecondi
        
        return {
            "name": node_name,
            "status": "online",
            "latency": latency,
            "response": str(response)[:100] + "..." if len(str(response)) > 100 else str(response)
        }
    except Exception as e:
        return {
            "name": node_name,
            "status": "offline",
            "latency": None,
            "error": str(e)[:100]
        }

def display_status(alice_status, bob_status, check_count):
    """Mostra lo stato formattato dei nodi"""
    print(CLEAR)  # Pulisce lo schermo
    
    # Header
    print(f"{BLUE}╔{'═'*60}╗{RESET}")
    print(f"{BLUE}║{RESET} Monitoraggio Nodi QKD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {BLUE}║{RESET}")
    print(f"{BLUE}╠{'═'*60}╣{RESET}")
    
    # Alice status
    alice_color = GREEN if alice_status['status'] == 'online' else RED
    alice_icon = '✓' if alice_status['status'] == 'online' else '✗'
    
    print(f"{BLUE}║{RESET} ALICE:")
    print(f"{BLUE}║{RESET}   Stato: {alice_color}{alice_icon} {alice_status['status'].upper()}{RESET}")
    if alice_status['status'] == 'online':
        print(f"{BLUE}║{RESET}   Latenza: {alice_status['latency']}ms")
        print(f"{BLUE}║{RESET}   Risposta: {alice_status['response']}")
    else:
        print(f"{BLUE}║{RESET}   Errore: {RED}{alice_status.get('error', 'Unknown')}{RESET}")
    
    print(f"{BLUE}║{RESET}")
    
    # Bob status
    bob_color = GREEN if bob_status['status'] == 'online' else RED
    bob_icon = '✓' if bob_status['status'] == 'online' else '✗'
    
    print(f"{BLUE}║{RESET} BOB:")
    print(f"{BLUE}║{RESET}   Stato: {bob_color}{bob_icon} {bob_status['status'].upper()}{RESET}")
    if bob_status['status'] == 'online':
        print(f"{BLUE}║{RESET}   Latenza: {bob_status['latency']}ms")
        print(f"{BLUE}║{RESET}   Risposta: {bob_status['response']}")
    else:
        print(f"{BLUE}║{RESET}   Errore: {RED}{bob_status.get('error', 'Unknown')}{RESET}")
    
    # Footer
    print(f"{BLUE}╠{'═'*60}╣{RESET}")
    
    # Riepilogo
    both_online = alice_status['status'] == 'online' and bob_status['status'] == 'online'
    if both_online:
        print(f"{BLUE}║{RESET} {GREEN}✓ Entrambi i nodi sono attivi{RESET}")
    else:
        online_count = sum(1 for s in [alice_status, bob_status] if s['status'] == 'online')
        print(f"{BLUE}║{RESET} {YELLOW}⚠️  Solo {online_count}/2 nodi attivi{RESET}")
    
    print(f"{BLUE}║{RESET} Controlli effettuati: {check_count}")
    print(f"{BLUE}╚{'═'*60}╝{RESET}")
    print(f"\n{YELLOW}Premi Ctrl+C per uscire{RESET}")

def main():
    # Verifica certificati
    cert_files = ["ca.crt", "client_Alice2.crt", "client_Alice2.key", 
                  "client_Bob2.crt", "client_Bob2.key"]
    missing_certs = [cert for cert in cert_files if not os.path.exists(f"certs/{cert}")]
    
    if missing_certs:
        print(f"{RED}ERRORE: Certificati mancanti nella cartella certs/:{RESET}")
        for cert in missing_certs:
            print(f"  - {cert}")
        print("\nCopia i certificati e riprova.")
        sys.exit(1)
    
    check_count = 0
    interval = 5  # secondi tra i controlli
    
    print(f"{BLUE}Avvio monitoraggio nodi QKD...{RESET}")
    print(f"Intervallo di controllo: {interval} secondi")
    time.sleep(2)
    
    try:
        while True:
            check_count += 1
            
            # Controlla entrambi i nodi in parallelo
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_alice = executor.submit(check_node, "Alice", alice_client)
                future_bob = executor.submit(check_node, "Bob", bob_client)
                
                alice_status = future_alice.result()
                bob_status = future_bob.result()
            
            # Mostra lo stato
            display_status(alice_status, bob_status, check_count)
            
            # Attendi prima del prossimo controllo
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Monitoraggio interrotto dall'utente.{RESET}")
        print(f"Totale controlli effettuati: {check_count}")
    except Exception as e:
        print(f"\n{RED}Errore durante il monitoraggio: {e}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()