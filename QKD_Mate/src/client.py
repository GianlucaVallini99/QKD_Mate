import json
import ssl
from pathlib import Path
from typing import Any, Dict

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
    Client HTTPS mTLS per nodi QKD/KME.
    Config YAML:
      - endpoint: https://IP:443
      - cert, key, ca: path ai file in certs/
      - timeout_sec, retries
      - api_paths: {status: "/api/status", keys: "/api/keys"}
    """
    def __init__(self, config_path: str | Path):
        config_path = Path(config_path).resolve()
        cfg = _load_yaml(config_path)
        if "extends" in cfg:
            # Resolve extends path relative to the config file's directory
            extends_path = config_path.parent / cfg["extends"]
            common = _load_yaml(extends_path)
            cfg = _merge(common, {k: v for k, v in cfg.items() if k != "extends"})
        self.base_url: str = cfg.get("base_url", cfg.get("endpoint", "")).rstrip("/")
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

    def _url(self, key_or_path: str) -> str:
        path = self.api_paths.get(key_or_path, key_or_path)
        return f"{self.base_url}{path}"

    @retry((requests.RequestException,), tries=3, delay=0.8)
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("cert", self.cert)
        kwargs.setdefault("verify", self.verify)
        r = requests.request(method=method, url=url, **kwargs)
        return r

    def _handle(self, r: requests.Response) -> Any:
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            # Handle specific error codes as per ETSI GS QKD 014
            if r.status_code in [400, 401, 503]:
                try:
                    error_data = r.json()
                    if "message" in error_data:
                        print(f"Error {r.status_code}: {error_data['message']}")
                    raise QKDClientError(f"HTTP {r.status_code}: {error_data}")
                except json.JSONDecodeError:
                    raise QKDClientError(f"HTTP {r.status_code} su {r.url}: {r.text}") from e
            else:
                raise QKDClientError(f"HTTP {r.status_code} su {r.url}: {r.text}") from e
        # Prova JSON, altrimenti testo
        try:
            return r.json()
        except json.JSONDecodeError:
            return r.text

    def get(self, key_or_path: str, params: dict | None = None) -> Any:
        url = self._url(key_or_path)
        r = self._request("GET", url, params=params)
        return self._handle(r)

    def post(self, key_or_path: str, data: dict | None = None) -> Any:
        url = self._url(key_or_path)
        r = self._request("POST", url, json=data or {})
        return self._handle(r)

    # ETSI GS QKD 014 compliant methods
    def get_status(self, slave_id: str) -> dict:
        """
        Get status of a slave SAE according to ETSI GS QKD 014.
        
        Args:
            slave_id: ID of the slave SAE to query status for
            
        Returns:
            dict: Status response from the QKD node
        """
        path = self.api_paths["status"].format(slave_id=slave_id)
        url = f"{self.base_url}{path}"
        r = self._request("GET", url)
        return self._handle(r)
    
    def get_key(self, slave_id: str, number: int = None, size: int = None,
                additional_slave_SAE_IDs: list[str] = None,
                extension_mandatory: dict = None,
                extension_optional: dict = None) -> dict:
        """
        Request encryption keys from slave SAE according to ETSI GS QKD 014.
        
        Args:
            slave_id: ID of the slave SAE
            number: Number of keys to request (optional)
            size: Size of each key in bits (must be multiple of 8)
            additional_slave_SAE_IDs: List of additional slave SAE IDs (optional)
            extension_mandatory: Mandatory extensions (optional)
            extension_optional: Optional extensions (optional)
            
        Returns:
            dict: Response containing key_ID and other metadata
            
        Raises:
            QKDClientError: If size is not multiple of 8 or other validation errors
        """
        # Validate size parameter
        if size is not None and size % 8 != 0:
            raise QKDClientError(f"Size must be multiple of 8, got {size}")
            
        path = self.api_paths["enc_keys"].format(slave_id=slave_id)
        url = f"{self.base_url}{path}"
        
        # Build request parameters
        params = {}
        if number is not None:
            params["number"] = number
        if size is not None:
            params["size"] = size
        if additional_slave_SAE_IDs is not None:
            params["additional_slave_SAE_IDs"] = additional_slave_SAE_IDs
        if extension_mandatory is not None:
            params["extension_mandatory"] = extension_mandatory
        if extension_optional is not None:
            params["extension_optional"] = extension_optional
            
        r = self._request("POST", url, json=params if params else {})
        return self._handle(r)
    
    def get_key_with_ids(self, master_id: str, key_IDs: list[str]) -> dict:
        """
        Request decryption keys using specific key IDs according to ETSI GS QKD 014.
        This method supports both single key_ID (GET) and multiple key_IDs (POST).
        
        Args:
            master_id: ID of the master SAE
            key_IDs: List of key IDs to request (can be single element)
            
        Returns:
            dict: Response containing the requested keys
        """
        path = self.api_paths["dec_keys"].format(master_id=master_id)
        url = f"{self.base_url}{path}"
        
        if len(key_IDs) == 1:
            # Single key_ID: use GET with query parameter
            params = {"key_ID": key_IDs[0]}
            r = self._request("GET", url, params=params)
        else:
            # Multiple key_IDs: use POST with JSON body
            data = {"key_IDs": key_IDs}
            r = self._request("POST", url, json=data)
            
        return self._handle(r)