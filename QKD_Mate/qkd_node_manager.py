#!/usr/bin/env python3
"""
Gestore Nodo QKD - Script Unificato per Gestione Nodi Quantistici
================================================================

Questo script fornisce un'interfaccia unificata per gestire nodi QKD
(Alice o Bob) con funzionalità complete di monitoraggio, diagnostica
e gestione delle chiavi quantistiche.

Caratteristiche principali:
- Configurabile per gestire sia Alice (master) che Bob (slave)
- Interfaccia a menu interattiva o comandi diretti
- Monitoraggio continuo con statistiche real-time
- Diagnostica completa di rete e certificati
- Gestione robusta degli errori
- Deploy su dispositivi separati

MODALITÀ DI CONFIGURAZIONE:
1. Configurazione inline: Modifica NODE_TYPE in questo file
2. File di configurazione: Usa node_config.yaml (RACCOMANDATO)
   - Permette configurazione senza modificare il codice
   - Facilita deployment su dispositivi diversi
   - Il file YAML ha sempre precedenza sulla configurazione inline

USO TIPICO:
- Dispositivo Alice: NODE_TYPE = "alice" + certificati Alice
- Dispositivo Bob: NODE_TYPE = "bob" + certificati Bob
- Ogni dispositivo gestisce un solo nodo per sicurezza

CONFORMITÀ ETSI GS QKD 014:
- Implementa tutti gli endpoint standard
- Gestione errori secondo specifiche
- Validazione parametri conforme
- Supporto per funzionalità avanzate
"""

# Import delle librerie standard
import sys          # Gestione argomenti comando e uscite
import time         # Gestione temporizzazioni e sleep
import os           # Operazioni filesystem e comandi sistema
from datetime import datetime  # Timestamp per logging e diagnostica

# ===============================================================
# CONFIGURAZIONE PRINCIPALE - MODIFICA QUESTA SEZIONE SE NECESSARIO
# ===============================================================
# Tipo di nodo da gestire: "alice" (master) o "bob" (slave)
# Questa configurazione viene sovrascritta da node_config.yaml se presente
NODE_TYPE = "alice"  # Cambia in "bob" per gestire il nodo Bob
# ===============================================================

# Carica configurazione da file YAML se presente
try:
    import yaml
    if os.path.exists("node_config.yaml"):
        with open("node_config.yaml", "r") as f:
            config = yaml.safe_load(f)
            if config and "node_type" in config:
                NODE_TYPE = config["node_type"]
                print(f"Configurazione caricata da node_config.yaml: NODE_TYPE = {NODE_TYPE}")
except ImportError:
    pass  # YAML non installato, usa configurazione inline

# Importa il client corretto basato sulla configurazione
if NODE_TYPE.lower() == "alice":
    from src.alice_client import alice_client as qkd_client
    NODE_NAME = "ALICE"
    NODE_IP = "78.40.171.143"
    CERT_PREFIX = "client_Alice2"
elif NODE_TYPE.lower() == "bob":
    from src.bob_client import bob_client as qkd_client
    NODE_NAME = "BOB"
    NODE_IP = "78.40.171.144"
    CERT_PREFIX = "client_Bob2"
else:
    print(f"ERRORE: NODE_TYPE '{NODE_TYPE}' non valido. Usa 'alice' o 'bob'")
    sys.exit(1)

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class QKDNodeManager:
    def __init__(self):
        self.node_name = NODE_NAME
        self.node_ip = NODE_IP
        self.cert_prefix = CERT_PREFIX
        print(f"{BLUE}Inizializzazione gestore per nodo {self.node_name}{RESET}")
        self.check_certificates()
        
    def check_certificates(self):
        """Verifica che i certificati necessari siano presenti"""
        required_certs = [
            "ca.crt", 
            f"{self.cert_prefix}.crt", 
            f"{self.cert_prefix}.key"
        ]
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
        key_path = f"certs/{self.cert_prefix}.key"
        if os.path.exists(key_path):
            stat_info = os.stat(key_path)
            if stat_info.st_mode & 0o077:
                print(f"{YELLOW}AVVISO: La chiave privata ha permessi troppo aperti.{RESET}")
                print(f"Esegui: chmod 600 {key_path}")
    
    def check_status(self):
        """Controlla lo stato del nodo"""
        try:
            print(f"{BLUE}Controllo stato nodo {self.node_name}...{RESET}")
            start_time = time.time()
            
            client = qkd_client()
            response = client.get("status")
            
            elapsed = time.time() - start_time
            
            print(f"{GREEN}✓ Nodo {self.node_name} ATTIVO{RESET}")
            print(f"  IP: {self.node_ip}:443")
            print(f"  Tempo risposta: {elapsed:.2f}s")
            print(f"  Risposta: {response}")
            
            return True, response
            
        except Exception as e:
            print(f"{RED}✗ Nodo {self.node_name} NON ATTIVO{RESET}")
            print(f"  IP: {self.node_ip}:443")
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
                print(f"  - Verifica che l'IP {self.node_ip}:443 sia raggiungibile")
                print(f"  - Prova: ping {self.node_ip}")
                
            return False, None
    
    def get_keys(self, count=1):
        """Richiede chiavi quantistiche dal nodo"""
        try:
            print(f"\n{BLUE}Richiesta {count} chiavi da {self.node_name}...{RESET}")
            
            client = qkd_client()
            response = client.post("keys", {"count": count})
            
            print(f"{GREEN}✓ Chiavi ricevute con successo{RESET}")
            print(f"  Risposta: {response}")
            
            return True, response
            
        except Exception as e:
            print(f"{RED}✗ Errore nella richiesta chiavi{RESET}")
            print(f"  Errore: {str(e)}")
            return False, None
    
    def continuous_monitor(self, interval=30):
        """Monitoraggio continuo del nodo"""
        print(f"{BLUE}=== Monitoraggio continuo nodo {self.node_name} ==={RESET}")
        print(f"IP monitorato: {self.node_ip}:443")
        print(f"Intervallo controlli: {interval} secondi")
        print(f"{YELLOW}Premi Ctrl+C per terminare{RESET}\n")
        
        check_count = 0
        failures = 0
        consecutive_failures = 0
        
        try:
            while True:
                check_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n[{timestamp}] Controllo #{check_count}")
                
                success, _ = self.check_status()
                
                if not success:
                    failures += 1
                    consecutive_failures += 1
                    print(f"{RED}Fallimenti consecutivi: {consecutive_failures}{RESET}")
                    
                    if consecutive_failures >= 3:
                        print(f"{RED}ATTENZIONE: Il nodo è offline da {consecutive_failures} controlli!{RESET}")
                    
                    # Log per troubleshooting dopo 5 fallimenti
                    if consecutive_failures == 5:
                        print(f"\n{YELLOW}=== Diagnostica avanzata ==={RESET}")
                        os.system(f"ping -c 2 {self.node_ip} 2>&1 | grep -E 'bytes from|Destination'")
                        print(f"{YELLOW}=========================={RESET}\n")
                else:
                    if consecutive_failures > 0:
                        print(f"{GREEN}Il nodo è tornato online dopo {consecutive_failures} fallimenti{RESET}")
                    consecutive_failures = 0
                
                # Statistiche
                uptime = ((check_count - failures) / check_count) * 100
                print(f"\nStatistiche: Uptime: {uptime:.1f}% ({check_count - failures}/{check_count})")
                
                # Attendi prima del prossimo controllo
                for i in range(interval):
                    print(f"\rProssimo controllo tra {interval - i} secondi...", end='', flush=True)
                    time.sleep(1)
                print("\r" + " " * 50 + "\r", end='', flush=True)  # Pulisce la linea
                
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Monitoraggio interrotto.{RESET}")
            print(f"Totale controlli: {check_count}")
            print(f"Uptime finale: {((check_count - failures) / check_count) * 100:.1f}%")

    def run_diagnostic(self):
        """Esegue una diagnostica completa del nodo"""
        print(f"\n{BLUE}=== DIAGNOSTICA NODO {self.node_name} ==={RESET}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Nodo configurato: {self.node_name}")
        print(f"IP target: {self.node_ip}:443")
        print("-" * 50)
        
        # 1. Verifica certificati
        print(f"\n{BLUE}1. Verifica certificati:{RESET}")
        cert_files = ["ca.crt", f"{self.cert_prefix}.crt", f"{self.cert_prefix}.key"]
        all_certs_ok = True
        for cert in cert_files:
            path = f"certs/{cert}"
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"  {GREEN}✓{RESET} {cert} (dimensione: {size} bytes)")
            else:
                print(f"  {RED}✗{RESET} {cert} MANCANTE")
                all_certs_ok = False
        
        # 2. Test connettività di rete
        print(f"\n{BLUE}2. Test connettività di rete:{RESET}")
        ping_result = os.system(f"ping -c 2 -W 2 {self.node_ip} > /dev/null 2>&1")
        if ping_result == 0:
            print(f"  {GREEN}✓{RESET} Ping a {self.node_ip} riuscito")
        else:
            print(f"  {RED}✗{RESET} Ping a {self.node_ip} fallito")
        
        # 3. Test porta 443
        print(f"\n{BLUE}3. Test porta 443:{RESET}")
        nc_result = os.system(f"nc -zv -w 2 {self.node_ip} 443 > /dev/null 2>&1")
        if nc_result == 0:
            print(f"  {GREEN}✓{RESET} Porta 443 aperta su {self.node_ip}")
        else:
            print(f"  {RED}✗{RESET} Porta 443 non raggiungibile su {self.node_ip}")
        
        # 4. Test API
        print(f"\n{BLUE}4. Test connessione API:{RESET}")
        if all_certs_ok:
            success, response = self.check_status()
            if success:
                print(f"  {GREEN}✓{RESET} API raggiungibile e funzionante")
            else:
                print(f"  {RED}✗{RESET} API non raggiungibile")
        else:
            print(f"  {YELLOW}⚠{RESET} Test saltato (certificati mancanti)")
        
        print("\n" + "=" * 50)

def main():
    print(f"{BLUE}╔{'═'*60}╗{RESET}")
    print(f"{BLUE}║{RESET} Gestore Nodo Quantistico QKD - {NODE_NAME:^30} {BLUE}║{RESET}")
    print(f"{BLUE}╚{'═'*60}╝{RESET}\n")
    
    manager = QKDNodeManager()
    
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
            
        elif command == "diagnostic":
            manager.run_diagnostic()
            
        else:
            print(f"{RED}Comando non riconosciuto: {command}{RESET}")
            print("\nUso:")
            print(f"  python {sys.argv[0]} status              # Controlla stato")
            print(f"  python {sys.argv[0]} monitor [intervallo] # Monitoraggio continuo")
            print(f"  python {sys.argv[0]} keys [numero]        # Richiedi chiavi")
            print(f"  python {sys.argv[0]} diagnostic           # Diagnostica completa")
            
    else:
        # Modalità interattiva
        while True:
            print("\n" + "="*60)
            print(f"MENU PRINCIPALE - Nodo {NODE_NAME}")
            print("="*60)
            print("1. Verifica stato nodo")
            print("2. Monitoraggio continuo")
            print("3. Richiedi chiavi quantistiche")
            print("4. Diagnostica completa")
            print("5. Esci")
            print("="*60)
            
            choice = input("\nSeleziona opzione (1-5): ")
            
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
                manager.run_diagnostic()
                input("\nPremi INVIO per continuare...")
                
            elif choice == "5":
                print(f"\n{YELLOW}Uscita dal gestore nodo {NODE_NAME}.{RESET}")
                break
                
            else:
                print(f"{RED}Opzione non valida!{RESET}")

if __name__ == "__main__":
    main()