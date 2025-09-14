"""
Client QKD per Bob (Slave SAE)
=============================

Questo modulo fornisce una factory function per creare un client QKD
configurato specificamente per Bob nel ruolo di Slave SAE.

Bob è il nodo "slave" nel protocollo ETSI GS QKD 014, il che significa:
- Riceve key_ID da Alice attraverso canali classici
- Usa i key_ID per recuperare le chiavi corrispondenti dal suo KME
- Non può iniziare richieste di nuove chiavi (solo Alice può farlo)
- Verifica lo stato dei link QKD con Alice
"""

from pathlib import Path
from .client import QKDClient


def bob_client() -> QKDClient:
    """
    Factory function per creare un client QKD configurato per Bob.
    
    Questa funzione è un wrapper di convenienza che:
    1. Localizza automaticamente il file di configurazione bob.yaml
    2. Crea un'istanza di QKDClient con la configurazione corretta
    3. Ritorna un client pronto per le operazioni slave
    
    Returns:
        QKDClient: Un'istanza configurata per Bob con:
                  - Endpoint: https://78.40.171.144:443 (KME di Bob)
                  - Certificati: client_Bob2.crt/key
                  - Ruolo: Slave SAE
    
    Configurazione caricata:
        - bob.yaml: Configurazione specifica di Bob
        - common.yaml: Configurazioni condivise (API paths, timeout, etc.)
    
    Esempio d'uso:
        # Crea client per Bob
        bob = bob_client()
        
        # Bob verifica lo stato del link con Alice
        status = bob.get_status("Alice2")
        print(f"Chiavi disponibili: {status['stored_key_count']}")
        
        # Bob riceve key_ID da Alice (tramite canale classico)
        key_id = "550e8400-e29b-41d4-a716-446655440000"  # Da Alice
        
        # Bob recupera la chiave usando il key_ID
        response = bob.get_key_with_ids("Alice2", [key_id])
        chiave = response['keys'][0]['key']
        
        print(f"Chiave ricevuta: {chiave}")
    
    Note:
        - Bob deve avere i certificati client_Bob2.crt e client_Bob2.key
        - Il KME di Bob deve essere raggiungibile su 78.40.171.144:443
        - Bob può solo recuperare chiavi con key_ID, non richiederne di nuove
        - Il key_ID deve essere comunicato da Alice tramite canale sicuro
    """
    # Determina il percorso del file di configurazione
    # Partendo dalla posizione di questo modulo (src/), sale di un livello
    # per raggiungere la directory principale QKD_Mate/
    module_dir = Path(__file__).parent.parent  # Go up from src/ to QKD_Mate/
    config_path = module_dir / "config" / "bob.yaml"
    
    # Crea e ritorna il client configurato
    return QKDClient(config_path)