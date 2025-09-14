"""
Client QKD conforme a ETSI GS QKD 014 - Core Implementation
==========================================================

Questo modulo implementa il client principale per comunicare con i KME
(Key Management Entity) secondo lo standard ETSI GS QKD 014.

Il client gestisce:
- Comunicazioni HTTPS con autenticazione mTLS (mutual TLS)
- Tutti gli endpoint API standard ETSI
- Gestione errori e retry automatici
- Validazione parametri secondo specifiche
- Configurazione flessibile tramite file YAML

Standard implementato:
- ETSI GS QKD 014 V1.1.1 (2019-02)
- Quantum Key Distribution (QKD); Protocol and data format of REST-based key delivery API
"""

import json
import ssl
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
import yaml
from .utils import retry, QKDClientError

def _load_yaml(path: str | Path) -> dict:
    """
    Carica un file YAML in modo sicuro.
    
    Args:
        path: Percorso al file YAML (stringa o Path object)
    
    Returns:
        dict: Contenuto del file YAML come dizionario
    
    Note:
        - Converte automaticamente il path in assoluto
        - Usa yaml.safe_load per sicurezza
        - Ritorna dizionario vuoto se il file è vuoto
    """
    path = Path(path).resolve()  # Convert to absolute path
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _merge(base: dict, override: dict) -> dict:
    """
    Merge ricorsivo di due dizionari.
    
    Questa funzione implementa il sistema di ereditarietà delle configurazioni
    YAML, permettendo ai file di configurazione di estendere altri file
    (es: alice.yaml extends common.yaml).
    
    Args:
        base: Dizionario base (es: configurazione comune)
        override: Dizionario che sovrascrive (es: configurazione specifica)
    
    Returns:
        dict: Dizionario merged con priorità ai valori di override
    
    Comportamento:
        - Valori semplici: override vince sempre
        - Dizionari annidati: merge ricorsivo
        - Liste: override sostituisce completamente base
    
    Esempio:
        base = {"timeout": 10, "api": {"version": "v1", "host": "default"}}
        override = {"api": {"host": "custom"}}
        result = {"timeout": 10, "api": {"version": "v1", "host": "custom"}}
    """
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            # Merge ricorsivo per dizionari annidati
            out[k] = _merge(out[k], v)
        else:
            # Sostituzione diretta per valori semplici
            out[k] = v
    return out

class QKDClient:
    """
    Client HTTPS mTLS per nodi QKD/KME conforme a ETSI GS QKD 014.
    
    Questa classe implementa un client completo per comunicare con i KME
    (Key Management Entity) secondo lo standard ETSI GS QKD 014.
    
    Caratteristiche principali:
    - Autenticazione mTLS (mutual TLS) con certificati X.509
    - Supporto completo per tutti gli endpoint ETSI
    - Retry automatico per robustezza
    - Gestione errori standardizzata
    - Configurazione flessibile tramite YAML
    - Validazione parametri secondo specifiche ETSI
    
    Configurazione YAML richiesta:
      - endpoint: URL del KME (es: https://78.40.171.143:443)
      - cert: Percorso al certificato client (.crt)
      - key: Percorso alla chiave privata (.key)
      - ca: Percorso al certificato CA (.crt)
      - timeout_sec: Timeout richieste HTTP (default: 10)
      - retries: Numero di retry (default: 2)
      - api_paths: Mapping degli endpoint API
    
    Endpoint supportati (ETSI GS QKD 014):
      - GET /api/v1/keys/{slave_id}/status
      - GET /api/v1/keys/{slave_id}/enc_keys
      - GET /api/v1/keys/{master_id}/dec_keys
    
    Esempio:
        client = QKDClient("config/alice.yaml")
        status = client.get_status("Bob2")
        keys = client.get_key("Bob2", number=1, size=256)
    """
    def __init__(self, config_path: str | Path):
        """
        Inizializza il client QKD con la configurazione specificata.
        
        Args:
            config_path: Percorso al file di configurazione YAML
        
        Raises:
            QKDClientError: Se i file di certificato non esistono
            FileNotFoundError: Se il file di configurazione non esiste
            yaml.YAMLError: Se il file YAML è malformato
        
        Il processo di inizializzazione:
        1. Carica la configurazione dal file YAML
        2. Gestisce l'ereditarietà (extends) se presente
        3. Valida l'esistenza dei certificati
        4. Configura i parametri di connessione
        """
        # Risolvi il percorso assoluto del file di configurazione
        config_path = Path(config_path).resolve()
        
        # Carica la configurazione principale
        cfg = _load_yaml(config_path)
        
        # Gestione dell'ereditarietà (extends)
        if "extends" in cfg:
            # Risolvi il path del file esteso relativamente al file corrente
            extends_path = config_path.parent / cfg["extends"]
            common = _load_yaml(extends_path)
            
            # Merge delle configurazioni: common + specifica
            # Rimuovi 'extends' dalla configurazione prima del merge
            specific_cfg = {k: v for k, v in cfg.items() if k != "extends"}
            cfg = _merge(common, specific_cfg)
        
        # Estrai e valida i parametri di configurazione
        self.base_url: str = cfg["endpoint"].rstrip("/")
        self.cert = (cfg["cert"], cfg["key"])  # Tupla (cert_file, key_file)
        self.verify = cfg["ca"]  # File CA per verifica server
        self.timeout = int(cfg.get("timeout_sec", 10))  # Timeout HTTP
        self.retries = int(cfg.get("retries", 2))  # Numero retry
        self.api_paths: Dict[str, str] = cfg.get("api_paths", {})  # Mapping API

        # Verifica esistenza file certificati (critico per mTLS)
        for cert_file in [*self.cert, self.verify]:
            if not Path(cert_file).exists():
                raise QKDClientError(
                    f"File certificato non trovato: {cert_file}\n"
                    f"Assicurati che tutti i certificati siano presenti nella directory certs/"
                )

        # Configurazione opzionale per verifica hostname SSL
        self.verify_hostname = bool(cfg.get("verify_hostname", True))

    def _url(self, key_or_path: str, **kwargs) -> str:
        """
        Costruisce l'URL completo per una richiesta API.
        
        Questo metodo implementa un sistema flessibile per costruire URL:
        1. Se key_or_path è una chiave in api_paths, usa il template corrispondente
        2. Altrimenti usa key_or_path come path diretto
        3. Sostituisce i placeholder nel path con i parametri forniti
        
        Args:
            key_or_path: Chiave API (es: "status") o path diretto (es: "/api/v1/test")
            **kwargs: Parametri per sostituire i placeholder (es: slave_id="Bob2")
        
        Returns:
            str: URL completo pronto per la richiesta HTTP
        
        Esempio:
            # Con chiave API
            url = self._url("status", slave_id="Bob2")
            # Risultato: "https://kme.example.com/api/v1/keys/Bob2/status"
            
            # Con path diretto
            url = self._url("/custom/endpoint")
            # Risultato: "https://kme.example.com/custom/endpoint"
        """
        # Ottieni il template del path dalla configurazione o usa il valore diretto
        path = self.api_paths.get(key_or_path, key_or_path)
        
        # Sostituisci i placeholder nel path (es: {slave_id} -> "Bob2")
        if kwargs:
            path = path.format(**kwargs)
            
        # Costruisci l'URL completo
        return f"{self.base_url}{path}"

    @retry((requests.RequestException,), tries=3, delay=0.8)
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Esegue una richiesta HTTP con retry automatico e configurazione mTLS.
        
        Questo metodo è il cuore delle comunicazioni con i KME:
        - Configura automaticamente mTLS con i certificati
        - Applica timeout configurato
        - Usa retry automatico per robustezza
        
        Args:
            method: Metodo HTTP ("GET", "POST", etc.)
            url: URL completo della richiesta
            **kwargs: Parametri aggiuntivi per requests
        
        Returns:
            requests.Response: Risposta HTTP grezza
        
        Note:
            - Il decorator @retry gestisce automaticamente i fallimenti temporanei
            - mTLS è configurato automaticamente con cert/key/ca
            - Il timeout previene richieste bloccate indefinitamente
        """
        # Configura parametri default se non già specificati
        kwargs.setdefault("timeout", self.timeout)  # Timeout HTTP
        kwargs.setdefault("cert", self.cert)        # Certificato client (mTLS)
        kwargs.setdefault("verify", self.verify)    # CA per verifica server
        
        # Esegui la richiesta HTTP
        # Il decorator @retry gestirà eventuali eccezioni di rete
        r = requests.request(method=method, url=url, **kwargs)
        return r

    def _handle(self, r: requests.Response) -> Any:
        """
        Gestisce la risposta HTTP e gli errori secondo lo standard ETSI.
        
        Questo metodo implementa la gestione standardizzata degli errori
        definita in ETSI GS QKD 014, con particolare attenzione ai codici
        di errore specifici del protocollo QKD.
        
        Args:
            r: Risposta HTTP da processare
        
        Returns:
            Any: Dati della risposta (JSON parsato o testo)
        
        Raises:
            QKDClientError: Per tutti gli errori HTTP con dettagli specifici
        
        Codici di errore ETSI gestiti:
            - 400 Bad Request: Parametri non validi (es: size non multiplo di 8)
            - 401 Unauthorized: Certificato non valido o non autorizzato
            - 503 Service Unavailable: KME temporaneamente non disponibile
        """
        try:
            # Controlla se la risposta è un successo (2xx)
            r.raise_for_status()
        except requests.HTTPError as e:
            # Gestione specifica per errori ETSI standard
            if r.status_code in [400, 401, 503]:
                try:
                    # Tenta di estrarre il messaggio di errore dal JSON
                    error_data = r.json()
                    if "message" in error_data:
                        raise QKDClientError(
                            f"HTTP {r.status_code}: {error_data['message']}"
                        ) from e
                except json.JSONDecodeError:
                    # Se il JSON non è valido, continua con gestione generica
                    pass
            
            # Gestione generica per tutti gli altri errori HTTP
            raise QKDClientError(
                f"HTTP {r.status_code} su {r.url}: {r.text}"
            ) from e
        
        # Parsing della risposta di successo
        try:
            # La maggior parte delle risposte ETSI sono in formato JSON
            return r.json()
        except json.JSONDecodeError:
            # Fallback per risposte in formato testo
            return r.text

    def get(self, key_or_path: str, params: dict | None = None, **path_kwargs) -> Any:
        """
        Esegue una richiesta GET generica con supporto per path variables.
        
        Questo metodo è un wrapper di convenienza per richieste GET che:
        1. Costruisce l'URL con i parametri del path
        2. Esegue la richiesta con retry automatico
        3. Gestisce la risposta secondo standard ETSI
        
        Args:
            key_or_path: Chiave API o path diretto
            params: Parametri query string (opzionali)
            **path_kwargs: Parametri per sostituire placeholder nell'URL
        
        Returns:
            Any: Dati della risposta parsati
        
        Esempio:
            # GET /api/v1/keys/Bob2/status
            response = client.get("status", slave_id="Bob2")
            
            # GET /api/v1/keys/Bob2/enc_keys?number=1&size=256
            response = client.get("enc_keys", 
                                params={"number": 1, "size": 256},
                                slave_id="Bob2")
        """
        # Costruisci URL con path parameters
        url = self._url(key_or_path, **path_kwargs)
        
        # Esegui richiesta GET con parametri query
        r = self._request("GET", url, params=params)
        
        # Gestisci risposta ed errori
        return self._handle(r)

    def post(self, key_or_path: str, data: dict | None = None, **path_kwargs) -> Any:
        """
        Esegue una richiesta POST generica con supporto per path variables.
        
        Questo metodo è un wrapper di convenienza per richieste POST che:
        1. Costruisce l'URL con i parametri del path
        2. Serializza i dati in JSON
        3. Esegue la richiesta con retry automatico
        4. Gestisce la risposta secondo standard ETSI
        
        Args:
            key_or_path: Chiave API o path diretto
            data: Dati da inviare nel body (serializzati in JSON)
            **path_kwargs: Parametri per sostituire placeholder nell'URL
        
        Returns:
            Any: Dati della risposta parsati
        
        Note:
            - I dati vengono automaticamente serializzati in JSON
            - Content-Type viene impostato automaticamente a application/json
            - Se data è None, viene inviato un oggetto JSON vuoto {}
        
        Esempio:
            # POST /api/v1/custom/endpoint
            response = client.post("custom_endpoint", 
                                 data={"parameter": "value"})
        """
        # Costruisci URL con path parameters
        url = self._url(key_or_path, **path_kwargs)
        
        # Esegui richiesta POST con dati JSON
        r = self._request("POST", url, json=data or {})
        
        # Gestisci risposta ed errori
        return self._handle(r)

    # =================================================================
    # Metodi conformi ETSI GS QKD 014 - Implementazione Standard
    # =================================================================

    def get_status(self, slave_id: str) -> dict:
        """
        GET /api/v1/keys/{slave_id}/status
        
        Ottiene informazioni sullo stato del link QKD con lo slave specificato.
        Questo endpoint è utilizzato per verificare la disponibilità e le
        caratteristiche del collegamento quantistico.
        
        Args:
            slave_id: Identificatore dello slave SAE (es: "Bob2")
        
        Returns:
            dict: Informazioni sullo stato del link contenenti:
                - source_KME_ID: ID del KME sorgente
                - target_KME_ID: ID del KME destinazione
                - master_SAE_ID: ID del master SAE
                - slave_SAE_ID: ID dello slave SAE
                - key_size: Dimensione standard delle chiavi in bit
                - stored_key_count: Numero di chiavi attualmente disponibili
                - max_key_count: Capacità massima di chiavi
                - max_key_per_request: Numero massimo di chiavi per richiesta
                - max_key_size: Dimensione massima supportata per le chiavi
                - min_key_size: Dimensione minima supportata per le chiavi
                - max_SAE_ID_count: Numero massimo di SAE supportati
        
        Raises:
            QKDClientError: Se il slave_id non è valido o il link non esiste
        
        Esempio:
            status = client.get_status("Bob2")
            print(f"Chiavi disponibili: {status['stored_key_count']}")
            print(f"Dimensione chiavi: {status['key_size']} bit")
        
        Uso tipico:
            - Verificare se un link QKD è attivo prima di richiedere chiavi
            - Monitorare la disponibilità di chiavi quantistiche
            - Ottenere limiti operativi per ottimizzare le richieste
        """
        return self.get("status", slave_id=slave_id)

    def get_key(self, slave_id: str, 
                number: Optional[int] = None,
                size: Optional[int] = None,
                additional_slave_SAE_IDs: Optional[List[str]] = None,
                extension_mandatory: Optional[dict] = None,
                extension_optional: Optional[dict] = None) -> dict:
        """
        GET /api/v1/keys/{slave_id}/enc_keys
        
        Richiede chiavi quantistiche al KME per comunicare con lo slave specificato.
        Questo è il metodo principale per i nodi MASTER che vogliono ottenere
        chiavi quantistiche fresche per comunicazioni sicure.
        
        IMPORTANTE: Solo i nodi MASTER possono utilizzare questo endpoint.
        I nodi SLAVE devono usare get_key_with_ids() con i key_ID ricevuti.
        
        Args:
            slave_id: ID dello slave SAE con cui comunicare (es: "Bob2")
            number: Numero di chiavi richieste (default: 1)
                   Limitato da max_key_per_request ottenuto da get_status()
            size: Dimensione di ogni chiave in bit (default: dal KME)
                 DEVE essere multiplo di 8 secondo ETSI
                 Limitato da min_key_size e max_key_size
            additional_slave_SAE_IDs: Lista di SAE ID aggiuntivi per multicast
                                    Permette di richiedere la stessa chiave
                                    per comunicare con più slave contemporaneamente
            extension_mandatory: Estensioni obbligatorie definite dall'implementazione
            extension_optional: Estensioni opzionali definite dall'implementazione
        
        Returns:
            dict: Risposta contenente:
                - keys: Lista di oggetti chiave, ognuno con:
                  - key_ID: Identificatore univoco della chiave (UUID)
                  - key: Chiave quantistica in formato esadecimale
        
        Raises:
            QKDClientError: 
                - Se size non è multiplo di 8
                - Se number supera max_key_per_request
                - Se size è fuori dai limiti min/max
                - Se non ci sono chiavi disponibili (HTTP 503)
                - Se slave_id non è valido (HTTP 400)
        
        Esempio:
            # Richiesta base
            response = alice.get_key("Bob2")
            key_id = response['keys'][0]['key_ID']
            key = response['keys'][0]['key']
            
            # Richiesta multipla con dimensione specifica
            response = alice.get_key("Bob2", number=3, size=512)
            for i, key_data in enumerate(response['keys']):
                print(f"Chiave {i+1}: ID={key_data['key_ID']}")
            
            # Multicast (stessa chiave per più slave)
            response = alice.get_key("Bob2", 
                                   additional_slave_SAE_IDs=["Charlie2", "Dave2"])
        
        Flusso tipico:
            1. Alice chiama get_key("Bob2") 
            2. Riceve chiave + key_ID
            3. Alice comunica key_ID a Bob tramite canale classico
            4. Bob usa get_key_with_ids() per ottenere la stessa chiave
        """
        # Validazione rigorosa della dimensione secondo ETSI
        if size is not None and size % 8 != 0:
            raise QKDClientError(
                f"Parametro 'size' deve essere multiplo di 8 secondo ETSI GS QKD 014. "
                f"Valore ricevuto: {size}"
            )
        
        # Costruisci parametri query per la richiesta
        params = {}
        
        # Parametri numerici opzionali
        if number is not None:
            params["number"] = number
        if size is not None:
            params["size"] = size
            
        # Gestione multicast - lista di slave aggiuntivi
        if additional_slave_SAE_IDs:
            params["additional_slave_SAE_IDs"] = ",".join(additional_slave_SAE_IDs)
            
        # Estensioni personalizzate (serializzate in JSON)
        if extension_mandatory:
            params["extension_mandatory"] = json.dumps(extension_mandatory)
        if extension_optional:
            params["extension_optional"] = json.dumps(extension_optional)
        
        # Esegui la richiesta con i parametri costruiti
        return self.get("enc_keys", params=params if params else None, slave_id=slave_id)

    def get_key_with_ids(self, master_id: str, key_IDs: List[str]) -> dict:
        """
        GET /api/v1/keys/{master_id}/dec_keys
        
        Recupera chiavi quantistiche usando gli ID forniti dal master.
        Questo è il metodo principale per i nodi SLAVE che vogliono ottenere
        le chiavi corrispondenti ai key_ID ricevuti dal master.
        
        IMPORTANTE: Solo i nodi SLAVE possono utilizzare questo endpoint.
        I nodi MASTER devono usare get_key() per richiedere nuove chiavi.
        
        Args:
            master_id: ID del master SAE che ha generato le chiavi (es: "Alice2")
            key_IDs: Lista di identificatori chiave ricevuti dal master
                    Ogni key_ID è un UUID univoco generato dal KME del master
        
        Returns:
            dict: Risposta contenente:
                - keys: Lista di oggetti chiave, ognuno con:
                  - key_ID: L'identificatore fornito nella richiesta
                  - key: La chiave quantistica corrispondente (identica a quella del master)
        
        Raises:
            QKDClientError:
                - Se key_IDs è vuoto
                - Se uno o più key_ID non esistono (HTTP 400)
                - Se il master_id non è valido
                - Se le chiavi sono già state consumate
        
        Formati supportati (ETSI):
            - Singolo key_ID: ?key_ID=uuid
            - Multipli key_IDs: ?key_IDs=uuid1,uuid2,uuid3
        
        Esempio:
            # Recupero singola chiave
            key_id = "550e8400-e29b-41d4-a716-446655440000"  # Da Alice
            response = bob.get_key_with_ids("Alice2", [key_id])
            key = response['keys'][0]['key']
            
            # Recupero multiple chiavi
            key_ids = ["uuid1", "uuid2", "uuid3"]  # Da Alice
            response = bob.get_key_with_ids("Alice2", key_ids)
            for key_data in response['keys']:
                print(f"Chiave {key_data['key_ID']}: {key_data['key']}")
        
        Flusso tipico:
            1. Alice chiama get_key() e ottiene chiave + key_ID
            2. Alice comunica key_ID a Bob (canale classico sicuro)
            3. Bob chiama get_key_with_ids() con il key_ID ricevuto
            4. Bob ottiene la stessa identica chiave di Alice
            5. Alice e Bob possono ora comunicare con la chiave condivisa
        
        Note di sicurezza:
            - I key_ID possono essere trasmessi su canali non quantistici
            - Le chiavi sono consumate dopo il recupero (one-time use)
            - La sicurezza dipende dall'autenticità del canale per i key_ID
        """
        # Validazione input
        if not key_IDs:
            raise QKDClientError(
                "Almeno un key_ID è richiesto per recuperare le chiavi. "
                "I key_ID devono essere forniti dal nodo master."
            )
        
        # ETSI supporta due formati per i parametri query
        if len(key_IDs) == 1:
            # Formato singolo: ?key_ID=uuid
            params = {"key_ID": key_IDs[0]}
        else:
            # Formato multiplo: ?key_IDs=uuid1,uuid2,uuid3
            params = {"key_IDs": ",".join(key_IDs)}
        
        # Esegui la richiesta al KME
        return self.get("dec_keys", params=params, master_id=master_id)