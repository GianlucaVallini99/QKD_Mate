"""
QKD Key Manager - Gestisce il pool di chiavi quantistiche per messaggistica sicura
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

from .alice_client import alice_client
from .bob_client import bob_client
from .utils import QKDClientError


@dataclass
class QuantumKey:
    """Rappresenta una chiave quantistica"""
    key_id: str
    key_data: bytes
    created_at: datetime
    used_at: Optional[datetime] = None
    partner_node: str = ""  # alice o bob
    is_used: bool = False
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['used_at'] = self.used_at.isoformat() if self.used_at else None
        data['key_data'] = self.key_data.hex()  # Converti bytes in hex per JSON
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QuantumKey':
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['used_at'] = datetime.fromisoformat(data['used_at']) if data['used_at'] else None
        data['key_data'] = bytes.fromhex(data['key_data'])
        return cls(**data)


class QKDKeyManager:
    """
    Gestore del pool di chiavi quantistiche per messaggistica sicura.
    
    Funzionalità:
    - Mantiene un pool di chiavi quantistiche fresche
    - Richiede automaticamente nuove chiavi quando necessario
    - Gestisce l'uso one-time delle chiavi (OTP)
    - Sincronizza chiavi tra Alice e Bob
    """
    
    def __init__(self, node_type: str, min_keys: int = 10, max_keys: int = 50):
        self.node_type = node_type.lower()
        self.min_keys = min_keys
        self.max_keys = max_keys
        self.key_pool: Dict[str, QuantumKey] = {}
        self.used_keys: Dict[str, QuantumKey] = {}
        self.lock = threading.RLock()
        
        # Client QKD
        if self.node_type == "alice":
            self.qkd_client = alice_client()
            self.partner_node = "bob"
        elif self.node_type == "bob":
            self.qkd_client = bob_client()
            self.partner_node = "alice"
        else:
            raise ValueError(f"Tipo nodo non valido: {node_type}")
        
        # File di persistenza
        self.storage_file = Path(f"keys_pool_{self.node_type}.json")
        
        # Thread per manutenzione automatica
        self.maintenance_thread = None
        self.running = False
        
        self.load_keys_from_storage()
        print(f"🔑 QKD Key Manager inizializzato per nodo {self.node_type.upper()}")
        print(f"   Pool minimo: {min_keys} chiavi, massimo: {max_keys}")
        print(f"   Chiavi caricate: {len(self.key_pool)}")
    
    def start_maintenance(self, interval: int = 60):
        """Avvia il thread di manutenzione automatica del pool"""
        if self.maintenance_thread and self.maintenance_thread.is_alive():
            return
        
        self.running = True
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_loop, 
            args=(interval,), 
            daemon=True
        )
        self.maintenance_thread.start()
        print(f"🔧 Manutenzione automatica avviata (intervallo: {interval}s)")
    
    def stop_maintenance(self):
        """Ferma il thread di manutenzione"""
        self.running = False
        if self.maintenance_thread:
            self.maintenance_thread.join(timeout=5)
        print("🛑 Manutenzione automatica fermata")
    
    def _maintenance_loop(self, interval: int):
        """Loop di manutenzione automatica"""
        while self.running:
            try:
                self.refill_key_pool()
                self.cleanup_old_keys()
                self.save_keys_to_storage()
            except Exception as e:
                print(f"❌ Errore durante manutenzione: {e}")
            
            time.sleep(interval)
    
    def refill_key_pool(self) -> int:
        """Riempie il pool di chiavi se sotto il minimo"""
        with self.lock:
            current_keys = len(self.key_pool)
            
            if current_keys >= self.min_keys:
                return 0
            
            keys_needed = self.max_keys - current_keys
            print(f"🔄 Richiesta {keys_needed} nuove chiavi quantistiche...")
            
            try:
                # Richiedi chiavi dal nodo QKD
                response = self.qkd_client.post("keys", {"count": keys_needed})
                
                # Processa la risposta (formato dipende dal vendor QKD)
                new_keys = self._process_qkd_response(response)
                
                for key in new_keys:
                    self.key_pool[key.key_id] = key
                
                print(f"✅ Aggiunte {len(new_keys)} chiavi quantistiche al pool")
                return len(new_keys)
                
            except Exception as e:
                print(f"❌ Errore richiesta chiavi: {e}")
                return 0
    
    def _process_qkd_response(self, response) -> List[QuantumKey]:
        """Processa la risposta del sistema QKD e crea oggetti QuantumKey"""
        keys = []
        
        # Formato risposta può variare - adattare in base al vendor
        if isinstance(response, dict):
            if "keys" in response:
                key_data_list = response["keys"]
            elif "key_data" in response:
                key_data_list = [response["key_data"]]
            else:
                # Fallback: usa l'intera risposta come chiave singola
                key_data_list = [str(response)]
        else:
            key_data_list = [str(response)]
        
        for i, key_data in enumerate(key_data_list):
            # Genera ID univoco per la chiave
            timestamp = datetime.now()
            key_id = hashlib.sha256(
                f"{self.node_type}_{timestamp.isoformat()}_{i}_{key_data}".encode()
            ).hexdigest()[:16]
            
            # Converti in bytes se necessario
            if isinstance(key_data, str):
                key_bytes = key_data.encode('utf-8')
            else:
                key_bytes = bytes(key_data)
            
            quantum_key = QuantumKey(
                key_id=key_id,
                key_data=key_bytes,
                created_at=timestamp,
                partner_node=self.partner_node
            )
            
            keys.append(quantum_key)
        
        return keys
    
    def get_fresh_key(self) -> Optional[QuantumKey]:
        """Ottiene una chiave fresca dal pool per crittografia"""
        with self.lock:
            if not self.key_pool:
                print("⚠️ Pool di chiavi vuoto, tentativo riempimento...")
                self.refill_key_pool()
                
                if not self.key_pool:
                    print("❌ Impossibile ottenere chiavi quantistiche")
                    return None
            
            # Prendi la chiave più vecchia (FIFO)
            key_id = min(self.key_pool.keys(), 
                        key=lambda k: self.key_pool[k].created_at)
            key = self.key_pool.pop(key_id)
            
            # Marca come usata
            key.used_at = datetime.now()
            key.is_used = True
            self.used_keys[key_id] = key
            
            print(f"🔑 Chiave quantistica utilizzata: {key_id}")
            return key
    
    def cleanup_old_keys(self, max_age_hours: int = 24):
        """Rimuove chiavi vecchie dal pool"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self.lock:
            # Rimuovi chiavi vecchie dal pool
            old_keys = [
                key_id for key_id, key in self.key_pool.items()
                if key.created_at < cutoff_time
            ]
            
            for key_id in old_keys:
                del self.key_pool[key_id]
            
            # Rimuovi chiavi usate molto vecchie
            old_used_keys = [
                key_id for key_id, key in self.used_keys.items()
                if key.used_at and key.used_at < cutoff_time
            ]
            
            for key_id in old_used_keys:
                del self.used_keys[key_id]
            
            if old_keys or old_used_keys:
                print(f"🧹 Rimosse {len(old_keys)} chiavi vecchie e {len(old_used_keys)} chiavi usate")
    
    def get_pool_status(self) -> Dict:
        """Restituisce lo stato del pool di chiavi"""
        with self.lock:
            return {
                "node_type": self.node_type,
                "available_keys": len(self.key_pool),
                "used_keys": len(self.used_keys),
                "min_threshold": self.min_keys,
                "max_capacity": self.max_keys,
                "oldest_key_age": self._get_oldest_key_age(),
                "last_updated": datetime.now().isoformat()
            }
    
    def _get_oldest_key_age(self) -> Optional[str]:
        """Calcola l'età della chiave più vecchia"""
        if not self.key_pool:
            return None
        
        oldest_key = min(self.key_pool.values(), key=lambda k: k.created_at)
        age = datetime.now() - oldest_key.created_at
        return str(age)
    
    def save_keys_to_storage(self):
        """Salva il pool di chiavi su file"""
        try:
            data = {
                "key_pool": {k: v.to_dict() for k, v in self.key_pool.items()},
                "used_keys": {k: v.to_dict() for k, v in self.used_keys.items()},
                "saved_at": datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Errore salvataggio chiavi: {e}")
    
    def load_keys_from_storage(self):
        """Carica il pool di chiavi da file"""
        try:
            if not self.storage_file.exists():
                return
            
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            # Carica chiavi disponibili
            for key_id, key_data in data.get("key_pool", {}).items():
                self.key_pool[key_id] = QuantumKey.from_dict(key_data)
            
            # Carica chiavi usate
            for key_id, key_data in data.get("used_keys", {}).items():
                self.used_keys[key_id] = QuantumKey.from_dict(key_data)
            
            print(f"📁 Caricate {len(self.key_pool)} chiavi dal storage")
            
        except Exception as e:
            print(f"⚠️ Errore caricamento chiavi: {e}")
    
    def force_key_refresh(self, count: int = None) -> int:
        """Forza il refresh del pool con nuove chiavi"""
        if count is None:
            count = self.max_keys
        
        print(f"🔄 Refresh forzato di {count} chiavi...")
        
        try:
            response = self.qkd_client.post("keys", {"count": count})
            new_keys = self._process_qkd_response(response)
            
            with self.lock:
                for key in new_keys:
                    self.key_pool[key.key_id] = key
            
            print(f"✅ Pool aggiornato con {len(new_keys)} nuove chiavi")
            return len(new_keys)
            
        except Exception as e:
            print(f"❌ Errore refresh chiavi: {e}")
            return 0