"""
Quantum Messenger - Client di messaggistica sicura con QKD
Sistema di messaggistica stile Telegram che usa chiavi quantistiche invece di RSA
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import uuid

from .qkd_key_manager import QKDKeyManager
from .qkd_crypto import QKDCryptoEngine, QKDSecureSession


class Message:
    """Rappresenta un messaggio nella chat"""
    
    def __init__(self, content: str, sender: str, recipient: str, 
                 timestamp: float = None, message_id: str = None):
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp or time.time()
        self.message_id = message_id or str(uuid.uuid4())
        self.encrypted = False
        self.session_id = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "content": self.content,
            "sender": self.sender,
            "recipient": self.recipient,
            "timestamp": self.timestamp,
            "encrypted": self.encrypted,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        msg = cls(
            content=data["content"],
            sender=data["sender"],
            recipient=data["recipient"],
            timestamp=data["timestamp"],
            message_id=data["message_id"]
        )
        msg.encrypted = data.get("encrypted", False)
        msg.session_id = data.get("session_id")
        return msg


class QuantumMessenger:
    """
    Client di messaggistica quantistica sicura.
    
    Caratteristiche:
    - Crittografia end-to-end con chiavi quantistiche
    - Perfect Forward Secrecy
    - Sessioni sicure per chat lunghe
    - Interfaccia simile a Telegram
    - Storage locale crittato
    """
    
    def __init__(self, node_type: str, username: str = None):
        self.node_type = node_type.lower()
        self.username = username or f"user_{self.node_type}"
        self.partner_node = "bob" if self.node_type == "alice" else "alice"
        
        # Inizializza componenti QKD
        self.key_manager = QKDKeyManager(self.node_type, min_keys=20, max_keys=100)
        self.crypto_engine = QKDCryptoEngine(self.key_manager)
        
        # Storage messaggi
        self.messages: List[Message] = []
        self.storage_file = Path(f"messages_{self.node_type}.json")
        
        # Sessioni attive
        self.active_sessions: Dict[str, QKDSecureSession] = {}
        self.current_session_id = None
        
        # Callbacks per eventi
        self.on_message_received: Optional[Callable[[Message], None]] = None
        self.on_connection_status: Optional[Callable[[bool], None]] = None
        
        # Thread per ricezione messaggi (simulato - in produzione sarebbe socket/websocket)
        self.receiving = False
        self.receive_thread = None
        
        self.load_messages()
        print(f"💬 Quantum Messenger inizializzato per {self.username} ({self.node_type.upper()})")
        print(f"   Partner: {self.partner_node.upper()}")
        
        # Avvia manutenzione chiavi
        self.key_manager.start_maintenance(interval=30)
    
    def start_session(self, session_name: str = None) -> str:
        """Avvia una nuova sessione sicura"""
        session_id = session_name or f"session_{int(time.time())}"
        
        if session_id in self.active_sessions:
            print(f"⚠️ Sessione {session_id} già attiva")
            return session_id
        
        session = QKDSecureSession(self.crypto_engine, session_id)
        if session.initialize_session():
            self.active_sessions[session_id] = session
            self.current_session_id = session_id
            print(f"🆕 Sessione sicura '{session_id}' avviata")
            return session_id
        else:
            print(f"❌ Impossibile avviare sessione {session_id}")
            return None
    
    def switch_session(self, session_id: str) -> bool:
        """Cambia sessione attiva"""
        if session_id not in self.active_sessions:
            print(f"❌ Sessione {session_id} non trovata")
            return False
        
        self.current_session_id = session_id
        print(f"🔄 Passato alla sessione '{session_id}'")
        return True
    
    def send_message(self, content: str, use_session: bool = True) -> bool:
        """
        Invia un messaggio crittato con QKD
        
        Args:
            content: Contenuto del messaggio
            use_session: Se True usa sessione sicura, altrimenti chiave QKD diretta
        """
        if not content.strip():
            print("❌ Messaggio vuoto")
            return False
        
        try:
            message = Message(
                content=content,
                sender=self.node_type,
                recipient=self.partner_node
            )
            
            if use_session and self.current_session_id:
                # Usa sessione sicura
                session = self.active_sessions[self.current_session_id]
                encrypted_package = session.encrypt_message(content)
                
                if encrypted_package:
                    message.encrypted = True
                    message.session_id = self.current_session_id
                    
                    # In produzione: invia via rete
                    success = self._transmit_message(encrypted_package, "session")
                    
                    if success:
                        self.messages.append(message)
                        self.save_messages()
                        print(f"📤 Messaggio inviato via sessione '{self.current_session_id}'")
                        return True
                
            else:
                # Usa chiave QKD diretta
                encrypted_package = self.crypto_engine.encrypt_message(content, self.partner_node)
                
                if encrypted_package:
                    message.encrypted = True
                    
                    # In produzione: invia via rete
                    success = self._transmit_message(encrypted_package, "direct")
                    
                    if success:
                        self.messages.append(message)
                        self.save_messages()
                        print(f"📤 Messaggio inviato con crittografia QKD diretta")
                        return True
            
            print("❌ Impossibile crittare il messaggio")
            return False
            
        except Exception as e:
            print(f"❌ Errore invio messaggio: {e}")
            return False
    
    def _transmit_message(self, encrypted_package: Dict[str, Any], method: str) -> bool:
        """
        Simula la trasmissione del messaggio (in produzione sarebbe via rete)
        
        Args:
            encrypted_package: Pacchetto crittato
            method: "session" o "direct"
        """
        # Simula trasmissione salvando in file temporaneo
        # In produzione questo sarebbe sostituito da invio via WebSocket/HTTP
        
        try:
            outbox_file = Path(f"outbox_{self.node_type}_to_{self.partner_node}.json")
            
            outbox_data = {
                "method": method,
                "timestamp": time.time(),
                "from": self.node_type,
                "to": self.partner_node,
                "encrypted_package": encrypted_package
            }
            
            # Append al file outbox
            outbox = []
            if outbox_file.exists():
                with open(outbox_file, 'r') as f:
                    outbox = json.load(f)
            
            outbox.append(outbox_data)
            
            with open(outbox_file, 'w') as f:
                json.dump(outbox, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Errore trasmissione: {e}")
            return False
    
    def check_messages(self) -> List[Message]:
        """Controlla messaggi in arrivo (simula ricezione)"""
        try:
            inbox_file = Path(f"outbox_{self.partner_node}_to_{self.node_type}.json")
            
            if not inbox_file.exists():
                return []
            
            with open(inbox_file, 'r') as f:
                inbox = json.load(f)
            
            new_messages = []
            
            for msg_data in inbox:
                try:
                    encrypted_package = msg_data["encrypted_package"]
                    method = msg_data["method"]
                    
                    if method == "session":
                        # Messaggio di sessione
                        session_id = encrypted_package["session_id"]
                        
                        if session_id not in self.active_sessions:
                            # Crea sessione se non esiste
                            self.start_session(session_id)
                        
                        if session_id in self.active_sessions:
                            session = self.active_sessions[session_id]
                            content = session.decrypt_message(encrypted_package)
                            
                            if content:
                                message = Message(
                                    content=content,
                                    sender=self.partner_node,
                                    recipient=self.node_type,
                                    timestamp=msg_data["timestamp"]
                                )
                                message.encrypted = True
                                message.session_id = session_id
                                new_messages.append(message)
                    
                    elif method == "direct":
                        # Messaggio QKD diretto
                        content = self.crypto_engine.decrypt_message(encrypted_package)
                        
                        if content:
                            message = Message(
                                content=content,
                                sender=self.partner_node,
                                recipient=self.node_type,
                                timestamp=msg_data["timestamp"]
                            )
                            message.encrypted = True
                            new_messages.append(message)
                
                except Exception as e:
                    print(f"⚠️ Errore decrittografia messaggio: {e}")
                    continue
            
            # Pulisci inbox dopo aver letto
            if new_messages:
                inbox_file.unlink()
            
            # Aggiungi ai messaggi e salva
            for msg in new_messages:
                self.messages.append(msg)
                if self.on_message_received:
                    self.on_message_received(msg)
            
            if new_messages:
                self.save_messages()
                print(f"📥 Ricevuti {len(new_messages)} nuovi messaggi")
            
            return new_messages
            
        except Exception as e:
            print(f"❌ Errore controllo messaggi: {e}")
            return []
    
    def start_receiving(self, interval: int = 5):
        """Avvia il controllo automatico dei messaggi"""
        if self.receiving:
            return
        
        self.receiving = True
        self.receive_thread = threading.Thread(
            target=self._receive_loop,
            args=(interval,),
            daemon=True
        )
        self.receive_thread.start()
        print(f"📡 Ricezione automatica avviata (intervallo: {interval}s)")
    
    def stop_receiving(self):
        """Ferma il controllo automatico"""
        self.receiving = False
        if self.receive_thread:
            self.receive_thread.join(timeout=2)
        print("📡 Ricezione automatica fermata")
    
    def _receive_loop(self, interval: int):
        """Loop di ricezione automatica"""
        while self.receiving:
            try:
                self.check_messages()
            except Exception as e:
                print(f"❌ Errore nel loop di ricezione: {e}")
            
            time.sleep(interval)
    
    def get_conversation_history(self, limit: int = 50) -> List[Message]:
        """Ottiene la cronologia della conversazione"""
        return sorted(self.messages, key=lambda m: m.timestamp)[-limit:]
    
    def search_messages(self, query: str) -> List[Message]:
        """Cerca nei messaggi"""
        query_lower = query.lower()
        return [
            msg for msg in self.messages
            if query_lower in msg.content.lower()
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiche del messenger"""
        total_messages = len(self.messages)
        sent_messages = len([m for m in self.messages if m.sender == self.node_type])
        received_messages = total_messages - sent_messages
        encrypted_messages = len([m for m in self.messages if m.encrypted])
        
        crypto_stats = self.crypto_engine.get_crypto_stats()
        
        return {
            "messenger": {
                "username": self.username,
                "node_type": self.node_type,
                "partner": self.partner_node,
                "active_sessions": len(self.active_sessions),
                "current_session": self.current_session_id
            },
            "messages": {
                "total": total_messages,
                "sent": sent_messages,
                "received": received_messages,
                "encrypted": encrypted_messages,
                "encryption_rate": f"{(encrypted_messages/total_messages)*100:.1f}%" if total_messages > 0 else "0%"
            },
            "crypto": crypto_stats
        }
    
    def save_messages(self):
        """Salva messaggi su file"""
        try:
            data = {
                "username": self.username,
                "node_type": self.node_type,
                "messages": [msg.to_dict() for msg in self.messages],
                "saved_at": datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Errore salvataggio messaggi: {e}")
    
    def load_messages(self):
        """Carica messaggi da file"""
        try:
            if not self.storage_file.exists():
                return
            
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            for msg_data in data.get("messages", []):
                message = Message.from_dict(msg_data)
                self.messages.append(message)
            
            print(f"📁 Caricati {len(self.messages)} messaggi dalla cronologia")
            
        except Exception as e:
            print(f"⚠️ Errore caricamento messaggi: {e}")
    
    def cleanup(self):
        """Pulizia risorse"""
        self.stop_receiving()
        self.key_manager.stop_maintenance()
        self.save_messages()
        print(f"🧹 Cleanup completato per {self.username}")


def format_message_display(message: Message) -> str:
    """Formatta un messaggio per la visualizzazione"""
    timestamp = datetime.fromtimestamp(message.timestamp).strftime("%H:%M:%S")
    encryption_icon = "🔒" if message.encrypted else "📝"
    session_info = f" [S:{message.session_id[:8]}]" if message.session_id else ""
    
    return f"[{timestamp}] {encryption_icon} {message.sender}: {message.content}{session_info}"


def print_conversation_history(messages: List[Message], limit: int = 20):
    """Stampa la cronologia della conversazione"""
    recent_messages = sorted(messages, key=lambda m: m.timestamp)[-limit:]
    
    print("\n" + "="*60)
    print("📜 CRONOLOGIA CONVERSAZIONE")
    print("="*60)
    
    for message in recent_messages:
        print(format_message_display(message))
    
    print("="*60)