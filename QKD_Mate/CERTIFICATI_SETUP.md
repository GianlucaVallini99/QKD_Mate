# 🔐 Setup Certificati QKD - Guida Completa

## 📋 Panoramica

Il sistema QKD richiede certificati mTLS (mutual TLS) per l'autenticazione sicura tra i client (Alice/Bob) e i KME (Key Management Entity). Questa guida spiega come configurare i certificati in diverse situazioni.

## 🎯 Soluzioni Rapide

### ✅ SITUAZIONE: Directory `certs/` Non Esiste

**SOLUZIONE AUTOMATICA**: I certificati di test sono già stati creati! 

```bash
cd /workspace/QKD_Mate
ls -la certs/
```

Dovresti vedere:
```
-rw-r--r-- 1 user user 1277 ca.crt                 # Certificate Authority
-rw------- 1 user user 1704 ca.key                 # CA private key  
-rw-r--r-- 1 user user 1253 client_Alice2.crt      # Certificato Alice
-rw------- 1 user user 1704 client_Alice2.key      # Chiave privata Alice
-rw-r--r-- 1 user user 1249 client_Bob2.crt        # Certificato Bob
-rw------- 1 user user 1704 client_Bob2.key        # Chiave privata Bob
```

### 🧪 Test Immediato

```bash
cd /workspace/QKD_Mate

# Test Alice
python -c "
from src.alice_client import alice_client
try:
    alice = alice_client()
    print('✅ Alice client configurato correttamente!')
except Exception as e:
    print(f'❌ Errore Alice: {e}')
"

# Test Bob  
python -c "
from src.bob_client import bob_client
try:
    bob = bob_client()
    print('✅ Bob client configurato correttamente!')
except Exception as e:
    print(f'❌ Errore Bob: {e}')
"
```

## 🏗️ Tipi di Certificati

### 1. 🧪 Certificati di Test (AUTO-FIRMATI)
**✅ GIÀ CONFIGURATI** - Perfetti per sviluppo e test locali

- **Vantaggi**: Immediati, funzionano offline
- **Limitazioni**: Non validi per produzione, non riconosciuti da KME reali
- **Uso**: Test, sviluppo, simulazioni

### 2. 🏢 Certificati di Produzione (DA OTTENERE)
**❗ RICHIESTI PER KME REALI**

- **Fonte**: Forniti dall'operatore QKD (es: TIM, Vodafone)
- **Validità**: Riconosciuti dai KME su 78.40.171.143/144
- **Sicurezza**: Certificati reali firmati da CA autorizzate

## 🔧 Configurazioni per Scenari Diversi

### 🌐 Scenario 1: Test con KME Reali

Se hai **certificati reali** forniti dall'operatore:

```bash
cd /workspace/QKD_Mate/certs

# Backup certificati di test
mkdir -p ../backup_test_certs
mv * ../backup_test_certs/

# Copia certificati reali
cp /path/to/real/ca.crt .
cp /path/to/real/client_Alice2.crt .
cp /path/to/real/client_Alice2.key .
cp /path/to/real/client_Bob2.crt .
cp /path/to/real/client_Bob2.key .

# Imposta permessi corretti
chmod 644 *.crt
chmod 600 *.key
```

### 🏠 Scenario 2: Test Locale/Simulazione

**✅ CONFIGURAZIONE ATTUALE** - Usa i certificati auto-firmati già creati.

### 🔄 Scenario 3: KME Simulato Locale

Per testare con un KME simulato locale, modifica gli endpoint:

```yaml
# config/alice.yaml
extends: "common.yaml"
endpoint: "https://localhost:8443"  # KME simulato
cert: "certs/client_Alice2.crt"
key:  "certs/client_Alice2.key"
ca:   "certs/ca.crt"
```

## 🛠️ Risoluzione Problemi

### ❌ Errore: "File certificato non trovato"

```bash
# Verifica esistenza
ls -la /workspace/QKD_Mate/certs/

# Se mancante, ricrea:
cd /workspace/QKD_Mate
mkdir -p certs
chmod 700 certs
# ... poi rigenera certificati (vedi sezione successiva)
```

### ❌ Errore: "Certificate verify failed"

```bash
# Verifica validità certificati
cd /workspace/QKD_Mate/certs
openssl verify -CAfile ca.crt client_Alice2.crt
openssl verify -CAfile ca.crt client_Bob2.crt

# Controlla scadenza
openssl x509 -in client_Alice2.crt -noout -dates
openssl x509 -in client_Bob2.crt -noout -dates
```

### ❌ Errore: "Connection refused" 

```bash
# Test connettività KME
curl -k --cert certs/client_Alice2.crt \
     --key certs/client_Alice2.key \
     --cacert certs/ca.crt \
     https://78.40.171.143:443/api/v1/keys/Bob2/status

# Se fallisce: KME non raggiungibile o certificati non autorizzati
```

## 🔨 Rigenerare Certificati di Test

Se hai bisogno di rigenerare i certificati auto-firmati:

```bash
cd /workspace/QKD_Mate/certs

# Pulisci certificati esistenti
rm -f *

# Genera nuova CA
openssl genrsa -out ca.key 2048
openssl req -new -x509 -key ca.key -sha256 \
    -subj "/C=IT/ST=Italy/L=Rome/O=QKD_Test/CN=QKD-CA" \
    -days 3650 -out ca.crt

# Genera certificati client
for client in Alice2 Bob2; do
    openssl genrsa -out client_${client}.key 2048
    openssl req -new -key client_${client}.key \
        -subj "/C=IT/ST=Italy/L=Rome/O=QKD_Test/CN=${client}" \
        -out client_${client}.csr
    openssl x509 -req -in client_${client}.csr \
        -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out client_${client}.crt -days 365 -sha256
    rm client_${client}.csr
done

# Imposta permessi
chmod 600 *.key
chmod 644 *.crt
```

## 📁 Struttura Finale

```
QKD_Mate/
├── certs/                     # ✅ CREATA
│   ├── ca.crt                 # Certificate Authority
│   ├── ca.key                 # CA private key (per rigenerazioni)
│   ├── client_Alice2.crt      # Certificato Alice
│   ├── client_Alice2.key      # Chiave privata Alice  
│   ├── client_Bob2.crt        # Certificato Bob
│   └── client_Bob2.key        # Chiave privata Bob
├── config/
│   ├── alice.yaml             # ✅ Punta a certs/
│   ├── bob.yaml               # ✅ Punta a certs/
│   └── common.yaml
└── src/
    ├── alice_client.py        # ✅ Funziona con certificati
    └── bob_client.py          # ✅ Funziona con certificati
```

## 🎯 Prossimi Passi

1. **✅ COMPLETATO**: Certificati di test configurati
2. **🧪 Test Locale**: Usa gli esempi in `examples/`
3. **📞 Per Produzione**: Contatta l'operatore QKD per certificati reali
4. **🔄 Per Simulazione**: Configura KME simulato locale

## 🆘 Supporto

- **Documentazione**: `README.md`, `Procedura.md`
- **Esempi**: Directory `examples/`
- **Sicurezza**: `SECURITY.md`
- **Troubleshooting**: Questa guida, sezione "Risoluzione Problemi"

---

**🎉 CONGRATULAZIONI!** I tuoi certificati sono pronti. Ora puoi connetterti ad Alice e Bob per i test QKD!