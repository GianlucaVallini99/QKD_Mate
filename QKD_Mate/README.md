# QKD_Mate - Quantum Key Distribution Client

Client Python conforme allo standard **ETSI GS QKD 014** per interfacciarsi con dispositivi QKD tramite connessioni HTTPS/mTLS.

## 🔐 Funzionalità

- Verifica stato link QKD tra nodi
- Richiesta chiavi quantistiche (master SAE)
- Recupero chiavi tramite key ID (slave SAE)
- Supporto comunicazioni multicast

## 🏗️ Architettura ETSI

Il sistema implementa l'architettura master/slave definita da ETSI:
- **Master SAE (Alice)**: Richiede chiavi al proprio KME e riceve key_ID
- **Slave SAE (Bob)**: Usa i key_ID per recuperare le stesse chiavi dal proprio KME

```
┌─────────────────┐         HTTPS/mTLS          ┌─────────────────┐
│  Alice (Master) │ ◄──────────────────────────► │   KME Alice     │
│     SAE ID:     │      GET enc_keys            │  78.40.171.143  │
│     Alice2      │      Returns: key + key_ID   │    Port 443     │
└─────────────────┘                              └─────────────────┘
        │                                                  │
        │ key_ID (via classical channel)                  │ QKD Link
        ▼                                                  ▼
┌─────────────────┐         HTTPS/mTLS          ┌─────────────────┐
│   Bob (Slave)   │ ◄──────────────────────────► │    KME Bob      │
│     SAE ID:     │      GET dec_keys            │  78.40.171.144  │
│      Bob2       │      with key_ID             │    Port 443     │
└─────────────────┘                              └─────────────────┘
```

## 📋 Prerequisiti

- Python 3.10 o superiore
- Certificati X.509 per autenticazione mTLS
- Accesso di rete ai KME sulla porta 443

## 🚀 Installazione

### Installazione Automatica (Raccomandato)
```bash
# Clona il repository
git clone https://github.com/[tuo-username]/QKD_Mate.git
cd QKD_Mate

# Installazione automatica con setup guidato
python install.py

# Oppure installazione silenziosa
python install.py --silent
```

### Installazione Manuale
```bash
# Setup automatizzato nel repository
python setup.py

# Gestione certificati semplificata
python cert_manager.py install
```

### Installazione Tradizionale
<details>
<summary>Clicca per vedere i passaggi manuali</summary>

1. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

2. **Prepara la directory dei certificati**
```bash
mkdir -p certs
# Copia i certificati CA specifici per nodo
cp /path/to/ca_alice.crt certs/  # Per Alice
cp /path/to/ca_bob.crt certs/    # Per Bob
# Copia i certificati client
cp /path/to/client_*.crt certs/
cp /path/to/client_*.key certs/
chmod 600 certs/*.key
```

3. **Configura il nodo**
```bash
echo "node_type: alice" > node_config.yaml  # o "bob"
```
</details>

## ⚙️ API Endpoints

### Status - Verifica stato link QKD
```bash
GET /api/v1/keys/{slave_id}/status
```

### Get Key (Master) - Richiesta chiavi
```bash
GET /api/v1/keys/{slave_id}/enc_keys?number={N}&size={S}
```

### Get Key with IDs (Slave) - Recupero chiavi
```bash
GET /api/v1/keys/{master_id}/dec_keys?key_ID={id}
```

## 🔧 Utilizzo

### Node Manager (Raccomandato)
```bash
# Modalità interattiva
python qkd_node_manager.py

# Comandi diretti
python qkd_node_manager.py status      # Verifica stato
python qkd_node_manager.py keys 3      # Richiedi 3 chiavi
python qkd_node_manager.py monitor     # Monitoraggio continuo
python qkd_node_manager.py diagnostic  # Test completo
```

### Strumenti di Installazione e Gestione
```bash
# Setup automatizzato
python setup.py                        # Setup guidato completo
python setup.py --verify               # Verifica installazione

# Gestione certificati
python cert_manager.py install         # Installazione guidata certificati
python cert_manager.py validate        # Validazione certificati
python cert_manager.py fix             # Riparazione automatica
python cert_manager.py backup          # Backup certificati
python cert_manager.py list            # Lista certificati installati

# Installer universale
python install.py                      # Installazione completa sistema
python install.py --silent             # Installazione automatica
python install.py --uninstall          # Disinstallazione
```

### Esempi Python
```python
from src.alice_client import alice_client
from src.bob_client import bob_client

# Alice richiede chiavi
alice = alice_client()
resp = alice.get_key("Bob2", number=1, size=256)
key_id = resp['keys'][0]['key_ID']

# Bob recupera chiavi
bob = bob_client()
resp = bob.get_key_with_ids("Alice2", [key_id])
```

### Script di Esempio
```bash
python examples/fetch_keys.py                    # Flusso completo
python examples/advanced_key_request.py          # Parametri avanzati
```

## 📁 Struttura del Progetto

```
QKD_Mate/
├── config/                     # Configurazioni YAML
├── src/                        # Codice sorgente
├── examples/                   # Script dimostrativi
├── certs/                      # Certificati mTLS (da aggiungere)
├── qkd_node_manager.py         # Gestore nodo unificato
├── node_config.yaml            # Configurazione nodo
└── requirements.txt            # Dipendenze Python
```

## 🔐 Configurazione

### Certificati
1. Copia i certificati nella directory `certs/`
2. Imposta permessi: `chmod 600 certs/*.key`
3. Configura il tipo di nodo in `node_config.yaml`

### Configurazione Nodo
```yaml
# node_config.yaml
node_type: alice  # o "bob"
```

## 🚀 Avvio Rapido

### Per Utenti Principianti
```bash
# Avvio guidato con interfaccia semplificata
python quick_start.py

# Oppure (Windows)
start.bat

# Oppure (Linux/macOS)  
./start.sh
```

### Per Utenti Esperti
```bash
# Avvio diretto del node manager
python qkd_node_manager.py
```

## 🐛 Troubleshooting

### Test Rapido
```bash
python qkd_node_manager.py diagnostic
```

### Errori Comuni
- **HTTP 401**: Verificare certificati e autorizzazioni
- **HTTP 503**: KME non disponibile o senza chiavi
- **Connection refused**: Verificare connettività di rete

### Test Connettività
```bash
nc -zv 78.40.171.143 443  # Test porta KME Alice
nc -zv 78.40.171.144 443  # Test porta KME Bob
```

## 📊 Conformità ETSI GS QKD 014

✅ Implementa tutti gli endpoint standard  
✅ Supporto parametri opzionali e validazione  
✅ Gestione errori conforme alle specifiche  

## 🤝 Contribuire

Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per le linee guida.

## 📄 Licenza

MIT License - vedi `LICENSE` per dettagli.