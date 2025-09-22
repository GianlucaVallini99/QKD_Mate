#!/usr/bin/env python3
"""
QKD_Mate Setup Script - Installazione Automatizzata
=================================================

Script di installazione automatica per QKD_Mate che semplifica
il processo di setup su qualsiasi PC.

Funzionalità:
- Installazione automatica delle dipendenze Python
- Setup guidato della configurazione del nodo
- Gestione automatica dei certificati
- Validazione della configurazione
- Test di connettività automatico

Uso:
    python setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class QKDSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.certs_dir = self.project_root / "certs"
        self.node_config_path = self.project_root / "node_config.yaml"
        
    def print_header(self):
        """Stampa l'header di benvenuto"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{BOLD}🔐 QKD_Mate - Setup Automatizzato 🔐{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"{CYAN}Installazione semplificata per client Quantum Key Distribution{RESET}")
        print(f"{CYAN}Conforme allo standard ETSI GS QKD 014{RESET}\n")
    
    def check_python_version(self):
        """Verifica che la versione di Python sia compatibile"""
        print(f"{BLUE}🐍 Controllo versione Python...{RESET}")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            print(f"{RED}❌ Python 3.10+ richiesto. Versione attuale: {version.major}.{version.minor}{RESET}")
            print(f"{YELLOW}Aggiorna Python e riprova.{RESET}")
            return False
        
        print(f"{GREEN}✅ Python {version.major}.{version.minor}.{version.micro} - OK{RESET}")
        return True
    
    def install_dependencies(self):
        """Installa le dipendenze Python automaticamente"""
        print(f"\n{BLUE}📦 Installazione dipendenze...{RESET}")
        
        try:
            # Controlla se pip è disponibile
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"{RED}❌ pip non trovato. Installa pip e riprova.{RESET}")
            return False
        
        try:
            # Installa dipendenze
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"{GREEN}✅ Dipendenze installate con successo{RESET}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{RED}❌ Errore nell'installazione delle dipendenze:{RESET}")
            print(f"{RED}{e.stderr}{RESET}")
            return False
    
    def setup_certificates_directory(self):
        """Crea la directory dei certificati se non existe"""
        print(f"\n{BLUE}🔐 Setup directory certificati...{RESET}")
        
        if not self.certs_dir.exists():
            self.certs_dir.mkdir(mode=0o700)
            print(f"{GREEN}✅ Directory certs/ creata{RESET}")
        else:
            print(f"{YELLOW}⚠️  Directory certs/ già esistente{RESET}")
        
        return True
    
    def interactive_node_configuration(self):
        """Configurazione interattiva del tipo di nodo"""
        print(f"\n{BLUE}⚙️  Configurazione nodo QKD...{RESET}")
        print(f"{CYAN}Seleziona il tipo di nodo che vuoi configurare:{RESET}\n")
        
        print("1. Alice (Master SAE) - IP: 78.40.171.143")
        print("2. Bob (Slave SAE) - IP: 78.40.171.144")
        print("3. Configura manualmente più tardi")
        
        while True:
            choice = input(f"\n{YELLOW}Scelta (1-3): {RESET}").strip()
            
            if choice == "1":
                node_type = "alice"
                print(f"{GREEN}✅ Configurato come Alice (Master){RESET}")
                break
            elif choice == "2":
                node_type = "bob"
                print(f"{GREEN}✅ Configurato come Bob (Slave){RESET}")
                break
            elif choice == "3":
                print(f"{YELLOW}⚠️  Configurazione rimandata. Modifica node_config.yaml manualmente.{RESET}")
                return True
            else:
                print(f"{RED}❌ Scelta non valida. Inserisci 1, 2 o 3.{RESET}")
        
        # Crea il file di configurazione
        config_content = f"node_type: {node_type}\n"
        with open(self.node_config_path, "w") as f:
            f.write(config_content)
        
        print(f"{GREEN}✅ File node_config.yaml creato{RESET}")
        return True
    
    def check_certificates_status(self):
        """Controlla lo stato dei certificati"""
        print(f"\n{BLUE}🔍 Controllo certificati...{RESET}")
        
        # Leggi la configurazione del nodo se existe
        node_type = None
        if self.node_config_path.exists():
            try:
                import yaml
                with open(self.node_config_path) as f:
                    config = yaml.safe_load(f)
                    node_type = config.get('node_type')
            except:
                pass
        
        required_certs = ["ca.crt"]
        if node_type == "alice":
            required_certs.extend(["client_Alice2.crt", "client_Alice2.key"])
        elif node_type == "bob":
            required_certs.extend(["client_Bob2.crt", "client_Bob2.key"])
        else:
            required_certs.extend([
                "client_Alice2.crt", "client_Alice2.key",
                "client_Bob2.crt", "client_Bob2.key"
            ])
        
        missing_certs = []
        present_certs = []
        
        for cert in required_certs:
            cert_path = self.certs_dir / cert
            if cert_path.exists():
                present_certs.append(cert)
                # Controlla permessi per le chiavi private
                if cert.endswith('.key'):
                    stat_info = cert_path.stat()
                    if stat_info.st_mode & 0o077:
                        print(f"{YELLOW}⚠️  {cert} ha permessi troppo aperti{RESET}")
                        cert_path.chmod(0o600)
                        print(f"{GREEN}✅ Permessi corretti impostati per {cert}{RESET}")
            else:
                missing_certs.append(cert)
        
        if present_certs:
            print(f"{GREEN}✅ Certificati trovati: {', '.join(present_certs)}{RESET}")
        
        if missing_certs:
            print(f"{YELLOW}⚠️  Certificati mancanti: {', '.join(missing_certs)}{RESET}")
            print(f"\n{CYAN}📋 Per completare l'installazione:{RESET}")
            print(f"1. Copia i certificati mancanti nella directory certs/")
            print(f"2. Esegui: python setup.py --verify")
            print(f"3. Oppure usa: python qkd_node_manager.py diagnostic")
            return False
        
        print(f"{GREEN}🎉 Tutti i certificati richiesti sono presenti!{RESET}")
        return True
    
    def test_connectivity(self):
        """Test di connettività di base"""
        print(f"\n{BLUE}🌐 Test connettività di rete...{RESET}")
        
        # Test ping agli endpoint
        endpoints = [
            ("Alice KME", "78.40.171.143"),
            ("Bob KME", "78.40.171.144")
        ]
        
        connectivity_ok = True
        for name, ip in endpoints:
            print(f"  Testing {name} ({ip})...", end=" ")
            
            # Usa ping appropriato per il sistema operativo
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", "2000", ip]
            else:
                cmd = ["ping", "-c", "1", "-W", "2", ip]
            
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f"{GREEN}✅{RESET}")
                else:
                    print(f"{RED}❌{RESET}")
                    connectivity_ok = False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"{YELLOW}⚠️{RESET}")
                connectivity_ok = False
        
        if connectivity_ok:
            print(f"{GREEN}🌐 Connettività di rete OK{RESET}")
        else:
            print(f"{YELLOW}⚠️  Alcuni endpoint non sono raggiungibili{RESET}")
            print(f"{CYAN}Questo potrebbe essere normale se i KME non sono attivi{RESET}")
        
        return True
    
    def create_quick_start_script(self):
        """Crea uno script di avvio rapido"""
        print(f"\n{BLUE}🚀 Creazione script di avvio rapido...{RESET}")
        
        if platform.system().lower() == "windows":
            script_name = "start_qkd.bat"
            script_content = """@echo off
echo Starting QKD Node Manager...
python qkd_node_manager.py
pause
"""
        else:
            script_name = "start_qkd.sh"
            script_content = """#!/bin/bash
echo "Starting QKD Node Manager..."
python3 qkd_node_manager.py
"""
        
        script_path = self.project_root / script_name
        with open(script_path, "w") as f:
            f.write(script_content)
        
        if not platform.system().lower() == "windows":
            script_path.chmod(0o755)
        
        print(f"{GREEN}✅ Script di avvio creato: {script_name}{RESET}")
        return True
    
    def print_completion_summary(self):
        """Stampa il riassunto dell'installazione"""
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}{BOLD}🎉 INSTALLAZIONE COMPLETATA! 🎉{RESET}")
        print(f"{GREEN}{'='*70}{RESET}")
        
        print(f"\n{CYAN}📋 Prossimi passi:{RESET}")
        print(f"1. {YELLOW}Copia i certificati nella directory certs/{RESET}")
        print(f"2. {YELLOW}Avvia con: python qkd_node_manager.py{RESET}")
        
        if platform.system().lower() == "windows":
            print(f"   {CYAN}Oppure fai doppio click su: start_qkd.bat{RESET}")
        else:
            print(f"   {CYAN}Oppure esegui: ./start_qkd.sh{RESET}")
        
        print(f"\n{CYAN}🔧 Comandi utili:{RESET}")
        print(f"  {YELLOW}python qkd_node_manager.py diagnostic{RESET} - Test completo")
        print(f"  {YELLOW}python qkd_node_manager.py status{RESET}     - Verifica stato")
        print(f"  {YELLOW}python setup.py --verify{RESET}              - Verifica setup")
        
        print(f"\n{BLUE}📖 Per maggiori informazioni consulta il README.md{RESET}")
    
    def verify_installation(self):
        """Verifica l'installazione esistente"""
        print(f"\n{BLUE}🔍 Verifica installazione esistente...{RESET}")
        
        checks = [
            ("Python 3.10+", self.check_python_version()),
            ("Dipendenze", self.check_dependencies()),
            ("Directory certs", self.certs_dir.exists()),
            ("Configurazione nodo", self.node_config_path.exists()),
        ]
        
        all_ok = True
        for name, status in checks:
            if status:
                print(f"{GREEN}✅ {name}{RESET}")
            else:
                print(f"{RED}❌ {name}{RESET}")
                all_ok = False
        
        if all_ok:
            self.check_certificates_status()
            print(f"\n{GREEN}🎉 Installazione verificata con successo!{RESET}")
        else:
            print(f"\n{YELLOW}⚠️  Alcuni controlli falliti. Esegui setup completo.{RESET}")
        
        return all_ok
    
    def check_dependencies(self):
        """Controlla se le dipendenze sono installate"""
        try:
            import requests
            import yaml
            return True
        except ImportError:
            return False
    
    def run_full_setup(self):
        """Esegue il setup completo"""
        self.print_header()
        
        steps = [
            ("Controllo Python", self.check_python_version),
            ("Installazione dipendenze", self.install_dependencies),
            ("Setup certificati", self.setup_certificates_directory),
            ("Configurazione nodo", self.interactive_node_configuration),
            ("Controllo certificati", self.check_certificates_status),
            ("Test connettività", self.test_connectivity),
            ("Script avvio rapido", self.create_quick_start_script),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n{RED}❌ Setup interrotto al passo: {step_name}{RESET}")
                return False
        
        self.print_completion_summary()
        return True

def main():
    setup = QKDSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        setup.verify_installation()
    else:
        setup.run_full_setup()

if __name__ == "__main__":
    main()