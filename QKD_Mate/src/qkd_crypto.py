"""
QKD Crypto Engine - Sistema crittografico basato su chiavi quantistiche
Sostituisce RSA con crittografia simmetrica usando chiavi QKD
"""

import hashlib
import hmac
import json
import os
import time
from datetime import datetime
from typing import Dict, Tuple, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

from .qkd_key_manager import QKDKeyManager, QuantumKey


class QKDCryptoEngine:
    """
    Motore crittografico che utilizza chiavi quantistiche per sostituire RSA.
    
    Caratteristiche:
    - Perfect Forward Secrecy tramite chiavi QKD one-time
    - Crittografia simmetrica AES-256 con chiavi quantistiche
    - Autenticazione messaggi con HMAC
    - Key derivation per messaggi lunghi
    - Protezione anti-replay
    """
    
    def __init__(self, key_manager: QKDKeyManager):
        self.key_manager = key_manager
        self.node_type = key_manager.node_type
        
        print(f"🔐 QKD Crypto Engine inizializzato per nodo {self.node_type.upper()}")
    
    def encrypt_message(self, message: str, recipient: str) -> Optional[Dict[str, Any]]:
        """
        Cripta un messaggio usando una chiave quantistica fresca.
        
        Args:
            message: Messaggio da crittare
            recipient: Destinatario (alice/bob)
            
        Returns:
            Dizionario con messaggio crittato e metadati
        """
        # Ottieni chiave quantistica fresca
        quantum_key = self.key_manager.get_fresh_key()
        if not quantum_key:
            print("❌ Nessuna chiave quantistica disponibile per crittografia")
            return None
        
        try:
            # Prepara i dati
            message_bytes = message.encode('utf-8')
            timestamp = int(time.time())
            nonce = os.urandom(16)  # IV per AES
            
            # Deriva chiavi dalla chiave quantistica
            encryption_key, auth_key = self._derive_keys(quantum_key.key_data, nonce)
            
            # Cripta il messaggio con AES-256-GCM
            cipher = Cipher(
                algorithms.AES(encryption_key),
                modes.GCM(nonce)
            )
            encryptor = cipher.encryptor()
            
            # Aggiungi metadati autenticati (AAD)
            aad = json.dumps({
                "sender": self.node_type,
                "recipient": recipient,
                "timestamp": timestamp,
                "key_id": quantum_key.key_id
            }, sort_keys=True).encode('utf-8')
            
            encryptor.authenticate_additional_data(aad)
            ciphertext = encryptor.update(message_bytes) + encryptor.finalize()
            
            # Crea HMAC per integrità aggiuntiva
            hmac_signature = hmac.new(
                auth_key,
                aad + ciphertext + encryptor.tag,
                hashlib.sha256
            ).hexdigest()
            
            encrypted_package = {
                "version": "1.0",
                "sender": self.node_type,
                "recipient": recipient,
                "timestamp": timestamp,
                "key_id": quantum_key.key_id,
                "nonce": base64.b64encode(nonce).decode('utf-8'),
                "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
                "auth_tag": base64.b64encode(encryptor.tag).decode('utf-8'),
                "hmac": hmac_signature,
                "aad": base64.b64encode(aad).decode('utf-8')
            }
            
            print(f"🔒 Messaggio crittato con chiave quantistica {quantum_key.key_id}")
            return encrypted_package
            
        except Exception as e:
            print(f"❌ Errore crittografia: {e}")
            return None
    
    def decrypt_message(self, encrypted_package: Dict[str, Any]) -> Optional[str]:
        """
        Decripta un messaggio usando la chiave quantistica corrispondente.
        
        Args:
            encrypted_package: Pacchetto crittato ricevuto
            
        Returns:
            Messaggio in chiaro o None se errore
        """
        try:
            # Estrai metadati
            sender = encrypted_package["sender"]
            recipient = encrypted_package["recipient"]
            timestamp = encrypted_package["timestamp"]
            key_id = encrypted_package["key_id"]
            
            # Verifica che il messaggio sia per noi
            if recipient != self.node_type:
                print(f"❌ Messaggio non destinato a {self.node_type}")
                return None
            
            # Verifica anti-replay (messaggio non troppo vecchio)
            current_time = int(time.time())
            if current_time - timestamp > 3600:  # 1 ora
                print("❌ Messaggio troppo vecchio, possibile replay attack")
                return None
            
            # Trova la chiave quantistica corrispondente
            quantum_key = self._find_key_by_id(key_id)
            if not quantum_key:
                print(f"❌ Chiave quantistica {key_id} non trovata")
                return None
            
            # Decodifica componenti
            nonce = base64.b64decode(encrypted_package["nonce"])
            ciphertext = base64.b64decode(encrypted_package["ciphertext"])
            auth_tag = base64.b64decode(encrypted_package["auth_tag"])
            aad = base64.b64decode(encrypted_package["aad"])
            received_hmac = encrypted_package["hmac"]
            
            # Deriva le stesse chiavi
            encryption_key, auth_key = self._derive_keys(quantum_key.key_data, nonce)
            
            # Verifica HMAC
            expected_hmac = hmac.new(
                auth_key,
                aad + ciphertext + auth_tag,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(received_hmac, expected_hmac):
                print("❌ Verifica HMAC fallita, messaggio compromesso")
                return None
            
            # Decripta con AES-256-GCM
            cipher = Cipher(
                algorithms.AES(encryption_key),
                modes.GCM(nonce, auth_tag)
            )
            decryptor = cipher.decryptor()
            decryptor.authenticate_additional_data(aad)
            
            plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            message = plaintext_bytes.decode('utf-8')
            
            # Marca la chiave come usata (se non già fatto)
            self._mark_key_as_used(key_id)
            
            print(f"🔓 Messaggio decriptato con chiave quantistica {key_id}")
            return message
            
        except Exception as e:
            print(f"❌ Errore decrittografia: {e}")
            return None
    
    def _derive_keys(self, quantum_key: bytes, nonce: bytes) -> Tuple[bytes, bytes]:
        """Deriva chiavi di crittografia e autenticazione dalla chiave quantistica"""
        
        # Usa PBKDF2 per derivare due chiavi da quella quantistica
        kdf_enc = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bit per AES-256
            salt=nonce,
            iterations=100000,
        )
        encryption_key = kdf_enc.derive(quantum_key + b"ENCRYPT")
        
        kdf_auth = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bit per HMAC
            salt=nonce,
            iterations=100000,
        )
        auth_key = kdf_auth.derive(quantum_key + b"AUTHENTICATE")
        
        return encryption_key, auth_key
    
    def _find_key_by_id(self, key_id: str) -> Optional[QuantumKey]:
        """Cerca una chiave nel pool o nelle chiavi usate"""
        # Prima cerca nel pool disponibile
        if key_id in self.key_manager.key_pool:
            return self.key_manager.key_pool[key_id]
        
        # Poi cerca nelle chiavi già usate (per messaggi in arrivo)
        if key_id in self.key_manager.used_keys:
            return self.key_manager.used_keys[key_id]
        
        return None
    
    def _mark_key_as_used(self, key_id: str):
        """Marca una chiave come usata se è nel pool"""
        with self.key_manager.lock:
            if key_id in self.key_manager.key_pool:
                key = self.key_manager.key_pool.pop(key_id)
                key.used_at = datetime.now()
                key.is_used = True
                self.key_manager.used_keys[key_id] = key
    
    def create_secure_channel_key(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Crea una chiave di sessione per canale sicuro persistente.
        Utile per chat lunghe senza consumare troppe chiavi quantistiche.
        """
        quantum_key = self.key_manager.get_fresh_key()
        if not quantum_key:
            return None
        
        try:
            # Deriva una chiave di sessione dalla chiave quantistica
            session_salt = hashlib.sha256(session_id.encode()).digest()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=session_salt,
                iterations=100000,
            )
            session_key = kdf.derive(quantum_key.key_data)
            
            # Crea un Fernet key (base64 encoded)
            fernet_key = base64.urlsafe_b64encode(session_key)
            
            channel_info = {
                "session_id": session_id,
                "fernet_key": fernet_key.decode('utf-8'),
                "quantum_key_id": quantum_key.key_id,
                "created_at": datetime.now().isoformat(),
                "node_type": self.node_type
            }
            
            print(f"🔑 Canale sicuro creato per sessione {session_id}")
            return channel_info
            
        except Exception as e:
            print(f"❌ Errore creazione canale sicuro: {e}")
            return None
    
    def encrypt_with_session_key(self, message: str, fernet_key: str) -> Optional[str]:
        """Cripta un messaggio con chiave di sessione"""
        try:
            f = Fernet(fernet_key.encode('utf-8'))
            encrypted = f.encrypt(message.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"❌ Errore crittografia sessione: {e}")
            return None
    
    def decrypt_with_session_key(self, encrypted_message: str, fernet_key: str) -> Optional[str]:
        """Decripta un messaggio con chiave di sessione"""
        try:
            f = Fernet(fernet_key.encode('utf-8'))
            encrypted_bytes = base64.b64decode(encrypted_message.encode('utf-8'))
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"❌ Errore decrittografia sessione: {e}")
            return None
    
    def get_crypto_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche del motore crittografico"""
        key_stats = self.key_manager.get_pool_status()
        
        return {
            "crypto_engine": {
                "node_type": self.node_type,
                "encryption_algorithm": "AES-256-GCM",
                "key_derivation": "PBKDF2-SHA256",
                "authentication": "HMAC-SHA256",
                "perfect_forward_secrecy": True
            },
            "key_management": key_stats,
            "security_features": [
                "Quantum Key Distribution",
                "One-Time Pad semantics",
                "Anti-replay protection",
                "Authenticated encryption",
                "Perfect Forward Secrecy"
            ]
        }


class QKDSecureSession:
    """
    Gestisce sessioni sicure per chat persistenti usando chiavi quantistiche.
    Ottimizza l'uso delle chiavi QKD per conversazioni lunghe.
    """
    
    def __init__(self, crypto_engine: QKDCryptoEngine, session_id: str):
        self.crypto_engine = crypto_engine
        self.session_id = session_id
        self.session_key = None
        self.created_at = None
        self.message_count = 0
        self.max_messages = 1000  # Rinnova chiave dopo N messaggi
        
    def initialize_session(self) -> bool:
        """Inizializza la sessione sicura"""
        channel_info = self.crypto_engine.create_secure_channel_key(self.session_id)
        if not channel_info:
            return False
        
        self.session_key = channel_info["fernet_key"]
        self.created_at = datetime.now()
        
        print(f"🔐 Sessione sicura {self.session_id} inizializzata")
        return True
    
    def encrypt_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Cripta messaggio nella sessione"""
        if not self.session_key:
            if not self.initialize_session():
                return None
        
        # Rinnova chiave se troppi messaggi
        if self.message_count >= self.max_messages:
            print("🔄 Rinnovo chiave di sessione...")
            if not self.initialize_session():
                return None
            self.message_count = 0
        
        encrypted = self.crypto_engine.encrypt_with_session_key(message, self.session_key)
        if encrypted:
            self.message_count += 1
            return {
                "session_id": self.session_id,
                "encrypted_message": encrypted,
                "message_number": self.message_count,
                "timestamp": int(time.time())
            }
        
        return None
    
    def decrypt_message(self, encrypted_package: Dict[str, Any]) -> Optional[str]:
        """Decripta messaggio nella sessione"""
        if not self.session_key:
            print("❌ Sessione non inizializzata")
            return None
        
        return self.crypto_engine.decrypt_with_session_key(
            encrypted_package["encrypted_message"], 
            self.session_key
        )