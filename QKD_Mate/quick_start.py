#!/usr/bin/env python3
"""
QKD_Mate Quick Start
===================

Script di avvio rapido che guida l'utente attraverso il primo utilizzo
di QKD_Mate con un'esperienza semplificata e intuitiva.

Funzionalità:
- Rilevamento automatico dello stato dell'installazione
- Setup guidato se necessario
- Avvio diretto del nodo manager
- Diagnostica automatica
- Suggerimenti contestuali

Uso:
    python quick_start.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class QuickStart:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.certs_dir = self.project_root / "certs"
        self.node_config = self.project_root / "node_config.yaml"
    
    def print_welcome(self):
        """Stampa messaggio di benvenuto"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{BOLD}🚀 Benvenuto in QKD_Mate! 🚀{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"{CYAN}Client per Quantum Key Distribution conforme ETSI GS QKD 014{RESET}\n")
    
    def check_installation_status(self):
        """Controlla lo stato dell'installazione"""
        print(f"{BLUE}🔍 Controllo stato installazione...{RESET}")
        
        issues = []
        
        # Controlla dipendenze Python
        try:
            import requests
            import yaml
            print(f"{GREEN}✅ Dipendenze Python installate{RESET}")
        except ImportError as e:
            issues.append(("dependencies", f"Dipendenze mancanti: {e}"))
            print(f"{RED}❌ Dipendenze Python mancanti{RESET}")
        
        # Controlla directory certificati
        if self.certs_dir.exists():
            cert_files = list(self.certs_dir.glob('*'))
            if cert_files:
                print(f"{GREEN}✅ Directory certificati presente ({len(cert_files)} file){RESET}")
            else:
                issues.append(("certificates", "Directory certificati vuota"))
                print(f"{YELLOW}⚠️  Directory certificati vuota{RESET}")
        else:
            issues.append(("certificates", "Directory certificati mancante"))
            print(f"{RED}❌ Directory certificati mancante{RESET}")
        
        # Controlla configurazione nodo
        if self.node_config.exists():
            print(f"{GREEN}✅ Configurazione nodo presente{RESET}")
        else:
            issues.append(("config", "Configurazione nodo mancante"))
            print(f"{YELLOW}⚠️  Configurazione nodo mancante{RESET}")
        
        return issues
    
    def suggest_fixes(self, issues):
        """Suggerisce correzioni per i problemi trovati"""
        if not issues:
            return True
        
        print(f"\n{YELLOW}🔧 Problemi rilevati che richiedono attenzione:{RESET}")
        
        for issue_type, description in issues:
            print(f"  • {description}")
        
        print(f"\n{CYAN}💡 Soluzioni suggerite:{RESET}")
        
        if any(issue[0] == "dependencies" for issue in issues):
            print(f"  🔹 Installa dipendenze: {YELLOW}python setup.py{RESET}")
        
        if any(issue[0] == "certificates" for issue in issues):
            print(f"  🔹 Installa certificati: {YELLOW}python cert_manager.py install{RESET}")
        
        if any(issue[0] == "config" for issue in issues):
            print(f"  🔹 Configura nodo: {YELLOW}python setup.py{RESET}")
        
        print(f"\n{CYAN}🚀 Setup completo automatico: {YELLOW}python install.py{RESET}")
        
        # Chiedi se procedere con il fix automatico
        print(f"\n{YELLOW}Vuoi eseguire il setup automatico ora? (s/n): {RESET}", end="")
        response = input().strip().lower()
        
        if response in ['s', 'si', 'y', 'yes']:
            return self.run_automatic_setup()
        else:
            print(f"{CYAN}Puoi eseguire il setup manualmente quando vuoi.{RESET}")
            return False
    
    def run_automatic_setup(self):
        """Esegue il setup automatico"""
        print(f"\n{BLUE}🔧 Avvio setup automatico...{RESET}")
        
        try:
            # Esegui setup.py
            result = subprocess.run([sys.executable, "setup.py"], 
                                  cwd=self.project_root,
                                  capture_output=False)
            
            if result.returncode == 0:
                print(f"{GREEN}✅ Setup completato con successo!{RESET}")
                return True
            else:
                print(f"{RED}❌ Setup fallito{RESET}")
                return False
                
        except Exception as e:
            print(f"{RED}❌ Errore durante setup: {e}{RESET}")
            return False
    
    def show_quick_actions(self):
        """Mostra azioni rapide disponibili"""
        print(f"\n{BLUE}🎯 Azioni rapide disponibili:{RESET}")
        print(f"  1. {CYAN}Avvia Node Manager{RESET} - Interfaccia principale")
        print(f"  2. {CYAN}Test di connettività{RESET} - Verifica stato nodi")
        print(f"  3. {CYAN}Diagnostica completa{RESET} - Controllo sistema completo")
        print(f"  4. {CYAN}Gestione certificati{RESET} - Installa/valida certificati")
        print(f"  5. {CYAN}Setup configurazione{RESET} - Riconfigura il sistema")
        print(f"  6. {CYAN}Esci{RESET}")
        
        while True:
            choice = input(f"\n{YELLOW}Seleziona un'azione (1-6): {RESET}").strip()
            
            if choice == "1":
                self.launch_node_manager()
                break
            elif choice == "2":
                self.run_connectivity_test()
            elif choice == "3":
                self.run_diagnostics()
            elif choice == "4":
                self.launch_cert_manager()
            elif choice == "5":
                self.launch_setup()
            elif choice == "6":
                print(f"{CYAN}Arrivederci! 👋{RESET}")
                break
            else:
                print(f"{RED}❌ Scelta non valida. Inserisci un numero da 1 a 6.{RESET}")
    
    def launch_node_manager(self):
        """Avvia il node manager"""
        print(f"\n{BLUE}🚀 Avvio Node Manager...{RESET}")
        try:
            subprocess.run([sys.executable, "qkd_node_manager.py"], 
                          cwd=self.project_root)
        except KeyboardInterrupt:
            print(f"\n{CYAN}Node Manager chiuso.{RESET}")
        except Exception as e:
            print(f"{RED}❌ Errore avviando Node Manager: {e}{RESET}")
    
    def run_connectivity_test(self):
        """Esegue test di connettività rapido"""
        print(f"\n{BLUE}🌐 Test di connettività...{RESET}")
        try:
            result = subprocess.run([sys.executable, "qkd_node_manager.py", "status"], 
                                  cwd=self.project_root,
                                  capture_output=False)
            input(f"\n{YELLOW}Premi INVIO per continuare...{RESET}")
        except Exception as e:
            print(f"{RED}❌ Errore nel test: {e}{RESET}")
    
    def run_diagnostics(self):
        """Esegue diagnostica completa"""
        print(f"\n{BLUE}🔬 Diagnostica completa...{RESET}")
        try:
            result = subprocess.run([sys.executable, "qkd_node_manager.py", "diagnostic"], 
                                  cwd=self.project_root,
                                  capture_output=False)
            input(f"\n{YELLOW}Premi INVIO per continuare...{RESET}")
        except Exception as e:
            print(f"{RED}❌ Errore nella diagnostica: {e}{RESET}")
    
    def launch_cert_manager(self):
        """Avvia il gestore certificati"""
        print(f"\n{BLUE}🔐 Gestione certificati...{RESET}")
        print(f"  1. Installa certificati")
        print(f"  2. Valida certificati esistenti")
        print(f"  3. Ripara problemi certificati")
        print(f"  4. Lista certificati")
        print(f"  5. Torna indietro")
        
        choice = input(f"\n{YELLOW}Scelta (1-5): {RESET}").strip()
        
        commands = {
            "1": "install",
            "2": "validate", 
            "3": "fix",
            "4": "list"
        }
        
        if choice in commands:
            try:
                subprocess.run([sys.executable, "cert_manager.py", commands[choice]], 
                              cwd=self.project_root,
                              capture_output=False)
                input(f"\n{YELLOW}Premi INVIO per continuare...{RESET}")
            except Exception as e:
                print(f"{RED}❌ Errore: {e}{RESET}")
        elif choice != "5":
            print(f"{RED}❌ Scelta non valida{RESET}")
    
    def launch_setup(self):
        """Avvia il setup"""
        print(f"\n{BLUE}⚙️  Setup configurazione...{RESET}")
        try:
            subprocess.run([sys.executable, "setup.py"], 
                          cwd=self.project_root,
                          capture_output=False)
        except Exception as e:
            print(f"{RED}❌ Errore nel setup: {e}{RESET}")
    
    def run(self):
        """Esegue il quick start"""
        self.print_welcome()
        
        # Controlla stato installazione
        issues = self.check_installation_status()
        
        if issues:
            # Se ci sono problemi, cerca di risolverli
            if not self.suggest_fixes(issues):
                print(f"\n{YELLOW}⚠️  Alcuni problemi devono essere risolti prima di continuare.{RESET}")
                print(f"{CYAN}Esegui il setup quando sei pronto e riprova.{RESET}")
                return
            
            # Ricontrolla dopo il fix
            issues = self.check_installation_status()
        
        if not issues:
            print(f"\n{GREEN}🎉 Sistema pronto all'uso!{RESET}")
            self.show_quick_actions()
        else:
            print(f"\n{YELLOW}⚠️  Alcuni problemi persistono. Controlla la documentazione.{RESET}")

def main():
    quick_start = QuickStart()
    quick_start.run()

if __name__ == "__main__":
    main()