"""
QKD Integration Layer - Modulo per integrare QKD in app di messaggistica esistenti
Sostituisce RSA con chiavi quantistiche mantenendo la stessa interfaccia
"""

import json
import base64
import hashlib
import time
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path

from .qkd_key_manager import QKDKeyManager
from .qkd_crypto import QKDCryptoEngine


class QKDKeyProvider:
    """
    Provider di chiavi quantistiche per app di messaggistica.
    Interfaccia semplice per ottenere chiavi fresche dal sistema QKD.
    """
    
    def __init__(self, node_type: str, config: Dict[str, Any] = None):
        """
        Inizializza il provider di chiavi QKD.
        
        Args:
            node_type: "alice" o "bob"
            config: Configurazione opzionale per il key manager
        """
        self.node_type = node_type.lower()
        
        # Configurazione default
        default_config = {
            "min_keys": 50,      # Pool minimo per app messaggistica
            "max_keys": 200,     # Pool massimo
            "auto_refill": True, # Riempimento automatico
            "maintenance_interval": 30  # Secondi
        }
        
        if config:
            default_config.update(config)
        
        # Inizializza key manager
        self.key_manager = QKDKeyManager(
            self.node_type,
            min_keys=default_config["min_keys"],
            max_keys=default_config["max_keys"]
        )
        
        # Avvia manutenzione se richiesta
        if default_config["auto_refill"]:
            self.key_manager.start_maintenance(default_config["maintenance_interval"])
        
        self.crypto_engine = QKDCryptoEngine(self.key_manager)
        
        print(f"🔑 QKD Key Provider inizializzato per {self.node_type.upper()}")
    
    def get_encryption_key(self, key_size: int = 32) -> Optional[bytes]:
        """
        Ottiene una chiave quantistica per crittografia.
        Interfaccia compatibile con sistemi RSA esistenti.
        
        Args:
            key_size: Dimensione chiave richiesta (ignorato, usa chiave QKD completa)
            
        Returns:
            Chiave quantistica come bytes, None se errore
        """
        quantum_key = self.key_manager.get_fresh_key()
        if quantum_key:
            # Deriva una chiave della dimensione richiesta
            derived_key = hashlib.pbkdf2_hmac(
                'sha256',
                quantum_key.key_data,
                b'messaging_app_salt',
                100000,
                key_size
            )
            return derived_key
        return None
    
    def get_key_pair(self) -> Optional[Tuple[bytes, str]]:
        """
        Simula una coppia di chiavi per compatibilità con sistemi esistenti.
        In realtà restituisce una chiave quantistica e il suo ID.
        
        Returns:
            Tupla (chiave_privata_simulata, id_chiave_pubblica)
        """
        quantum_key = self.key_manager.get_fresh_key()
        if quantum_key:
            return quantum_key.key_data, quantum_key.key_id
        return None
    
    def get_available_keys_count(self) -> int:
        """Restituisce il numero di chiavi disponibili"""
        return len(self.key_manager.key_pool)
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Restituisce lo status del provider"""
        return self.key_manager.get_pool_status()
    
    def cleanup(self):
        """Pulizia risorse"""
        self.key_manager.stop_maintenance()
        self.key_manager.save_keys_to_storage()


class QKDCryptoAdapter:
    """
    Adapter per sostituire la crittografia RSA con QKD nella tua app.
    Mantiene la stessa interfaccia dei sistemi RSA esistenti.
    """
    
    def __init__(self, node_type: str):
        """
        Inizializza l'adapter crittografico.
        
        Args:
            node_type: "alice" o "bob"
        """
        self.node_type = node_type.lower()
        self.partner_node = "bob" if node_type == "alice" else "alice"
        
        self.key_provider = QKDKeyProvider(node_type)
        self.crypto_engine = self.key_provider.crypto_engine
        
        print(f"🔐 QKD Crypto Adapter inizializzato per {node_type.upper()}")
    
    def encrypt(self, message: Union[str, bytes], recipient_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Cripta un messaggio usando QKD.
        Interfaccia compatibile con encrypt RSA.
        
        Args:
            message: Messaggio da crittare (str o bytes)
            recipient_id: ID destinatario (opzionale, usa partner di default)
            
        Returns:
            Dizionario con messaggio crittato e metadati
        """
        # Converti in stringa se necessario
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        
        recipient = recipient_id or self.partner_node
        
        # Usa il crypto engine QKD
        encrypted_package = self.crypto_engine.encrypt_message(message, recipient)
        
        if encrypted_package:
            # Aggiungi metadati per compatibilità
            encrypted_package.update({
                "encryption_type": "QKD",
                "key_type": "quantum",
                "algorithm": "AES-256-GCM + QKD",
                "compatible_format": True
            })
        
        return encrypted_package
    
    def decrypt(self, encrypted_data: Dict[str, Any]) -> Optional[str]:
        """
        Decripta un messaggio usando QKD.
        Interfaccia compatibile con decrypt RSA.
        
        Args:
            encrypted_data: Dati crittati (formato QKD o compatibile)
            
        Returns:
            Messaggio in chiaro o None se errore
        """
        # Verifica formato
        if not isinstance(encrypted_data, dict):
            print("❌ Formato dati crittati non valido")
            return None
        
        # Gestisci diversi formati per retrocompatibilità
        if encrypted_data.get("encryption_type") == "QKD":
            # Formato QKD nativo
            return self.crypto_engine.decrypt_message(encrypted_data)
        
        elif "ciphertext" in encrypted_data and "key_id" in encrypted_data:
            # Formato QKD standard
            return self.crypto_engine.decrypt_message(encrypted_data)
        
        else:
            print("❌ Formato crittografia non riconosciuto")
            return None
    
    def generate_session_key(self, session_id: str) -> Optional[str]:
        """
        Genera una chiave di sessione usando QKD.
        Utile per chat lunghe senza consumare troppe chiavi quantistiche.
        
        Args:
            session_id: Identificativo univoco della sessione
            
        Returns:
            Chiave di sessione codificata in base64
        """
        channel_info = self.crypto_engine.create_secure_channel_key(session_id)
        if channel_info:
            return channel_info["fernet_key"]
        return None
    
    def encrypt_with_session(self, message: str, session_key: str) -> Optional[str]:
        """Cripta con chiave di sessione"""
        return self.crypto_engine.encrypt_with_session_key(message, session_key)
    
    def decrypt_with_session(self, encrypted_message: str, session_key: str) -> Optional[str]:
        """Decripta con chiave di sessione"""
        return self.crypto_engine.decrypt_with_session_key(encrypted_message, session_key)
    
    def get_public_key_equivalent(self) -> str:
        """
        Restituisce un identificatore pubblico per questo nodo.
        Simula la chiave pubblica RSA per compatibilità.
        """
        node_info = {
            "node_type": self.node_type,
            "qkd_endpoint": f"qkd://{self.node_type}",
            "crypto_capabilities": ["AES-256-GCM", "HMAC-SHA256", "QKD"],
            "created_at": datetime.now().isoformat()
        }
        
        # Crea un hash dell'info del nodo come "chiave pubblica"
        node_json = json.dumps(node_info, sort_keys=True)
        public_key_hash = hashlib.sha256(node_json.encode()).hexdigest()
        
        return f"qkd_public_{self.node_type}_{public_key_hash[:16]}"
    
    def verify_partner_key(self, partner_key: str) -> bool:
        """
        Verifica la "chiave pubblica" del partner.
        In QKD la verifica avviene tramite il canale quantistico.
        """
        # Verifica formato chiave partner
        if partner_key.startswith(f"qkd_public_{self.partner_node}_"):
            print(f"✅ Chiave partner {self.partner_node} verificata")
            return True
        
        print(f"❌ Chiave partner non valida: {partner_key}")
        return False
    
    def get_crypto_info(self) -> Dict[str, Any]:
        """Restituisce informazioni sulla crittografia utilizzata"""
        return {
            "encryption_method": "Quantum Key Distribution",
            "algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2-SHA256",
            "authentication": "HMAC-SHA256",
            "perfect_forward_secrecy": True,
            "quantum_safe": True,
            "node_type": self.node_type,
            "available_keys": self.key_provider.get_available_keys_count(),
            "status": "operational"
        }
    
    def cleanup(self):
        """Pulizia risorse"""
        self.key_provider.cleanup()


class QKDMessageWrapper:
    """
    Wrapper per integrare QKD nei messaggi della tua app esistente.
    Aggiunge layer di crittografia quantistica trasparente.
    """
    
    def __init__(self, node_type: str):
        self.crypto_adapter = QKDCryptoAdapter(node_type)
        self.node_type = node_type
    
    def wrap_outgoing_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrappa un messaggio in uscita con crittografia QKD.
        
        Args:
            message_data: Dati originali del messaggio dalla tua app
            
        Returns:
            Messaggio wrappato con crittografia QKD
        """
        try:
            # Estrai il contenuto del messaggio
            content = message_data.get("content", "")
            recipient = message_data.get("recipient", "")
            
            # Cripta con QKD
            encrypted_package = self.crypto_adapter.encrypt(content, recipient)
            
            if encrypted_package:
                # Crea messaggio wrappato
                wrapped_message = {
                    # Metadati originali (non crittati)
                    "message_id": message_data.get("message_id"),
                    "sender": message_data.get("sender"),
                    "recipient": message_data.get("recipient"),
                    "timestamp": message_data.get("timestamp", time.time()),
                    "message_type": message_data.get("message_type", "text"),
                    
                    # Contenuto crittato con QKD
                    "encrypted_content": encrypted_package,
                    "encryption_method": "QKD",
                    
                    # Flag per identificare messaggi QKD
                    "qkd_encrypted": True,
                    "quantum_safe": True
                }
                
                return wrapped_message
            
            else:
                print("❌ Errore crittografia QKD, invio messaggio non crittato")
                return message_data
        
        except Exception as e:
            print(f"❌ Errore wrap messaggio: {e}")
            return message_data
    
    def unwrap_incoming_message(self, wrapped_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unwrappa un messaggio in arrivo crittato con QKD.
        
        Args:
            wrapped_message: Messaggio wrappato ricevuto
            
        Returns:
            Messaggio originale decrittato
        """
        try:
            # Verifica se è un messaggio QKD
            if not wrapped_message.get("qkd_encrypted", False):
                # Messaggio normale, restituisci così com'è
                return wrapped_message
            
            # Decritta il contenuto
            encrypted_content = wrapped_message.get("encrypted_content", {})
            decrypted_content = self.crypto_adapter.decrypt(encrypted_content)
            
            if decrypted_content:
                # Ricostruisci il messaggio originale
                original_message = {
                    "message_id": wrapped_message.get("message_id"),
                    "sender": wrapped_message.get("sender"),
                    "recipient": wrapped_message.get("recipient"),
                    "timestamp": wrapped_message.get("timestamp"),
                    "message_type": wrapped_message.get("message_type", "text"),
                    "content": decrypted_content,
                    
                    # Metadati crittografia
                    "was_encrypted": True,
                    "encryption_method": "QKD",
                    "quantum_safe": True
                }
                
                return original_message
            
            else:
                print("❌ Impossibile decrittare messaggio QKD")
                return {
                    "error": "Decryption failed",
                    "original_message": wrapped_message
                }
        
        except Exception as e:
            print(f"❌ Errore unwrap messaggio: {e}")
            return {"error": str(e), "original_message": wrapped_message}
    
    def cleanup(self):
        """Pulizia risorse"""
        self.crypto_adapter.cleanup()


def create_qkd_integration(node_type: str, integration_type: str = "adapter") -> Union[QKDCryptoAdapter, QKDMessageWrapper, QKDKeyProvider]:
    """
    Factory function per creare l'integrazione QKD appropriata.
    
    Args:
        node_type: "alice" o "bob"
        integration_type: "adapter", "wrapper", o "provider"
        
    Returns:
        Oggetto di integrazione appropriato
    """
    if integration_type == "adapter":
        return QKDCryptoAdapter(node_type)
    elif integration_type == "wrapper":
        return QKDMessageWrapper(node_type)
    elif integration_type == "provider":
        return QKDKeyProvider(node_type)
    else:
        raise ValueError(f"Tipo integrazione non valido: {integration_type}")


# Esempio di utilizzo per la tua app esistente
def example_integration():
    """
    Esempio di come integrare QKD nella tua app di messaggistica esistente.
    """
    
    # 1. OPZIONE ADAPTER - Sostituisce completamente RSA
    print("🔧 Esempio integrazione con Adapter:")
    
    # Nella tua app, invece di inizializzare RSA:
    # rsa_crypto = RSACrypto()
    
    # Usa QKD:
    qkd_crypto = QKDCryptoAdapter("alice")
    
    # Stesso utilizzo di prima
    message = "Hello Bob, questo messaggio è protetto da QKD!"
    encrypted = qkd_crypto.encrypt(message)
    print(f"Messaggio crittato: {encrypted['key_id']}")
    
    # Per decrittare (lato Bob)
    # qkd_crypto_bob = QKDCryptoAdapter("bob")
    # decrypted = qkd_crypto_bob.decrypt(encrypted)
    
    print("\n" + "="*50 + "\n")
    
    # 2. OPZIONE WRAPPER - Aggiunge QKD ai messaggi esistenti
    print("📦 Esempio integrazione con Wrapper:")
    
    wrapper = QKDMessageWrapper("alice")
    
    # Messaggio dalla tua app esistente
    original_message = {
        "message_id": "msg_123",
        "sender": "alice",
        "recipient": "bob",
        "content": "Ciao Bob!",
        "timestamp": time.time()
    }
    
    # Wrappa con QKD
    wrapped = wrapper.wrap_outgoing_message(original_message)
    print(f"Messaggio wrappato con QKD: {wrapped.get('qkd_encrypted')}")
    
    # Unwrappa (lato ricevente)
    # unwrapped = wrapper.unwrap_incoming_message(wrapped)
    
    # Cleanup
    qkd_crypto.cleanup()
    wrapper.cleanup()


if __name__ == "__main__":
    example_integration()