#!/usr/bin/env python3
"""
Gestore del nodo Alice - Script per il dispositivo dedicato ad Alice
"""
import sys
import time
import os
from datetime import datetime
from src.alice_client import alice_client

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class AliceNodeManager:
    def __init__(self):
        self.node_name = "ALICE"
        self.check_certificates()
        
    def check_certificates(self):
        """Verifica che i certificati necessari per Alice siano presenti"""
        required_certs = ["ca.crt", "client_Alice2.crt", "client_Alice2.key"]
        missing = []
        
        for cert in required_certs:
            if not os.path.exists(f"certs/{cert}"):
                missing.append(cert)
        
        if missing:
            print(f"{RED}ERRORE: Certificati mancanti per {self.node_name}:{RESET}")
            for cert in missing:
                print(f"  - {cert}")
            print("\nCopia i certificati nella cartella certs/ e riprova.")
            sys.exit(1)
        
        # Verifica permessi chiave privata
        key_path = "certs/client_Alice2.key"
        if os.path.exists(key_path):
            stat_info = os.stat(key_path)
            if stat_info.st_mode & 0o077:
                print(f"{YELLOW}AVVISO: La chiave privata ha permessi troppo aperti.{RESET}")
                print(f"Esegui: chmod 600 {key_path}")
    
    def check_status(self):
        """Controlla lo stato del nodo Alice"""
        try:
            print(f"{BLUE}Controllo stato nodo {self.node_name}...{RESET}")
            start_time = time.time()
            
            client = alice_client()
            response = client.get("status")
            
            elapsed = time.time() - start_time
            
            print(f"{GREEN}✓ Nodo {self.node_name} ATTIVO{RESET}")
            print(f"  Tempo risposta: {elapsed:.2f}s")
            print(f"  Risposta: {response}")
            
            return True, response
            
        except Exception as e:
            print(f"{RED}✗ Nodo {self.node_name} NON ATTIVO{RESET}")
            print(f"  Errore: {str(e)}")
            
            # Suggerimenti basati sull'errore
            if "certificate" in str(e).lower():
                print(f"\n{YELLOW}Suggerimento:{RESET}")
                print("  - Verifica che i certificati siano validi")
                print("  - Controlla la data/ora del sistema")
                print("  - Verifica che il server riconosca il tuo certificato client")
            elif "connection" in str(e).lower():
                print(f"\n{YELLOW}Suggerimento:{RESET}")
                print("  - Verifica la connessione di rete")
                print("  - Controlla il firewall")
                print("  - Verifica che l'IP 78.40.171.143:443 sia raggiungibile")
                
            return False, None
    
    def get_keys(self, count=1):
        """Richiede chiavi quantistiche dal nodo Alice"""
        try:
            print(f"\n{BLUE}Richiesta {count} chiavi da {self.node_name}...{RESET}")
            
            client = alice_client()
            response = client.post("keys", {"count": count})
            
            print(f"{GREEN}✓ Chiavi ricevute con successo{RESET}")
            print(f"  Risposta: {response}")
            
            return True, response
            
        except Exception as e:
            print(f"{RED}✗ Errore nella richiesta chiavi{RESET}")
            print(f"  Errore: {str(e)}")
            return False, None
    
    def continuous_monitor(self, interval=30):
        """Monitoraggio continuo del nodo Alice"""
        print(f"{BLUE}=== Monitoraggio continuo nodo {self.node_name} ==={RESET}")
        print(f"Intervallo controlli: {interval} secondi")
        print(f"{YELLOW}Premi Ctrl+C per terminare{RESET}\n")
        
        check_count = 0
        failures = 0
        
        try:
            while True:
                check_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n[{timestamp}] Controllo #{check_count}")
                
                success, _ = self.check_status()
                
                if not success:
                    failures += 1
                    print(f"{RED}Fallimenti consecutivi: {failures}{RESET}")
                    
                    if failures >= 3:
                        print(f"{RED}ATTENZIONE: Il nodo è offline da {failures} controlli!{RESET}")
                else:
                    if failures > 0:
                        print(f"{GREEN}Il nodo è tornato online dopo {failures} fallimenti{RESET}")
                    failures = 0
                
                # Statistiche
                uptime = ((check_count - failures) / check_count) * 100
                print(f"\nStatistiche: Uptime: {uptime:.1f}% ({check_count - failures}/{check_count})")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Monitoraggio interrotto.{RESET}")
            print(f"Totale controlli: {check_count}")
            print(f"Uptime finale: {((check_count - failures) / check_count) * 100:.1f}%")

def main():
    print(f"{BLUE}╔{'═'*50}╗{RESET}")
    print(f"{BLUE}║{RESET} Gestore Nodo Quantistico ALICE {BLUE}║{RESET}")
    print(f"{BLUE}╚{'═'*50}╝{RESET}\n")
    
    manager = AliceNodeManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            manager.check_status()
            
        elif command == "monitor":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            manager.continuous_monitor(interval)
            
        elif command == "keys":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            manager.get_keys(count)
            
        else:
            print(f"{RED}Comando non riconosciuto: {command}{RESET}")
            print("\nUso:")
            print("  python alice_node_manager.py status     # Controlla stato")
            print("  python alice_node_manager.py monitor [intervallo]  # Monitoraggio continuo")
            print("  python alice_node_manager.py keys [numero]  # Richiedi chiavi")
            
    else:
        # Modalità interattiva
        while True:
            print("\n" + "="*50)
            print("MENU PRINCIPALE - Nodo ALICE")
            print("="*50)
            print("1. Verifica stato nodo")
            print("2. Monitoraggio continuo")
            print("3. Richiedi chiavi quantistiche")
            print("4. Esci")
            print("="*50)
            
            choice = input("\nSeleziona opzione (1-4): ")
            
            if choice == "1":
                manager.check_status()
                input("\nPremi INVIO per continuare...")
                
            elif choice == "2":
                interval = input("Intervallo controlli in secondi (default 30): ")
                interval = int(interval) if interval else 30
                manager.continuous_monitor(interval)
                
            elif choice == "3":
                count = input("Numero di chiavi da richiedere (default 1): ")
                count = int(count) if count else 1
                manager.get_keys(count)
                input("\nPremi INVIO per continuare...")
                
            elif choice == "4":
                print(f"\n{YELLOW}Uscita dal gestore nodo ALICE.{RESET}")
                break
                
            else:
                print(f"{RED}Opzione non valida!{RESET}")

if __name__ == "__main__":
    main()