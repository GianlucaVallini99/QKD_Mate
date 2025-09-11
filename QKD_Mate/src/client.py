import json
import ssl
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
import yaml
from .utils import retry, QKDClientError

def _load_yaml(path: str | Path) -> dict:
    path = Path(path).resolve()  # Convert to absolute path
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out

class QKDClient:
    """
    Client HTTPS mTLS per nodi QKD/KME conforme a ETSI GS QKD 014.
    Config YAML:
      - endpoint: https://IP:443
      - cert, key, ca: path ai file in certs/
      - timeout_sec, retries
      - api_paths: {status: "/api/v1/keys/{slave_id}/status", ...}
    """
    def __init__(self, config_path: str | Path):
        config_path = Path(config_path).resolve()
        cfg = _load_yaml(config_path)
        if "extends" in cfg:
            # Resolve extends path relative to the config file's directory
            extends_path = config_path.parent / cfg["extends"]
            common = _load_yaml(extends_path)
            cfg = _merge(common, {k: v for k, v in cfg.items() if k != "extends"})
        self.base_url: str = cfg["endpoint"].rstrip("/")
        self.cert = (cfg["cert"], cfg["key"])
        self.verify = cfg["ca"]  # CA file
        self.timeout = int(cfg.get("timeout_sec", 10))
        self.retries = int(cfg.get("retries", 2))
        self.api_paths: Dict[str, str] = cfg.get("api_paths", {})

        # Sanity check file paths
        for p in [*self.cert, self.verify]:
            if not Path(p).exists():
                raise QKDClientError(f"File non trovato: {p}")

        # opzionale: verifica hostname
        self.verify_hostname = bool(cfg.get("verify_hostname", True))

    def _url(self, key_or_path: str, **kwargs) -> str:
        """Costruisce URL sostituendo i placeholder come {slave_id}"""
        path = self.api_paths.get(key_or_path, key_or_path)
        # Sostituisce i placeholder nel path
        if kwargs:
            path = path.format(**kwargs)
        return f"{self.base_url}{path}"

    @retry((requests.RequestException,), tries=3, delay=0.8)
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("cert", self.cert)
        kwargs.setdefault("verify", self.verify)
        r = requests.request(method=method, url=url, **kwargs)
        return r

    def _handle(self, r: requests.Response) -> Any:
        """Gestisce la risposta e gli errori secondo ETSI"""
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            # Per errori 400/401/503, prova a estrarre il messaggio JSON
            if r.status_code in [400, 401, 503]:
                try:
                    error_data = r.json()
                    if "message" in error_data:
                        raise QKDClientError(f"HTTP {r.status_code}: {error_data['message']}") from e
                except json.JSONDecodeError:
                    pass
            raise QKDClientError(f"HTTP {r.status_code} su {r.url}: {r.text}") from e
        # Prova JSON, altrimenti testo
        try:
            return r.json()
        except json.JSONDecodeError:
            return r.text

    def get(self, key_or_path: str, params: dict | None = None, **path_kwargs) -> Any:
        """GET generico con supporto per path variables"""
        url = self._url(key_or_path, **path_kwargs)
        r = self._request("GET", url, params=params)
        return self._handle(r)

    def post(self, key_or_path: str, data: dict | None = None, **path_kwargs) -> Any:
        """POST generico con supporto per path variables"""
        url = self._url(key_or_path, **path_kwargs)
        r = self._request("POST", url, json=data or {})
        return self._handle(r)

    # Metodi conformi ETSI GS QKD 014

    def get_status(self, slave_id: str) -> dict:
        """
        GET /api/v1/keys/{slave_id}/status
        Ottiene lo stato del link QKD con lo slave specificato.
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
        Richiede chiavi crittografiche al KME per comunicare con lo slave.
        
        Args:
            slave_id: ID dello slave SAE
            number: Numero di chiavi richieste
            size: Dimensione di ogni chiave in bit (multiplo di 8)
            additional_slave_SAE_IDs: Lista di slave SAE ID aggiuntivi
            extension_mandatory: Estensioni obbligatorie
            extension_optional: Estensioni opzionali
        """
        # Validazione size
        if size is not None and size % 8 != 0:
            raise QKDClientError(f"size deve essere multiplo di 8, ricevuto: {size}")
        
        # Costruisci parametri query
        params = {}
        if number is not None:
            params["number"] = number
        if size is not None:
            params["size"] = size
        if additional_slave_SAE_IDs:
            params["additional_slave_SAE_IDs"] = ",".join(additional_slave_SAE_IDs)
        if extension_mandatory:
            params["extension_mandatory"] = json.dumps(extension_mandatory)
        if extension_optional:
            params["extension_optional"] = json.dumps(extension_optional)
        
        return self.get("enc_keys", params=params if params else None, slave_id=slave_id)

    def get_key_with_ids(self, master_id: str, key_IDs: List[str]) -> dict:
        """
        GET /api/v1/keys/{master_id}/dec_keys
        Richiede chiavi di decrittazione usando gli ID forniti dal master.
        
        Args:
            master_id: ID del master SAE
            key_IDs: Lista di key ID da recuperare
        
        Supporta sia singolo key_ID che lista di key_IDs come da ETSI.
        """
        if not key_IDs:
            raise QKDClientError("Almeno un key_ID è richiesto")
        
        # ETSI supporta sia singolo che multipli key_IDs
        if len(key_IDs) == 1:
            params = {"key_ID": key_IDs[0]}
        else:
            params = {"key_IDs": ",".join(key_IDs)}
        
        return self.get("dec_keys", params=params, master_id=master_id)