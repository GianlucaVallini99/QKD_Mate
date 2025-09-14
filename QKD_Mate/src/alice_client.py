"""
Client QKD per Alice (Master SAE)
================================

Questo modulo fornisce una factory function per creare un client QKD
configurato specificamente per Alice nel ruolo di Master SAE.

Alice è il nodo "master" nel protocollo ETSI GS QKD 014, il che significa:
- Inizia le richieste di chiavi quantistiche
- Riceve chiavi + key_ID dal suo KME
- Comunica i key_ID a Bob attraverso canali classici
- Ha priorità nella gestione delle sessioni QKD
"""

from pathlib import Path
from .client import QKDClient


def alice_client() -> QKDClient:
    """
    Factory function per creare un client QKD configurato per Alice.
    
    Questa funzione è un wrapper di convenienza che:
    1. Localizza automaticamente il file di configurazione alice.yaml
    2. Crea un'istanza di QKDClient con la configurazione corretta
    3. Ritorna un client pronto per le operazioni master
    
    Returns:
        QKDClient: Un'istanza configurata per Alice con:
                  - Endpoint: https://78.40.171.143:443 (KME di Alice)
                  - Certificati: client_Alice2.crt/key
                  - Ruolo: Master SAE
    
    Configurazione caricata:
        - alice.yaml: Configurazione specifica di Alice
        - common.yaml: Configurazioni condivise (API paths, timeout, etc.)
    
    Esempio d'uso:
        # Crea client per Alice
        alice = alice_client()
        
        # Alice richiede una chiave per comunicare con Bob
        response = alice.get_key("Bob2", number=1, size=256)
        key_id = response['keys'][0]['key_ID']
        
        # Alice ora può comunicare key_id a Bob
        print(f"Comunica questo key_ID a Bob: {key_id}")
    
    Note:
        - Alice deve avere i certificati client_Alice2.crt e client_Alice2.key
        - Il KME di Alice deve essere raggiungibile su 78.40.171.143:443
        - Alice può richiedere chiavi ma non può usare key_ID per recuperarle
    """
    # Determina il percorso del file di configurazione
    # Partendo dalla posizione di questo modulo (src/), sale di un livello
    # per raggiungere la directory principale QKD_Mate/
    module_dir = Path(__file__).parent.parent  # Go up from src/ to QKD_Mate/
    config_path = module_dir / "config" / "alice.yaml"
    
    # Crea e ritorna il client configurato
    return QKDClient(config_path)