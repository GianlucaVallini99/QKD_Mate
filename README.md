# QKD_Mate

Client Python per interrogare i nodi QKD **Alice** e **Bob** via HTTPS mTLS.

## Prerequisiti
- Python 3.10+
- Certificati locali in `certs/`:
  - `ca.crt`
  - `client_Alice2.crt` + `client_Alice2.key`
  - `client_Bob2.crt` + `client_Bob2.key`
- La cartella `certs/` è esclusa da git (.gitignore).

## Setup
```bash
pip install -r requirements.txt
```

Copia i certificati:
```bash
mkdir -p certs
# copia qui i file .crt/.key e proteggi le key:
chmod 600 certs/*.key
```

Verifica/aggiorna gli endpoint in `config/alice.yaml` e `config/bob.yaml`.
Gli alias di API (status, keys) sono definiti in `config/common.yaml`.

## Esempi d'uso

### Stato Alice
```bash
python examples/get_status_alice.py
```

### Stato Bob
```bash
python examples/get_status_bob.py
```

### Richiesta chiavi (esempio POST)
```bash
python examples/fetch_keys.py --node alice --count 1
```

**Nota**: i path `/api/status` e `/api/keys` sono placeholder comuni; sostituiscili con quelli reali del tuo vendor QKD se diversi.

## Troubleshooting

- **certificate verify failed** → controlla `ca.crt` e l'orario di sistema.
- **bad certificate** → certificato/chiave non corrispondono o server non riconosce il tuo client.
- **connection timed out / refused** → IP non abilitato verso 78.40.171.143/.144 sulla 443 oppure firewall.