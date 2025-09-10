#!/usr/bin/env python3
"""
Quantum Chat - Interfaccia CLI per messaggistica sicura con QKD
Sistema di chat sicuro che sostituisce RSA con Quantum Key Distribution
"""

import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# Aggiungi il path per importare i moduli
sys.path.insert(0, str(Path(__file__).parent))

from src.quantum_messenger import QuantumMessenger, print_conversation_history, format_message_display
from src.utils import QKDClientError

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'


class QuantumChatCLI:
    """Interfaccia CLI per Quantum Chat"""
    
    def __init__(self, node_type: str, username: str = None):
        self.node_type = node_type.lower()
        self.username = username or f"user_{self.node_type}"
        self.partner = "bob" if self.node_type == "alice" else "alice"
        
        try:
            self.messenger = QuantumMessenger(self.node_type, self.username)
            self.messenger.on_message_received = self.on_message_received
            
            # Avvia ricezione automatica
            self.messenger.start_receiving(interval=3)
            
            self.running = True
            self.new_message_flag = False
            
        except Exception as e:
            print(f"{RED}❌ Errore inizializzazione: {e}{RESET}")
            sys.exit(1)
    
    def on_message_received(self, message):
        """Callback per messaggi ricevuti"""
        self.new_message_flag = True
        print(f"\n{CYAN}📥 NUOVO MESSAGGIO:{RESET}")
        print(f"   {format_message_display(message)}")
        print(f"{YELLOW}Premi INVIO per continuare...{RESET}", end='', flush=True)
    
    def print_header(self):
        """Stampa header dell'applicazione"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}🔮 {BOLD}QUANTUM CHAT{RESET} {BLUE}- Messaggistica Sicura con QKD{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"{GREEN}👤 Utente: {self.username} ({self.node_type.upper()}){RESET}")
        print(f"{GREEN}🤝 Partner: {self.partner.upper()}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
    
    def print_menu(self):
        """Stampa menu principale"""
        stats = self.messenger.get_stats()
        key_stats = stats["crypto"]["key_management"]
        
        print(f"\n{CYAN}📋 MENU PRINCIPALE{RESET}")
        print(f"{CYAN}{'─'*40}{RESET}")
        print(f"{GREEN}1.{RESET} 💬 Invia messaggio")
        print(f"{GREEN}2.{RESET} 📜 Visualizza cronologia")
        print(f"{GREEN}3.{RESET} 🔍 Cerca messaggi")
        print(f"{GREEN}4.{RESET} 🆕 Nuova sessione sicura")
        print(f"{GREEN}5.{RESET} 🔄 Cambia sessione")
        print(f"{GREEN}6.{RESET} 📊 Statistiche sistema")
        print(f"{GREEN}7.{RESET} 🔑 Gestione chiavi")
        print(f"{GREEN}8.{RESET} ⚙️  Impostazioni")
        print(f"{GREEN}9.{RESET} 🚪 Esci")
        print(f"{CYAN}{'─'*40}{RESET}")
        
        # Status bar
        available_keys = key_stats["available_keys"]
        current_session = self.messenger.current_session_id or "Nessuna"
        
        if available_keys < 5:
            key_color = RED
        elif available_keys < 10:
            key_color = YELLOW
        else:
            key_color = GREEN
        
        print(f"{BLUE}Status:{RESET} Chiavi: {key_color}{available_keys}{RESET} | Sessione: {CYAN}{current_session[:12]}{RESET}")
        
        if self.new_message_flag:
            print(f"{YELLOW}💡 Hai nuovi messaggi!{RESET}")
            self.new_message_flag = False
    
    def send_message_interactive(self):
        """Interfaccia interattiva per invio messaggi"""
        print(f"\n{MAGENTA}✍️  INVIO MESSAGGIO{RESET}")
        print(f"{MAGENTA}{'─'*30}{RESET}")
        
        # Scegli modalità
        print(f"\n{YELLOW}Modalità crittografia:{RESET}")
        print(f"1. 🔐 Sessione sicura (raccomandato per chat lunghe)")
        print(f"2. 🔑 Chiave QKD diretta (massima sicurezza, una chiave per messaggio)")
        
        mode = input(f"\n{CYAN}Scegli modalità (1-2): {RESET}").strip()
        use_session = mode != "2"
        
        if use_session and not self.messenger.current_session_id:
            print(f"\n{YELLOW}⚠️  Nessuna sessione attiva. Creando nuova sessione...{RESET}")
            session_id = self.messenger.start_session()
            if not session_id:
                print(f"{RED}❌ Impossibile creare sessione{RESET}")
                return
        
        print(f"\n{CYAN}Destinatario: {self.partner.upper()}{RESET}")
        print(f"{YELLOW}Scrivi il messaggio (INVIO per inviare, 'cancel' per annullare):{RESET}")
        
        message = input(f"{GREEN}> {RESET}").strip()
        
        if message.lower() == 'cancel':
            print(f"{YELLOW}Invio annullato{RESET}")
            return
        
        if not message:
            print(f"{RED}❌ Messaggio vuoto{RESET}")
            return
        
        print(f"\n{BLUE}🔄 Crittografia e invio in corso...{RESET}")
        
        success = self.messenger.send_message(message, use_session=use_session)
        
        if success:
            mode_str = "sessione sicura" if use_session else "chiave QKD diretta"
            print(f"{GREEN}✅ Messaggio inviato con {mode_str}{RESET}")
        else:
            print(f"{RED}❌ Errore invio messaggio{RESET}")
    
    def show_conversation_history(self):
        """Mostra cronologia conversazione"""
        print(f"\n{MAGENTA}📜 CRONOLOGIA CONVERSAZIONE{RESET}")
        
        limit = input(f"{CYAN}Numero messaggi da mostrare (default 20): {RESET}").strip()
        limit = int(limit) if limit.isdigit() else 20
        
        messages = self.messenger.get_conversation_history(limit)
        
        if not messages:
            print(f"{YELLOW}📭 Nessun messaggio nella cronologia{RESET}")
            return
        
        print_conversation_history(messages, limit)
        
        print(f"\n{GREEN}Totale messaggi mostrati: {len(messages)}{RESET}")
    
    def search_messages(self):
        """Cerca nei messaggi"""
        print(f"\n{MAGENTA}🔍 RICERCA MESSAGGI{RESET}")
        print(f"{MAGENTA}{'─'*25}{RESET}")
        
        query = input(f"{CYAN}Termine da cercare: {RESET}").strip()
        
        if not query:
            print(f"{RED}❌ Query vuota{RESET}")
            return
        
        print(f"\n{BLUE}🔄 Ricerca in corso...{RESET}")
        
        results = self.messenger.search_messages(query)
        
        if not results:
            print(f"{YELLOW}📭 Nessun risultato per '{query}'{RESET}")
            return
        
        print(f"\n{GREEN}🎯 Trovati {len(results)} risultati per '{query}':{RESET}")
        print(f"{GREEN}{'─'*50}{RESET}")
        
        for message in results:
            print(format_message_display(message))
        
        print(f"{GREEN}{'─'*50}{RESET}")
    
    def manage_sessions(self):
        """Gestione sessioni sicure"""
        print(f"\n{MAGENTA}🆕 GESTIONE SESSIONI{RESET}")
        print(f"{MAGENTA}{'─'*30}{RESET}")
        
        active_sessions = list(self.messenger.active_sessions.keys())
        current = self.messenger.current_session_id
        
        if active_sessions:
            print(f"\n{GREEN}📋 Sessioni attive:{RESET}")
            for i, session_id in enumerate(active_sessions, 1):
                marker = " 👈 CORRENTE" if session_id == current else ""
                print(f"  {i}. {session_id[:20]}...{marker}")
        else:
            print(f"{YELLOW}📭 Nessuna sessione attiva{RESET}")
        
        print(f"\n{CYAN}Opzioni:{RESET}")
        print(f"1. Crea nuova sessione")
        print(f"2. Cambia sessione attiva")
        print(f"3. Torna al menu")
        
        choice = input(f"\n{CYAN}Scegli opzione: {RESET}").strip()
        
        if choice == "1":
            name = input(f"{CYAN}Nome sessione (opzionale): {RESET}").strip()
            session_id = self.messenger.start_session(name if name else None)
            if session_id:
                print(f"{GREEN}✅ Sessione '{session_id}' creata e attivata{RESET}")
            else:
                print(f"{RED}❌ Errore creazione sessione{RESET}")
        
        elif choice == "2":
            if not active_sessions:
                print(f"{YELLOW}⚠️  Nessuna sessione disponibile{RESET}")
                return
            
            try:
                idx = int(input(f"{CYAN}Numero sessione (1-{len(active_sessions)}): {RESET}")) - 1
                if 0 <= idx < len(active_sessions):
                    session_id = active_sessions[idx]
                    if self.messenger.switch_session(session_id):
                        print(f"{GREEN}✅ Cambiato alla sessione '{session_id}'{RESET}")
                    else:
                        print(f"{RED}❌ Errore cambio sessione{RESET}")
                else:
                    print(f"{RED}❌ Numero non valido{RESET}")
            except ValueError:
                print(f"{RED}❌ Input non valido{RESET}")
    
    def show_stats(self):
        """Mostra statistiche sistema"""
        print(f"\n{MAGENTA}📊 STATISTICHE SISTEMA{RESET}")
        print(f"{MAGENTA}{'='*50}{RESET}")
        
        stats = self.messenger.get_stats()
        
        # Stats messenger
        msg_stats = stats["messages"]
        print(f"\n{CYAN}💬 Messaggistica:{RESET}")
        print(f"  📤 Messaggi inviati: {msg_stats['sent']}")
        print(f"  📥 Messaggi ricevuti: {msg_stats['received']}")
        print(f"  📊 Totale: {msg_stats['total']}")
        print(f"  🔒 Crittati: {msg_stats['encrypted']} ({msg_stats['encryption_rate']})")
        
        # Stats chiavi
        key_stats = stats["crypto"]["key_management"]
        print(f"\n{CYAN}🔑 Gestione Chiavi:{RESET}")
        print(f"  💎 Chiavi disponibili: {key_stats['available_keys']}")
        print(f"  ✅ Chiavi usate: {key_stats['used_keys']}")
        print(f"  ⚖️  Soglia minima: {key_stats['min_threshold']}")
        print(f"  📦 Capacità massima: {key_stats['max_capacity']}")
        
        if key_stats['oldest_key_age']:
            print(f"  ⏰ Età chiave più vecchia: {key_stats['oldest_key_age']}")
        
        # Stats crittografia
        crypto_info = stats["crypto"]["crypto_engine"]
        print(f"\n{CYAN}🔐 Crittografia:{RESET}")
        print(f"  🧮 Algoritmo: {crypto_info['encryption_algorithm']}")
        print(f"  🔑 Derivazione chiavi: {crypto_info['key_derivation']}")
        print(f"  ✍️  Autenticazione: {crypto_info['authentication']}")
        print(f"  🛡️  Perfect Forward Secrecy: {'✅' if crypto_info['perfect_forward_secrecy'] else '❌'}")
        
        # Sessioni
        messenger_stats = stats["messenger"]
        print(f"\n{CYAN}🔗 Sessioni:{RESET}")
        print(f"  📋 Sessioni attive: {messenger_stats['active_sessions']}")
        print(f"  👈 Sessione corrente: {messenger_stats['current_session'] or 'Nessuna'}")
    
    def manage_keys(self):
        """Gestione chiavi quantistiche"""
        print(f"\n{MAGENTA}🔑 GESTIONE CHIAVI QUANTISTICHE{RESET}")
        print(f"{MAGENTA}{'='*45}{RESET}")
        
        key_stats = self.messenger.key_manager.get_pool_status()
        
        print(f"\n{CYAN}Status Pool Chiavi:{RESET}")
        print(f"  💎 Disponibili: {key_stats['available_keys']}")
        print(f"  ✅ Usate: {key_stats['used_keys']}")
        print(f"  ⚖️  Min/Max: {key_stats['min_threshold']}/{key_stats['max_capacity']}")
        
        print(f"\n{CYAN}Operazioni:{RESET}")
        print(f"1. 🔄 Ricarica pool chiavi")
        print(f"2. 🧹 Pulizia chiavi vecchie")
        print(f"3. 💾 Salva stato")
        print(f"4. 📊 Status dettagliato")
        print(f"5. 🔙 Torna al menu")
        
        choice = input(f"\n{CYAN}Scegli operazione: {RESET}").strip()
        
        if choice == "1":
            count = input(f"{CYAN}Numero chiavi da richiedere (default: riempimento automatico): {RESET}").strip()
            if count.isdigit():
                added = self.messenger.key_manager.force_key_refresh(int(count))
            else:
                added = self.messenger.key_manager.refill_key_pool()
            
            print(f"{GREEN}✅ Aggiunte {added} nuove chiavi{RESET}")
        
        elif choice == "2":
            self.messenger.key_manager.cleanup_old_keys()
            print(f"{GREEN}✅ Pulizia completata{RESET}")
        
        elif choice == "3":
            self.messenger.key_manager.save_keys_to_storage()
            print(f"{GREEN}✅ Stato salvato{RESET}")
        
        elif choice == "4":
            import json
            print(f"\n{BLUE}📋 Status dettagliato:{RESET}")
            print(json.dumps(key_stats, indent=2))
    
    def settings_menu(self):
        """Menu impostazioni"""
        print(f"\n{MAGENTA}⚙️  IMPOSTAZIONI{RESET}")
        print(f"{MAGENTA}{'─'*20}{RESET}")
        
        print(f"\n{CYAN}Configurazione corrente:{RESET}")
        print(f"  👤 Username: {self.username}")
        print(f"  🏷️  Nodo: {self.node_type.upper()}")
        print(f"  🤝 Partner: {self.partner.upper()}")
        
        print(f"\n{CYAN}Opzioni:{RESET}")
        print(f"1. 📁 Percorso file messaggi")
        print(f"2. 🔄 Intervallo controllo messaggi")
        print(f"3. 🧹 Pulisci cronologia")
        print(f"4. 🔙 Torna al menu")
        
        choice = input(f"\n{CYAN}Scegli opzione: {RESET}").strip()
        
        if choice == "1":
            print(f"{BLUE}📁 File messaggi: {self.messenger.storage_file}{RESET}")
        
        elif choice == "2":
            print(f"{BLUE}🔄 Intervallo corrente: 3 secondi{RESET}")
            print(f"{YELLOW}⚠️  Modifica non implementata in questa versione{RESET}")
        
        elif choice == "3":
            confirm = input(f"{RED}⚠️  Eliminare TUTTA la cronologia? (yes/no): {RESET}").strip().lower()
            if confirm == "yes":
                self.messenger.messages.clear()
                self.messenger.save_messages()
                print(f"{GREEN}✅ Cronologia eliminata{RESET}")
            else:
                print(f"{YELLOW}Operazione annullata{RESET}")
    
    def run(self):
        """Avvia l'interfaccia CLI"""
        try:
            self.print_header()
            
            while self.running:
                self.print_menu()
                
                choice = input(f"\n{CYAN}Scegli opzione (1-9): {RESET}").strip()
                
                if choice == "1":
                    self.send_message_interactive()
                
                elif choice == "2":
                    self.show_conversation_history()
                
                elif choice == "3":
                    self.search_messages()
                
                elif choice == "4":
                    name = input(f"{CYAN}Nome sessione (opzionale): {RESET}").strip()
                    session_id = self.messenger.start_session(name if name else None)
                    if session_id:
                        print(f"{GREEN}✅ Nuova sessione '{session_id}' creata{RESET}")
                
                elif choice == "5":
                    self.manage_sessions()
                
                elif choice == "6":
                    self.show_stats()
                
                elif choice == "7":
                    self.manage_keys()
                
                elif choice == "8":
                    self.settings_menu()
                
                elif choice == "9":
                    self.running = False
                    print(f"\n{YELLOW}👋 Chiusura Quantum Chat...{RESET}")
                
                else:
                    print(f"{RED}❌ Opzione non valida{RESET}")
                
                if self.running and choice != "9":
                    input(f"\n{YELLOW}Premi INVIO per continuare...{RESET}")
        
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}👋 Uscita con Ctrl+C{RESET}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Pulizia risorse"""
        print(f"{BLUE}🧹 Pulizia in corso...{RESET}")
        self.messenger.cleanup()
        print(f"{GREEN}✅ Quantum Chat chiuso correttamente{RESET}")


def main():
    """Funzione principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum Chat - Messaggistica sicura con QKD")
    parser.add_argument("--node", choices=["alice", "bob"], required=True,
                       help="Tipo di nodo (alice o bob)")
    parser.add_argument("--username", type=str,
                       help="Nome utente (opzionale)")
    
    args = parser.parse_args()
    
    # Verifica dipendenze crittografiche
    try:
        import cryptography
        print(f"{GREEN}✅ Libreria cryptography trovata{RESET}")
    except ImportError:
        print(f"{RED}❌ Libreria cryptography mancante{RESET}")
        print(f"{YELLOW}Installa con: pip install cryptography{RESET}")
        sys.exit(1)
    
    # Avvia chat
    try:
        chat = QuantumChatCLI(args.node, args.username)
        chat.run()
    except Exception as e:
        print(f"{RED}❌ Errore fatale: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()