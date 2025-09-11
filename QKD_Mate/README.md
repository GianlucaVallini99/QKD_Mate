# QKD_Mate - Quantum Key Distribution Node Manager

Sistema di gestione per nodi QKD (Quantum Key Distribution) che permette di monitorare e controllare i nodi quantistici Alice e Bob tramite connessioni HTTPS con autenticazione mTLS (mutual TLS).

## 🔐 Panoramica

QKD_Mate è un client Python progettato per interfacciarsi con dispositivi QKD in ambienti di produzione, conforme allo standard **ETSI GS QKD 014**. Fornisce un'interfaccia unificata per:
- Verificare lo stato dei nodi quantistici
- Monitorare continuamente la disponibilità dei nodi
- Richiedere chiavi quantistiche sicure tramite API conformi ETSI
- Supportare il flusso master/slave per la distribuzione delle chiavi
- Eseguire diagnostica di rete e certificati

## 🏗️ Architettura

Il sistema è progettato per operare in modalità distribuita:
- **Un dispositivo gestisce il nodo Alice** (IP: 78.40.171.143)
- **Un altro dispositivo gestisce il nodo Bob** (IP: 78.40.171.144)

Ogni dispositivo esegue una propria istanza del software configurata per il nodo specifico.

```
┌─────────────────┐         HTTPS/mTLS          ┌─────────────────┐
│  Device Alice   │ ◄──────────────────────────► │   Nodo Alice    │
│  (QKD_Mate)     │         Port 443             │  78.40.171.143  │
└─────────────────┘                              └─────────────────┘

┌─────────────────┐         HTTPS/mTLS          ┌─────────────────┐
│   Device Bob    │ ◄──────────────────────────► │    Nodo Bob     │
│  (QKD_Mate)     │         Port 443             │  78.40.171.144  │
└─────────────────┘                              └─────────────────┘
```

## 🌐 Endpoint API ETSI GS QKD 014

Il sistema implementa i seguenti endpoint conformi allo standard ETSI GS QKD 014:

### Status Endpoint
```
GET /api/v1/keys/{slave_id}/status
```
Verifica lo stato di un SAE slave.

### Encryption Keys Endpoint  
```
POST /api/v1/keys/{slave_id}/enc_keys
```
Richiede chiavi di crittografia da un SAE slave (modalità master).

### Decryption Keys Endpoint
```
GET /api/v1/keys/{master_id}/dec_keys?key_ID={key_id}
POST /api/v1/keys/{master_id}/dec_keys
```
Richiede chiavi di decrittografia usando key_ID specifici (modalità slave).

### Esempi curl

#### 1. Verificare lo stato di Alice (Bob → Alice)
```bash
curl -X GET "https://78.40.171.143:443/api/v1/keys/Alice2/status" \
  --cert certs/client_Bob2.crt \
  --key certs/client_Bob2.key \
  --cacert certs/ca.crt
```

#### 2. Richiedere chiave da Bob (Alice → Bob)
```bash
curl -X POST "https://78.40.171.144:443/api/v1/keys/Bob2/enc_keys" \
  --cert certs/client_Alice2.crt \
  --key certs/client_Alice2.key \
  --cacert certs/ca.crt \
  --header "Content-Type: application/json" \
  --data '{"number": 1, "size": 256}'
```

#### 3. Recuperare chiave con key_ID (Bob → Alice)
```bash
curl -X GET "https://78.40.171.143:443/api/v1/keys/Alice2/dec_keys?key_ID=abc123" \
  --cert certs/client_Bob2.crt \
  --key certs/client_Bob2.key \
  --cacert certs/ca.crt
```

## 📋 Prerequisiti

- Python 3.10 o superiore
- Certificati X.509 per autenticazione mTLS
- Accesso di rete ai nodi QKD sulla porta 443

## 🚀 Installazione

1. **Clona il repository**
```bash
git clone https://github.com/[tuo-username]/QKD_Mate.git
cd QKD_Mate
```

2. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

3. **Prepara la directory dei certificati**
```bash
mkdir -p certs
```

4. **Copia i certificati necessari**

Per il dispositivo che gestisce Alice:
```bash
cp /path/to/ca.crt certs/
cp /path/to/client_Alice2.crt certs/
cp /path/to/client_Alice2.key certs/
chmod 600 certs/client_Alice2.key
```

Per il dispositivo che gestisce Bob:
```bash
cp /path/to/ca.crt certs/
cp /path/to/client_Bob2.crt certs/
cp /path/to/client_Bob2.key certs/
chmod 600 certs/client_Bob2.key
```

## ⚙️ Configurazione

### Metodo 1: File di configurazione (consigliato)

Modifica il file `node_config.yaml`:

```yaml
# Per il dispositivo che gestisce Alice
node_type: alice

# Per il dispositivo che gestisce Bob
node_type: bob
```

### Metodo 2: Modifica diretta del codice

Apri `qkd_node_manager.py` e modifica:

```python
NODE_TYPE = "alice"  # o "bob" per l'altro dispositivo
```

## 🔧 Utilizzo

### API Python ETSI GS QKD 014

Il client fornisce i seguenti metodi conformi allo standard ETSI:

#### `get_status(slave_id: str) -> dict`
Verifica lo stato di un SAE slave.
```python
from src.alice_client import alice_client

client = alice_client()
status = client.get_status("Bob2")  # Alice verifica lo stato di Bob
print(status)
```

#### `get_key(slave_id, number=None, size=None, ...) -> dict`
Richiede chiavi di crittografia da un SAE slave (modalità master).
```python
from src.alice_client import alice_client

client = alice_client()
response = client.get_key("Bob2", number=1, size=256)
key_id = response["key_ID"]  # Salva il key_ID per Bob
print(f"Key ID: {key_id}")
```

#### `get_key_with_ids(master_id: str, key_IDs: list[str]) -> dict`
Richiede chiavi di decrittografia usando key_ID specifici (modalità slave).
```python
from src.bob_client import bob_client

client = bob_client()
keys = client.get_key_with_ids("Alice2", [key_id])  # Bob recupera la chiave
print(keys)
```

### Flusso Master/Slave Completo
```python
# Step 1: Alice (master) richiede chiave da Bob (slave)
alice = alice_client()
resp = alice.get_key("Bob2", number=1, size=256)
key_id = resp["key_ID"]

# Step 2: Bob (slave) recupera la chiave usando key_ID
bob = bob_client()
key_data = bob.get_key_with_ids("Alice2", [key_id])
```

### Modalità Interattiva

Esegui lo script senza parametri per accedere al menu interattivo:

```bash
python qkd_node_manager.py
```

Vedrai un menu come questo:
```
╔════════════════════════════════════════════════════════════╗
║ Gestore Nodo Quantistico QKD -            ALICE             ║
╚════════════════════════════════════════════════════════════╝

============================================================
MENU PRINCIPALE - Nodo ALICE
============================================================
1. Verifica stato nodo
2. Monitoraggio continuo
3. Richiedi chiavi quantistiche
4. Diagnostica completa
5. Esci
============================================================

Seleziona opzione (1-5):
```

### Modalità Comando Diretto

#### 1. Verifica Stato
Controlla se il nodo è attivo e raggiungibile:
```bash
python qkd_node_manager.py status
```

Output esempio:
```
Controllo stato nodo ALICE...
✓ Nodo ALICE ATTIVO
  IP: 78.40.171.143:443
  Tempo risposta: 0.23s
  Risposta: {"status": "operational", "keys_available": 1024}
```

#### 2. Monitoraggio Continuo
Monitora il nodo con controlli periodici:
```bash
# Controllo ogni 30 secondi (default)
python qkd_node_manager.py monitor

# Controllo ogni 10 secondi
python qkd_node_manager.py monitor 10
```

Il monitoraggio mostra:
- Stato in tempo reale
- Statistiche di uptime
- Alert per fallimenti consecutivi
- Diagnostica automatica dopo 5 fallimenti

#### 3. Richiesta Chiavi Quantistiche
Richiedi chiavi sicure dal nodo:
```bash
# Richiedi 1 chiave (default)
python qkd_node_manager.py keys

# Richiedi 10 chiavi
python qkd_node_manager.py keys 10
```

#### 4. Diagnostica Completa
Esegue test approfonditi di sistema:
```bash
python qkd_node_manager.py diagnostic
```

La diagnostica include:
- Verifica presenza certificati
- Test connettività di rete (ping)
- Test porta 443
- Test API con certificati

## 📁 Struttura del Progetto

```
QKD_Mate/
├── qkd_node_manager.py      # Script principale unificato
├── node_config.yaml         # Configurazione nodo (alice/bob)
├── requirements.txt         # Dipendenze Python
├── README.md               # Questa documentazione
├── README_NODE_MANAGER.md  # Guida rapida d'uso
│
├── config/                 # Configurazioni YAML
│   ├── alice.yaml         # Endpoint e settings Alice
│   ├── bob.yaml           # Endpoint e settings Bob
│   └── common.yaml        # Settings comuni
│
├── src/                   # Codice sorgente
│   ├── __init__.py
│   ├── client.py          # Client HTTP base
│   ├── alice_client.py    # Client specifico Alice
│   ├── bob_client.py      # Client specifico Bob
│   └── utils.py           # Utility functions
│
├── examples/              # Script di esempio ETSI GS QKD 014
│   ├── get_status_alice.py    # Bob verifica stato di Alice
│   ├── get_status_bob.py      # Alice verifica stato di Bob  
│   └── fetch_keys.py          # Flusso completo master/slave
│
└── certs/                 # Certificati (non in git)
    ├── ca.crt
    ├── client_Alice2.crt
    ├── client_Alice2.key
    ├── client_Bob2.crt
    └── client_Bob2.key
```

## 🔐 Sicurezza

### Autenticazione mTLS
Il sistema utilizza mutual TLS authentication:
- Il server verifica il certificato del client
- Il client verifica il certificato del server
- Tutte le comunicazioni sono crittografate

### Best Practices
1. **Protezione chiavi private**: Sempre `chmod 600` sulle chiavi
2. **Certificati separati**: Ogni dispositivo ha i propri certificati
3. **No condivisione**: Mai condividere certificati tra dispositivi
4. **Verifica hostname**: Abilitata di default per prevenire MITM

## 🐛 Troubleshooting

### Errori Comuni

#### "certificate verify failed"
- **Causa**: Certificato CA non valido o scaduto
- **Soluzione**: 
  - Verifica la validità del certificato CA
  - Controlla data/ora del sistema
  - Assicurati che `ca.crt` sia corretto

#### "bad certificate"
- **Causa**: Il server non riconosce il certificato client
- **Soluzione**:
  - Verifica di usare il certificato corretto (Alice2/Bob2)
  - Controlla che certificato e chiave corrispondano
  - Verifica che il certificato sia autorizzato sul server

#### "connection refused" o "timeout"
- **Causa**: Problemi di rete o firewall
- **Soluzione**:
  - Verifica connettività: `ping 78.40.171.143` (o .144)
  - Controlla firewall locale e remoto
  - Verifica che la porta 443 sia aperta
  - Testa con: `nc -zv 78.40.171.143 443`

### Diagnostica Avanzata

Usa il comando diagnostic per un'analisi completa:
```bash
python qkd_node_manager.py diagnostic
```

## 🔄 Workflow Tipico

### Setup Iniziale (una volta)
1. Clona repository su entrambi i dispositivi
2. Configura NODE_TYPE per ogni dispositivo
3. Installa certificati appropriati
4. Testa connettività con `status`

### Operazioni Quotidiane
1. Avvia monitoraggio: `python qkd_node_manager.py monitor`
2. Richiedi chiavi quando necessario: `python qkd_node_manager.py keys N`
3. Controlla log per anomalie

### Manutenzione
1. Esegui diagnostica periodica
2. Verifica scadenza certificati
3. Monitora statistiche uptime

## 📊 Metriche e Logging

Il sistema traccia:
- **Uptime**: Percentuale di disponibilità del nodo
- **Latenza**: Tempo di risposta delle API
- **Fallimenti**: Conteggio e pattern dei fallimenti
- **Chiavi**: Numero di chiavi richieste/ricevute

## 🚧 Limitazioni Note

- Supporta solo Python 3.10+
- Richiede certificati X.509 validi
- Opera solo su porta 443
- Un dispositivo può gestire solo un nodo alla volta
- Conforme allo standard ETSI GS QKD 014 v1.1.1

## 📜 Standard ETSI GS QKD 014

Questo progetto implementa le specifiche del documento **ETSI GS QKD 014 v1.1.1 "Quantum Key Distribution (QKD); Protocol and data format of REST-based key delivery API"**.

### Caratteristiche Implementate:
- ✅ Endpoint `/api/v1/keys/{slave_id}/status` per verifica stato
- ✅ Endpoint `/api/v1/keys/{slave_id}/enc_keys` per richiesta chiavi master
- ✅ Endpoint `/api/v1/keys/{master_id}/dec_keys` per recupero chiavi slave
- ✅ Supporto parametri `number`, `size`, `additional_slave_SAE_IDs`
- ✅ Supporto estensioni `extension_mandatory` e `extension_optional`
- ✅ Gestione errori HTTP 400/401/503 con messaggi JSON
- ✅ Validazione `size` multiplo di 8
- ✅ Supporto sia GET (singolo key_ID) che POST (multipli key_IDs)
- ✅ Autenticazione mTLS conforme agli standard di sicurezza

## 🤝 Contribuire

1. Fork il repository
2. Crea un branch: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'Add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Apri una Pull Request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

## 👥 Autori

- Il tuo nome - @GianlucaVallini99

## 🙏 Riconoscimenti

- Basato su standard QKD industriali
- Utilizza best practices per sicurezza mTLS
- Compatibile con dispositivi QKD commerciali
