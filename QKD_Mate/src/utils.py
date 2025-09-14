"""
Utilities per il client QKD - Gestione errori e retry logic
==========================================================

Questo modulo fornisce utilities condivise per la gestione degli errori
e meccanismi di retry per le comunicazioni con i KME (Key Management Entity).
"""

import time
import functools
from typing import Callable, Type


class QKDClientError(Exception):
    """
    Eccezione personalizzata per errori del client QKD.
    
    Questa classe viene utilizzata per incapsulare tutti gli errori
    specifici del protocollo QKD, distinguendoli da errori generici
    di rete o di sistema.
    
    Esempi di utilizzo:
        - Errori HTTP 400/401/503 dai KME
        - Parametri non validi (es. size non multiplo di 8)
        - Certificati mancanti o non validi
        - Errori di parsing delle risposte JSON
    """
    pass


def retry(exceptions: tuple[Type[BaseException], ...], tries: int = 2, delay: float = 0.8):
    """
    Decorator per implementare retry automatico su funzioni che possono fallire.
    
    Questo decorator è fondamentale per la robustezza delle comunicazioni QKD,
    poiché i KME possono essere temporaneamente non disponibili o sovraccarichi.
    
    Args:
        exceptions: Tupla delle eccezioni su cui fare retry
                   Es: (requests.RequestException, ConnectionError)
        tries: Numero massimo di tentativi (default: 2)
               - tries=1: nessun retry, solo un tentativo
               - tries=2: un tentativo + un retry
               - tries=3: un tentativo + due retry
        delay: Secondi di attesa tra i tentativi (default: 0.8)
               Implementa un backoff lineare semplice
    
    Returns:
        Decorator function che può essere applicato a qualsiasi funzione
    
    Esempio d'uso:
        @retry((requests.RequestException,), tries=3, delay=1.0)
        def richiedi_chiavi():
            # Codice che può fallire per problemi di rete
            return requests.get("https://kme.example.com/api/...")
    
    Comportamento:
        1. Esegue la funzione decorata
        2. Se succede, ritorna il risultato
        3. Se fallisce con una delle exceptions specificate:
           - Se non è l'ultimo tentativo: aspetta 'delay' secondi e riprova
           - Se è l'ultimo tentativo: rilancia l'eccezione originale
        4. Se fallisce con un'eccezione non specificata: rilancia immediatamente
    """
    def deco(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            # Ciclo per il numero specificato di tentativi
            for attempt in range(tries):
                try:
                    # Tentativo di esecuzione della funzione
                    return fn(*args, **kwargs)
                    
                except exceptions as e:
                    # Salva l'eccezione per eventuale rilancio finale
                    last_exception = e
                    
                    # Se è l'ultimo tentativo, rilancia l'eccezione
                    if attempt == tries - 1:
                        raise
                    
                    # Altrimenti aspetta prima del prossimo tentativo
                    # Questo previene il sovraccarico dei KME con richieste troppo frequenti
                    time.sleep(delay)
            
            # Fallback (non dovrebbe mai essere raggiunto)
            raise last_exception
        return wrapper
    return deco