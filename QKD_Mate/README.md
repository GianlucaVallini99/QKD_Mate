# QKD_Mate - Quantum Key Distribution Client (ETSI GS QKD 014)

Client Python per nodi QKD (Quantum Key Distribution) conforme allo standard **ETSI GS QKD 014** che permette di interfacciarsi con i Key Management Entity (KME) tramite connessioni HTTPS con autenticazione mTLS.

## 🔐 Panoramica

QKD_Mate è un client Python progettato per interfacciarsi con dispositivi QKD secondo lo standard ETSI GS QKD 014. Fornisce un'interfaccia completa per:
- Verificare lo stato dei link QKD tra nodi
- Richiedere chiavi quantistiche sicure (master SAE)
- Recuperare chiavi usando key ID (slave SAE)
- Supportare comunicazioni multicast con multiple SAE

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
# Copia i certificati forniti
cp /path/to/ca.crt certs/
cp /path/to/client_*.crt certs/
cp /path/to/client_*.key certs/
chmod 600 certs/*.key
```

## ⚙️ API Endpoints (ETSI GS QKD 014)

### 1. Status - Verifica stato link QKD
```
GET /api/v1/keys/{slave_id}/status
```

**Esempio cURL:**
```bash
curl -X GET https://78.40.171.143:443/api/v1/keys/Bob2/status \
  --cert certs/client_Alice2.crt \
  --key certs/client_Alice2.key \
  --cacert certs/ca.crt
```

**Risposta:**
```json
{
  "source_KME_ID": "KME_Alice",
  "target_KME_ID": "KME_Bob",
  "master_SAE_ID": "Alice2",
  "slave_SAE_ID": "Bob2",
  "key_size": 256,
  "stored_key_count": 1024,
  "max_key_count": 10000,
  "max_key_per_request": 100,
  "max_key_size": 1024,
  "min_key_size": 64,
  "max_SAE_ID_count": 10
}
```

### 2. Get Key (Master) - Richiesta chiavi
```
GET /api/v1/keys/{slave_id}/enc_keys?number={N}&size={S}
```

**Parametri:**
- `number`: Numero di chiavi richieste
- `size`: Dimensione in bit (multiplo di 8)
- `additional_slave_SAE_IDs`: Lista di SAE ID aggiuntivi (opzionale)

**Esempio cURL:**
```bash
curl -X GET "https://78.40.171.143:443/api/v1/keys/Bob2/enc_keys?number=1&size=256" \
  --cert certs/client_Alice2.crt \
  --key certs/client_Alice2.key \
  --cacert certs/ca.crt
```

**Risposta:**
```json
{
  "keys": [
    {
      "key_ID": "550e8400-e29b-41d4-a716-446655440000",
      "key": "A1B2C3D4E5F6..."
    }
  ]
}
```

### 3. Get Key with IDs (Slave) - Recupero chiavi
```
GET /api/v1/keys/{master_id}/dec_keys?key_ID={id}
GET /api/v1/keys/{master_id}/dec_keys?key_IDs={id1},{id2},...
```

**Esempio cURL:**
```bash
curl -X GET "https://78.40.171.144:443/api/v1/keys/Alice2/dec_keys?key_ID=550e8400-e29b-41d4-a716-446655440000" \
  --cert certs/client_Bob2.crt \
  --key certs/client_Bob2.key \
  --cacert certs/ca.crt
```

## 🔧 Utilizzo del Client Python

### Esempio Base - Flusso Completo

```python
from src.alice_client import alice_client
from src.bob_client import bob_client

# 1. Alice (master) richiede una chiave
alice = alice_client()
resp = alice.get_key("Bob2", number=1, size=256)
key_id = resp['keys'][0]['key_ID']
print(f"Alice riceve key_ID: {key_id}")

# 2. Alice comunica key_ID a Bob (canale classico)

# 3. Bob (slave) recupera la chiave
bob = bob_client()
resp = bob.get_key_with_ids("Alice2", [key_id])
print(f"Bob recupera la chiave con ID: {key_id}")
```

### Script di Esempio

#### Status del Link
```bash
# Bob verifica status del link con Alice
python examples/get_status_alice.py

# Alice verifica status del link con Bob  
python examples/get_status_bob.py
```

#### Scambio Chiavi Completo
```bash
# Esempio completo master/slave
python examples/fetch_keys.py

# Solo master (Alice richiede chiavi)
python examples/fetch_keys.py --mode master --number 3 --size 512

# Solo slave (Bob recupera con key_IDs)
python examples/fetch_keys.py --mode slave --key-ids "id1" "id2" "id3"
```

#### Richieste Avanzate
```bash
# Esempi con parametri opzionali ETSI
python examples/advanced_key_request.py
```

## 📁 Struttura del Progetto

```
QKD_Mate/
├── config/                     # Configurazioni
│   ├── common.yaml            # API paths ETSI
│   ├── alice.yaml             # Config Alice (78.40.171.143)
│   └── bob.yaml               # Config Bob (78.40.171.144)
│
├── src/                       # Codice sorgente
│   ├── client.py              # Client ETSI GS QKD 014
│   ├── alice_client.py        # Helper Alice
│   ├── bob_client.py          # Helper Bob
│   └── utils.py               # Utilities
│
├── examples/                  # Script dimostrativi
│   ├── get_status_alice.py    # Status link Bob→Alice
│   ├── get_status_bob.py      # Status link Alice→Bob
│   ├── fetch_keys.py          # Flusso master/slave
│   └── advanced_key_request.py # Funzionalità avanzate
│
├── certs/                     # Certificati mTLS
│   ├── ca.crt                 # Certificate Authority
│   ├── client_Alice2.crt/key  # Certificati Alice
│   └── client_Bob2.crt/key    # Certificati Bob
│
├── requirements.txt           # Dipendenze Python
└── README.md                  # Questa documentazione
```

## 🔐 Sicurezza

### Autenticazione mTLS
- Ogni SAE ha certificati univoci (Alice2, Bob2)
- Tutte le comunicazioni su HTTPS porta 443
- Verifica bidirezionale dei certificati

### Best Practices
1. **Protezione chiavi private**: `chmod 600` su tutti i file `.key`
2. **Validazione parametri**: `size` deve essere multiplo di 8
3. **Gestione errori**: Il client gestisce errori 400/401/503 secondo ETSI
4. **Key ID sicuri**: Comunicare key_ID solo su canale autenticato

## 🐛 Troubleshooting

### Errori Comuni

#### HTTP 400 - Bad Request
- **Causa**: Parametri non validi (es. size non multiplo di 8)
- **Soluzione**: Verificare i parametri della richiesta

#### HTTP 401 - Unauthorized  
- **Causa**: Certificato client non valido o non autorizzato
- **Soluzione**: Verificare certificati e autorizzazioni sul KME

#### HTTP 503 - Service Unavailable
- **Causa**: KME temporaneamente non disponibile o senza chiavi
- **Soluzione**: Riprovare più tardi o verificare stato link QKD

### Test di Connettività

```bash
# Test porta 443
nc -zv 78.40.171.143 443

# Test con OpenSSL
openssl s_client -connect 78.40.171.143:443 \
  -cert certs/client_Alice2.crt \
  -key certs/client_Alice2.key \
  -CAfile certs/ca.crt
```

## 📊 Conformità ETSI GS QKD 014

Questo client implementa:
- ✅ Status API (GET /api/v1/keys/{slave_id}/status)
- ✅ Enc Keys API per master (GET /api/v1/keys/{slave_id}/enc_keys)
- ✅ Dec Keys API per slave (GET /api/v1/keys/{master_id}/dec_keys)
- ✅ Supporto key_ID singolo e multipli
- ✅ Parametri opzionali (additional_slave_SAE_IDs, extensions)
- ✅ Validazione size multiplo di 8
- ✅ Gestione errori standard (400/401/503)

## 🤝 Contribuire

1. Fork il repository
2. Crea branch: `git checkout -b feature/nuova-funzionalita`
3. Commit: `git commit -m 'Aggiunge nuova funzionalità'`
4. Push: `git push origin feature/nuova-funzionalita`
5. Apri Pull Request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per dettagli.

## 🙏 Riconoscimenti

- Conforme a ETSI GS QKD 014 V1.1.1 (2019-02)
- Compatibile con dispositivi QKD commerciali
- Utilizza best practices per sicurezza mTLS