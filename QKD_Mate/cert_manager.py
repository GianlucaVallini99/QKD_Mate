#!/usr/bin/env python3
"""
QKD Certificate Manager - Gestione Semplificata Certificati
=========================================================

Script per semplificare la gestione dei certificati mTLS per QKD_Mate.
Fornisce funzionalità per:
- Installazione guidata dei certificati
- Validazione automatica
- Riparazione permessi
- Backup e ripristino

Uso:
    python cert_manager.py install    # Installazione guidata
    python cert_manager.py validate   # Validazione certificati
    python cert_manager.py fix        # Riparazione automatica
    python cert_manager.py backup     # Backup certificati
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import platform

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class CertificateManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.certs_dir = self.project_root / "certs"
        self.backup_dir = self.project_root / "cert_backups"
        
        # Certificati richiesti per ogni nodo
        self.cert_templates = {
            "common": ["ca.crt"],
            "alice": ["client_Alice2.crt", "client_Alice2.key"],
            "bob": ["client_Bob2.crt", "client_Bob2.key"]
        }
    
    def print_header(self, title):
        """Stampa header colorato"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{BOLD}🔐 {title} 🔐{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
    
    def ensure_certs_directory(self):
        """Assicura che la directory certificati esista"""
        if not self.certs_dir.exists():
            self.certs_dir.mkdir(mode=0o700)
            print(f"{GREEN}✅ Directory certs/ creata{RESET}")
        return True
    
    def detect_available_certificates(self, source_dir):
        """Rileva i certificati disponibili in una directory"""
        if not Path(source_dir).exists():
            return []
        
        found_certs = []
        for cert_file in Path(source_dir).iterdir():
            if cert_file.is_file() and cert_file.suffix in ['.crt', '.key', '.pem']:
                found_certs.append(cert_file.name)
        
        return sorted(found_certs)
    
    def interactive_certificate_install(self):
        """Installazione interattiva dei certificati"""
        self.print_header("INSTALLAZIONE CERTIFICATI")
        
        print(f"{CYAN}Questo wizard ti aiuterà a installare i certificati necessari.{RESET}\n")
        
        # Chiedi la directory sorgente
        while True:
            source_path = input(f"{YELLOW}Inserisci il percorso della cartella contenente i certificati: {RESET}").strip()
            
            if not source_path:
                print(f"{RED}❌ Percorso non può essere vuoto{RESET}")
                continue
            
            source_dir = Path(source_path).expanduser()
            if not source_dir.exists():
                print(f"{RED}❌ Directory non trovata: {source_dir}{RESET}")
                continue
            
            # Rileva certificati disponibili
            available_certs = self.detect_available_certificates(source_dir)
            if not available_certs:
                print(f"{RED}❌ Nessun certificato trovato in: {source_dir}{RESET}")
                print(f"{CYAN}Assicurati che la directory contenga file .crt, .key o .pem{RESET}")
                continue
            
            break
        
        print(f"\n{GREEN}✅ Certificati trovati:{RESET}")
        for cert in available_certs:
            print(f"  - {cert}")
        
        # Chiedi conferma per la copia
        print(f"\n{YELLOW}Procedere con la copia dei certificati? (s/n): {RESET}", end="")
        if input().lower() not in ['s', 'si', 'y', 'yes']:
            print(f"{YELLOW}⚠️  Installazione annullata{RESET}")
            return False
        
        # Copia i certificati
        self.ensure_certs_directory()
        copied_count = 0
        
        for cert_file in available_certs:
            source_file = source_dir / cert_file
            dest_file = self.certs_dir / cert_file
            
            try:
                shutil.copy2(source_file, dest_file)
                
                # Imposta permessi corretti per le chiavi private
                if cert_file.endswith('.key'):
                    dest_file.chmod(0o600)
                    print(f"{GREEN}✅ {cert_file} (permessi sicuri){RESET}")
                else:
                    print(f"{GREEN}✅ {cert_file}{RESET}")
                
                copied_count += 1
                
            except Exception as e:
                print(f"{RED}❌ Errore copiando {cert_file}: {e}{RESET}")
        
        print(f"\n{GREEN}🎉 {copied_count} certificati installati con successo!{RESET}")
        
        # Valida i certificati installati
        self.validate_certificates()
        return True
    
    def validate_certificates(self):
        """Valida i certificati installati"""
        self.print_header("VALIDAZIONE CERTIFICATI")
        
        if not self.certs_dir.exists():
            print(f"{RED}❌ Directory certs/ non trovata{RESET}")
            return False
        
        # Leggi configurazione nodo se disponibile
        node_type = self.detect_node_type()
        
        # Determina certificati richiesti
        required_certs = self.cert_templates["common"].copy()
        
        if node_type == "alice":
            required_certs.extend(self.cert_templates["alice"])
            print(f"{CYAN}📋 Nodo configurato come: Alice (Master){RESET}")
        elif node_type == "bob":
            required_certs.extend(self.cert_templates["bob"])
            print(f"{CYAN}📋 Nodo configurato come: Bob (Slave){RESET}")
        else:
            # Se non configurato, controlla per entrambi
            required_certs.extend(self.cert_templates["alice"])
            required_certs.extend(self.cert_templates["bob"])
            print(f"{CYAN}📋 Nodo non configurato - controllo tutti i certificati{RESET}")
        
        print(f"\n{BLUE}🔍 Controllo certificati richiesti...{RESET}")
        
        validation_results = []
        for cert in required_certs:
            cert_path = self.certs_dir / cert
            status = self.validate_single_certificate(cert_path)
            validation_results.append((cert, status))
        
        # Riassunto validazione
        valid_count = sum(1 for _, status in validation_results if status['valid'])
        total_count = len(validation_results)
        
        print(f"\n{BLUE}📊 Riassunto validazione:{RESET}")
        print(f"  Certificati validi: {valid_count}/{total_count}")
        
        if valid_count == total_count:
            print(f"{GREEN}🎉 Tutti i certificati sono validi!{RESET}")
            return True
        else:
            print(f"{YELLOW}⚠️  Alcuni certificati richiedono attenzione{RESET}")
            return False
    
    def validate_single_certificate(self, cert_path):
        """Valida un singolo certificato"""
        cert_name = cert_path.name
        result = {
            'valid': False,
            'exists': False,
            'permissions_ok': True,
            'readable': False,
            'size_ok': False
        }
        
        # Controllo esistenza
        if not cert_path.exists():
            print(f"{RED}❌ {cert_name} - Non trovato{RESET}")
            return result
        
        result['exists'] = True
        
        # Controllo dimensione
        try:
            size = cert_path.stat().st_size
            if size > 0:
                result['size_ok'] = True
            else:
                print(f"{RED}❌ {cert_name} - File vuoto{RESET}")
                return result
        except Exception:
            print(f"{RED}❌ {cert_name} - Errore lettura dimensione{RESET}")
            return result
        
        # Controllo permessi per chiavi private
        if cert_name.endswith('.key'):
            try:
                stat_info = cert_path.stat()
                if stat_info.st_mode & 0o077:
                    print(f"{YELLOW}⚠️  {cert_name} - Permessi troppo aperti (riparabili){RESET}")
                    result['permissions_ok'] = False
                else:
                    result['permissions_ok'] = True
            except Exception:
                print(f"{RED}❌ {cert_name} - Errore controllo permessi{RESET}")
                return result
        
        # Controllo leggibilità
        try:
            with open(cert_path, 'r') as f:
                content = f.read(100)  # Leggi primi 100 caratteri
                if content.strip():
                    result['readable'] = True
                else:
                    print(f"{RED}❌ {cert_name} - File non leggibile o vuoto{RESET}")
                    return result
        except Exception:
            print(f"{RED}❌ {cert_name} - Errore lettura file{RESET}")
            return result
        
        # Se tutto OK
        if result['exists'] and result['size_ok'] and result['readable']:
            if result['permissions_ok']:
                print(f"{GREEN}✅ {cert_name} - Valido{RESET}")
                result['valid'] = True
            else:
                print(f"{YELLOW}⚠️  {cert_name} - Valido ma permessi da correggere{RESET}")
        
        return result
    
    def fix_certificates(self):
        """Ripara automaticamente i problemi dei certificati"""
        self.print_header("RIPARAZIONE CERTIFICATI")
        
        if not self.certs_dir.exists():
            print(f"{RED}❌ Directory certs/ non trovata{RESET}")
            return False
        
        print(f"{BLUE}🔧 Riparazione automatica in corso...{RESET}")
        
        fixed_count = 0
        for cert_file in self.certs_dir.iterdir():
            if cert_file.is_file() and cert_file.name.endswith('.key'):
                try:
                    stat_info = cert_file.stat()
                    if stat_info.st_mode & 0o077:
                        cert_file.chmod(0o600)
                        print(f"{GREEN}✅ Permessi corretti per {cert_file.name}{RESET}")
                        fixed_count += 1
                except Exception as e:
                    print(f"{RED}❌ Errore riparando {cert_file.name}: {e}{RESET}")
        
        if fixed_count > 0:
            print(f"\n{GREEN}🎉 {fixed_count} certificati riparati!{RESET}")
        else:
            print(f"\n{CYAN}ℹ️  Nessuna riparazione necessaria{RESET}")
        
        return True
    
    def backup_certificates(self):
        """Crea backup dei certificati"""
        self.print_header("BACKUP CERTIFICATI")
        
        if not self.certs_dir.exists() or not any(self.certs_dir.iterdir()):
            print(f"{RED}❌ Nessun certificato da fare backup{RESET}")
            return False
        
        # Crea directory backup se non existe
        self.backup_dir.mkdir(exist_ok=True)
        
        # Nome backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"certs_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for cert_file in self.certs_dir.iterdir():
                    if cert_file.is_file():
                        zipf.write(cert_file, cert_file.name)
                        print(f"{GREEN}✅ Aggiunto al backup: {cert_file.name}{RESET}")
            
            print(f"\n{GREEN}🎉 Backup creato: {backup_path}{RESET}")
            print(f"{CYAN}Dimensione: {backup_path.stat().st_size} bytes{RESET}")
            return True
            
        except Exception as e:
            print(f"{RED}❌ Errore creando backup: {e}{RESET}")
            return False
    
    def detect_node_type(self):
        """Rileva il tipo di nodo dalla configurazione"""
        config_path = self.project_root / "node_config.yaml"
        if not config_path.exists():
            return None
        
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config.get('node_type')
        except:
            return None
    
    def list_certificates(self):
        """Lista i certificati installati"""
        self.print_header("CERTIFICATI INSTALLATI")
        
        if not self.certs_dir.exists():
            print(f"{RED}❌ Directory certs/ non trovata{RESET}")
            return
        
        cert_files = list(self.certs_dir.glob('*'))
        if not cert_files:
            print(f"{YELLOW}⚠️  Nessun certificato installato{RESET}")
            return
        
        print(f"{CYAN}📋 Certificati trovati in certs/:{RESET}\n")
        
        for cert_file in sorted(cert_files):
            if cert_file.is_file():
                size = cert_file.stat().st_size
                modified = datetime.fromtimestamp(cert_file.stat().st_mtime)
                
                # Icona basata sul tipo
                if cert_file.name.endswith('.key'):
                    icon = "🔑"
                elif cert_file.name.endswith('.crt'):
                    icon = "📜"
                else:
                    icon = "📄"
                
                print(f"  {icon} {cert_file.name}")
                print(f"    Dimensione: {size} bytes")
                print(f"    Modificato: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
                print()

def main():
    cert_manager = CertificateManager()
    
    if len(sys.argv) < 2:
        print(f"{YELLOW}Uso: python cert_manager.py <comando>{RESET}")
        print(f"\nComandi disponibili:")
        print(f"  install   - Installazione guidata certificati")
        print(f"  validate  - Validazione certificati esistenti")
        print(f"  fix       - Riparazione automatica problemi")
        print(f"  backup    - Backup certificati")
        print(f"  list      - Lista certificati installati")
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        cert_manager.interactive_certificate_install()
    elif command == "validate":
        cert_manager.validate_certificates()
    elif command == "fix":
        cert_manager.fix_certificates()
    elif command == "backup":
        cert_manager.backup_certificates()
    elif command == "list":
        cert_manager.list_certificates()
    else:
        print(f"{RED}❌ Comando non riconosciuto: {command}{RESET}")
        print(f"{YELLOW}Comandi validi: install, validate, fix, backup, list{RESET}")

if __name__ == "__main__":
    main()