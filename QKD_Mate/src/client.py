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