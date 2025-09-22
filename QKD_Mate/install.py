#!/usr/bin/env python3
"""
QKD_Mate Universal Installer
===========================

Installer universale per QKD_Mate che funziona su Windows, Linux e macOS.
Automatizza completamente il processo di installazione.

Caratteristiche:
- Installazione con un solo comando
- Rilevamento automatico del sistema operativo
- Setup completo senza intervento manuale (modalità silent)
- Installazione guidata interattiva
- Creazione di shortcut desktop
- Registrazione nel sistema

Uso:
    python install.py                    # Installazione guidata
    python install.py --silent          # Installazione automatica
    python install.py --uninstall       # Disinstallazione
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import json

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class UniversalInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent.resolve()
        self.project_name = "QKD_Mate"
        
        # Percorsi di installazione per sistema
        self.install_paths = {
            'windows': Path.home() / "AppData" / "Local" / self.project_name,
            'linux': Path.home() / ".local" / "share" / self.project_name,
            'darwin': Path.home() / "Applications" / self.project_name  # macOS
        }
        
        self.install_path = self.install_paths.get(self.system, 
                                                  Path.home() / self.project_name)
        
        # File di configurazione installazione
        self.install_config = self.install_path / "install_info.json"
    
    def print_banner(self):
        """Stampa banner di installazione"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{BOLD}🚀 QKD_Mate Universal Installer 🚀{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"{CYAN}Sistema rilevato: {platform.system()} {platform.release()}{RESET}")
        print(f"{CYAN}Architettura: {platform.machine()}{RESET}")
        print(f"{CYAN}Python: {sys.version.split()[0]}{RESET}")
        print(f"{CYAN}Percorso installazione: {self.install_path}{RESET}\n")
    
    def check_requirements(self):
        """Controlla i requisiti di sistema"""
        print(f"{BLUE}🔍 Controllo requisiti di sistema...{RESET}")
        
        # Controllo versione Python
        if sys.version_info < (3, 10):
            print(f"{RED}❌ Python 3.10+ richiesto. Versione attuale: {sys.version.split()[0]}{RESET}")
            return False
        
        print(f"{GREEN}✅ Python {sys.version.split()[0]} - OK{RESET}")
        
        # Controllo pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print(f"{GREEN}✅ pip disponibile{RESET}")
        except subprocess.CalledProcessError:
            print(f"{RED}❌ pip non trovato{RESET}")
            return False
        
        # Controllo spazio disco (almeno 50MB)
        try:
            free_space = shutil.disk_usage(Path.home()).free
            if free_space < 50 * 1024 * 1024:  # 50MB
                print(f"{RED}❌ Spazio disco insufficiente{RESET}")
                return False
            print(f"{GREEN}✅ Spazio disco sufficiente{RESET}")
        except:
            print(f"{YELLOW}⚠️  Impossibile verificare spazio disco{RESET}")
        
        return True
    
    def install_application(self, silent=False):
        """Installa l'applicazione"""
        print(f"\n{BLUE}📦 Installazione QKD_Mate...{RESET}")
        
        # Crea directory di installazione
        self.install_path.mkdir(parents=True, exist_ok=True)
        print(f"{GREEN}✅ Directory di installazione creata{RESET}")
        
        # Copia file del progetto
        files_to_copy = [
            "qkd_node_manager.py",
            "setup.py",
            "cert_manager.py",
            "requirements.txt",
            "README.md",
            "LICENSE",
            "node_config.yaml",
            "src/",
            "config/",
            "examples/"
        ]
        
        copied_files = []
        for item in files_to_copy:
            source = self.project_root / item
            if source.exists():
                dest = self.install_path / item
                
                if source.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
                    print(f"{GREEN}✅ Copiata directory: {item}{RESET}")
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                    print(f"{GREEN}✅ Copiato file: {item}{RESET}")
                
                copied_files.append(item)
        
        # Crea directory certs
        certs_dir = self.install_path / "certs"
        certs_dir.mkdir(exist_ok=True)
        print(f"{GREEN}✅ Directory certificati creata{RESET}")
        
        # Installa dipendenze Python
        print(f"\n{BLUE}📚 Installazione dipendenze Python...{RESET}")
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r", 
                   str(self.install_path / "requirements.txt")]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"{GREEN}✅ Dipendenze installate{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{RED}❌ Errore installazione dipendenze: {e}{RESET}")
            return False
        
        # Configurazione iniziale se non in modalità silent
        if not silent:
            self.interactive_initial_setup()
        
        # Crea script di avvio
        self.create_launcher_scripts()
        
        # Crea shortcut desktop se possibile
        self.create_desktop_shortcut()
        
        # Salva informazioni installazione
        install_info = {
            "install_date": str(datetime.now()),
            "install_path": str(self.install_path),
            "version": "1.0.0",
            "system": platform.system(),
            "python_version": sys.version.split()[0],
            "files": copied_files
        }
        
        with open(self.install_config, "w") as f:
            json.dump(install_info, f, indent=2)
        
        print(f"\n{GREEN}🎉 Installazione completata con successo!{RESET}")
        return True
    
    def interactive_initial_setup(self):
        """Setup iniziale interattivo"""
        print(f"\n{BLUE}⚙️  Configurazione iniziale...{RESET}")
        
        # Configurazione tipo nodo
        print(f"{CYAN}Configurazione tipo di nodo QKD:{RESET}")
        print("1. Alice (Master SAE)")
        print("2. Bob (Slave SAE)")
        print("3. Configura più tardi")
        
        while True:
            choice = input(f"\n{YELLOW}Scelta (1-3): {RESET}").strip()
            
            if choice in ["1", "2", "3"]:
                if choice == "1":
                    node_type = "alice"
                elif choice == "2":
                    node_type = "bob"
                else:
                    node_type = None
                break
            else:
                print(f"{RED}❌ Scelta non valida{RESET}")
        
        # Salva configurazione se specificata
        if node_type:
            config_path = self.install_path / "node_config.yaml"
            with open(config_path, "w") as f:
                f.write(f"node_type: {node_type}\n")
            print(f"{GREEN}✅ Configurazione salvata: {node_type}{RESET}")
    
    def create_launcher_scripts(self):
        """Crea script di avvio per il sistema"""
        print(f"\n{BLUE}🚀 Creazione script di avvio...{RESET}")
        
        if self.system == "windows":
            self.create_windows_launcher()
        else:
            self.create_unix_launcher()
    
    def create_windows_launcher(self):
        """Crea launcher per Windows"""
        # Script batch principale
        bat_content = f"""@echo off
cd /d "{self.install_path}"
python qkd_node_manager.py %*
pause
"""
        bat_path = self.install_path / "QKD_Mate.bat"
        with open(bat_path, "w") as f:
            f.write(bat_content)
        print(f"{GREEN}✅ Script Windows creato: QKD_Mate.bat{RESET}")
        
        # Script PowerShell
        ps1_content = f"""
Set-Location "{self.install_path}"
python qkd_node_manager.py $args
Read-Host "Premi INVIO per continuare"
"""
        ps1_path = self.install_path / "QKD_Mate.ps1"
        with open(ps1_path, "w") as f:
            f.write(ps1_content)
        print(f"{GREEN}✅ Script PowerShell creato: QKD_Mate.ps1{RESET}")
    
    def create_unix_launcher(self):
        """Crea launcher per Unix/Linux/macOS"""
        script_content = f"""#!/bin/bash
cd "{self.install_path}"
python3 qkd_node_manager.py "$@"
"""
        script_path = self.install_path / "qkd_mate"
        with open(script_path, "w") as f:
            f.write(script_content)
        script_path.chmod(0o755)
        print(f"{GREEN}✅ Script Unix creato: qkd_mate{RESET}")
        
        # Crea anche un .desktop file per Linux
        if self.system == "linux":
            self.create_linux_desktop_file()
    
    def create_linux_desktop_file(self):
        """Crea file .desktop per Linux"""
        desktop_content = f"""[Desktop Entry]
Name=QKD Mate
Comment=Quantum Key Distribution Client
Exec=python3 "{self.install_path}/qkd_node_manager.py"
Path={self.install_path}
Icon={self.install_path}/icon.png
Terminal=true
Type=Application
Categories=Network;Security;
"""
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_path = desktop_dir / "qkd-mate.desktop"
        with open(desktop_path, "w") as f:
            f.write(desktop_content)
        desktop_path.chmod(0o755)
        print(f"{GREEN}✅ File .desktop creato{RESET}")
    
    def create_desktop_shortcut(self):
        """Crea shortcut sul desktop"""
        print(f"\n{BLUE}🖥️  Creazione shortcut desktop...{RESET}")
        
        if self.system == "windows":
            self.create_windows_shortcut()
        elif self.system == "linux":
            self.create_linux_shortcut()
        elif self.system == "darwin":
            self.create_macos_shortcut()
    
    def create_windows_shortcut(self):
        """Crea shortcut Windows"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "QKD Mate.lnk")
            target = str(self.install_path / "QKD_Mate.bat")
            wDir = str(self.install_path)
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            shortcut.save()
            
            print(f"{GREEN}✅ Shortcut desktop creato{RESET}")
        except ImportError:
            print(f"{YELLOW}⚠️  Shortcut desktop non creato (moduli Windows mancanti){RESET}")
        except Exception as e:
            print(f"{YELLOW}⚠️  Shortcut desktop non creato: {e}{RESET}")
    
    def create_linux_shortcut(self):
        """Crea shortcut Linux"""
        desktop_path = Path.home() / "Desktop" / "QKD Mate.desktop"
        if Path.home().joinpath("Desktop").exists():
            try:
                shutil.copy2(
                    Path.home() / ".local" / "share" / "applications" / "qkd-mate.desktop",
                    desktop_path
                )
                desktop_path.chmod(0o755)
                print(f"{GREEN}✅ Shortcut desktop creato{RESET}")
            except:
                print(f"{YELLOW}⚠️  Shortcut desktop non creato{RESET}")
    
    def create_macos_shortcut(self):
        """Crea shortcut macOS"""
        # Per macOS, creiamo un alias o un'app bundle semplice
        print(f"{YELLOW}⚠️  Shortcut desktop automatico non supportato su macOS{RESET}")
        print(f"{CYAN}Puoi creare manualmente un alias a: {self.install_path}{RESET}")
    
    def uninstall(self):
        """Disinstalla l'applicazione"""
        print(f"\n{YELLOW}🗑️  Disinstallazione QKD_Mate...{RESET}")
        
        if not self.install_path.exists():
            print(f"{RED}❌ QKD_Mate non sembra essere installato{RESET}")
            return False
        
        # Conferma disinstallazione
        print(f"{YELLOW}Questo rimuoverà QKD_Mate da: {self.install_path}{RESET}")
        confirm = input(f"{YELLOW}Procedere? (s/n): {RESET}").lower()
        
        if confirm not in ['s', 'si', 'y', 'yes']:
            print(f"{CYAN}Disinstallazione annullata{RESET}")
            return False
        
        try:
            # Rimuovi directory principale
            shutil.rmtree(self.install_path)
            print(f"{GREEN}✅ Directory principale rimossa{RESET}")
            
            # Rimuovi shortcut desktop se esistenti
            self.remove_shortcuts()
            
            print(f"{GREEN}🎉 Disinstallazione completata{RESET}")
            return True
            
        except Exception as e:
            print(f"{RED}❌ Errore durante disinstallazione: {e}{RESET}")
            return False
    
    def remove_shortcuts(self):
        """Rimuove shortcut e file di sistema"""
        shortcuts_to_remove = []
        
        if self.system == "windows":
            shortcuts_to_remove.extend([
                Path.home() / "Desktop" / "QKD Mate.lnk",
                Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "QKD Mate.lnk"
            ])
        elif self.system == "linux":
            shortcuts_to_remove.extend([
                Path.home() / "Desktop" / "QKD Mate.desktop",
                Path.home() / ".local" / "share" / "applications" / "qkd-mate.desktop"
            ])
        
        for shortcut in shortcuts_to_remove:
            if shortcut.exists():
                try:
                    shortcut.unlink()
                    print(f"{GREEN}✅ Rimosso: {shortcut.name}{RESET}")
                except:
                    print(f"{YELLOW}⚠️  Impossibile rimuovere: {shortcut.name}{RESET}")
    
    def show_post_install_info(self):
        """Mostra informazioni post-installazione"""
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}{BOLD}🎉 INSTALLAZIONE COMPLETATA! 🎉{RESET}")
        print(f"{GREEN}{'='*70}{RESET}")
        
        print(f"\n{CYAN}📍 Percorso installazione:{RESET}")
        print(f"   {self.install_path}")
        
        print(f"\n{CYAN}🚀 Come avviare QKD_Mate:{RESET}")
        
        if self.system == "windows":
            print(f"   • Doppio click su: QKD Mate (shortcut desktop)")
            print(f"   • Oppure esegui: {self.install_path}\\QKD_Mate.bat")
        else:
            print(f"   • Esegui: {self.install_path}/qkd_mate")
            if self.system == "linux":
                print(f"   • Oppure cerca 'QKD Mate' nel menu applicazioni")
        
        print(f"\n{CYAN}📋 Prossimi passi:{RESET}")
        print(f"   1. Copia i certificati mTLS nella directory: {self.install_path}/certs/")
        print(f"   2. Avvia QKD_Mate per completare la configurazione")
        
        print(f"\n{CYAN}🔧 Strumenti utili:{RESET}")
        print(f"   • Gestione certificati: python cert_manager.py")
        print(f"   • Setup aggiuntivo: python setup.py")
        print(f"   • Disinstallazione: python install.py --uninstall")

def main():
    from datetime import datetime
    
    installer = UniversalInstaller()
    
    # Parsing argomenti
    silent_mode = "--silent" in sys.argv
    uninstall_mode = "--uninstall" in sys.argv
    
    if uninstall_mode:
        installer.uninstall()
        return
    
    installer.print_banner()
    
    if not installer.check_requirements():
        print(f"\n{RED}❌ Requisiti non soddisfatti. Installazione interrotta.{RESET}")
        return
    
    if installer.install_application(silent=silent_mode):
        installer.show_post_install_info()
    else:
        print(f"\n{RED}❌ Installazione fallita{RESET}")

if __name__ == "__main__":
    main()