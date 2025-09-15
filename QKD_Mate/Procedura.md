# 🔐 Procedura Completa per Implementazione QKD_Mate

## 📋 Guida Esaustiva per Collegare Alice e Bob e Scambiare Chiavi Quantistiche

### 🎯 Obiettivo
Questa guida fornisce una procedura dettagliata per implementare un sistema di comunicazione quantisticamente sicuro usando QKD_Mate, dalla configurazione iniziale all'integrazione in applicazioni reali come sistemi di messaggistica.

---

## 📚 Indice

1. [Prerequisiti e Teoria](#1-prerequisiti-e-teoria)
2. [Architettura del Sistema](#2-architettura-del-sistema)
3. [Configurazione Ambiente](#3-configurazione-ambiente)
4. [Deployment Alice (Master)](#4-deployment-alice-master)
5. [Deployment Bob (Slave)](#5-deployment-bob-slave)
6. [Test di Connettività](#6-test-di-connettività)
7. [Scambio Chiavi Quantistiche](#7-scambio-chiavi-quantistiche)
8. [Integrazione in App di Messaggistica](#8-integrazione-in-app-di-messaggistica)
9. [Monitoraggio e Manutenzione](#9-monitoraggio-e-manutenzione)
10. [Troubleshooting](#10-troubleshooting)
11. [Sicurezza e Best Practices](#11-sicurezza-e-best-practices)

---

## 1. 📖 Prerequisiti e Teoria

### 1.1 Concetti Fondamentali

**Quantum Key Distribution (QKD)** è una tecnologia che sfrutta le proprietà della meccanica quantistica per distribuire chiavi crittografiche con sicurezza teoricamente assoluta.

#### Componenti del Sistema:
- **Alice (Master SAE)**: Nodo che inizia le richieste di chiavi
- **Bob (Slave SAE)**: Nodo che recupera chiavi usando key_ID
- **KME (Key Management Entity)**: Server che gestisce le chiavi quantistiche
- **Link Quantistico**: Collegamento fisico tra i KME per generazione chiavi

#### Protocollo ETSI GS QKD 014:
```
┌─────────────┐    HTTPS/mTLS     ┌─────────────┐
│ Alice (SAE) │ ◄─────────────────► │  KME Alice  │
│ 10.0.0.100  │  Richiede chiavi   │78.40.171.143│
└─────────────┘                     └─────────────┘
      │                                     │
      │ key_ID (canale classico)            │ QKD Link
      ▼                                     ▼
┌─────────────┐    HTTPS/mTLS     ┌─────────────┐
│  Bob (SAE)  │ ◄─────────────────► │  KME Bob    │
│ 10.0.0.200  │  Recupera chiavi   │78.40.171.144│
└─────────────┘                     └─────────────┘
```

### 1.2 Requisiti Tecnici

#### Hardware:
- **2 dispositivi separati** (Alice e Bob)
- **CPU**: x86_64, ARM64 supportato
- **RAM**: Minimo 1GB, raccomandato 2GB
- **Storage**: 500MB liberi per certificati e log
- **Rete**: Connessione internet stabile, porte 443 aperte

#### Software:
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Python**: 3.10 o superiore
- **Librerie**: requests, PyYAML (automatiche con requirements.txt)

#### Certificati X.509:
- **ca.crt**: Certificate Authority comune
- **client_Alice2.crt/key**: Certificati per Alice
- **client_Bob2.crt/key**: Certificati per Bob

---

## 2. 🏗️ Architettura del Sistema

### 2.1 Topologia di Rete

```
Internet
   │
   ├── Alice Device (10.0.0.100)
   │   ├── QKD_Mate Client
   │   ├── Certificati Alice
   │   └── App Messaggistica
   │
   ├── Bob Device (10.0.0.200)
   │   ├── QKD_Mate Client  
   │   ├── Certificati Bob
   │   └── App Messaggistica
   │
   ├── KME Alice (78.40.171.143:443)
   │   ├── Gestione chiavi quantistiche
   │   └── API ETSI GS QKD 014
   │
   └── KME Bob (78.40.171.144:443)
       ├── Gestione chiavi quantistiche
       └── Collegamento quantistico con KME Alice
```

### 2.2 Flusso di Comunicazione

1. **Generazione Automatica**: I KME generano chiavi quantistiche tramite il link fisico
2. **Richiesta Master**: Alice richiede chiavi al suo KME specificando Bob come destinatario
3. **Risposta con Key_ID**: Il KME di Alice fornisce chiavi + identificatori univoci
4. **Comunicazione Classica**: Alice comunica i key_ID a Bob via canale normale
5. **Recupero Slave**: Bob usa i key_ID per ottenere le stesse chiavi dal suo KME
6. **Utilizzo Sicuro**: Alice e Bob usano le chiavi per crittografia end-to-end

---

## 3. ⚙️ Configurazione Ambiente

### 3.1 Preparazione Sistema Alice

#### 🐧 Linux (Ubuntu/Debian)

```bash
# ===== DISPOSITIVO ALICE - LINUX =====

# 1. Aggiornamento sistema
sudo apt update && sudo apt upgrade -y

# 2. Installazione Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# 3. Installazione tools di rete
sudo apt install curl netcat-openbsd openssl -y

# 4. Creazione utente dedicato (opzionale ma raccomandato)
sudo useradd -m -s /bin/bash qkd-alice
sudo usermod -aG sudo qkd-alice

# 5. Configurazione firewall
sudo ufw allow ssh
sudo ufw allow out 443/tcp  # Per comunicazioni con KME
sudo ufw --force enable
```

#### 🪟 Windows 10/11

```powershell
# ===== DISPOSITIVO ALICE - WINDOWS =====

# 1. Installazione Python 3.10+ (se non già presente)
# Scaricare da https://www.python.org/downloads/windows/
# Assicurarsi di spuntare "Add Python to PATH" durante l'installazione

# 2. Verifica installazione Python
python --version
pip --version

# 3. Installazione Git (se necessario)
# Scaricare da https://git-scm.com/download/win

# 4. Configurazione Windows Defender Firewall
# Aprire Windows Defender Firewall con sicurezza avanzata
# Creare regola in uscita per porta 443 (HTTPS)
New-NetFirewallRule -DisplayName "QKD HTTPS Out" -Direction Outbound -Protocol TCP -LocalPort 443 -Action Allow

# 5. Installazione OpenSSL (opzionale, per test certificati)
# Scaricare da https://slproweb.com/products/Win32OpenSSL.html
# Oppure usare tramite Git Bash che include OpenSSL

# 6. Creazione directory di lavoro
mkdir C:\QKD_Mate
cd C:\QKD_Mate
```

#### 🍎 macOS

```bash
# ===== DISPOSITIVO ALICE - macOS =====

# 1. Installazione Homebrew (se non già presente)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Installazione Python 3.10+ (se non già presente)
brew install python@3.10

# 3. Installazione tools di rete
brew install curl netcat openssl

# 4. Verifica installazione
python3 --version
pip3 --version

# 5. Configurazione firewall (opzionale)
# Su macOS il firewall è gestito tramite Preferenze di Sistema > Sicurezza e Privacy > Firewall
# Permettere connessioni in uscita per Python

# 6. Creazione directory di lavoro
sudo mkdir -p /opt/QKD_Mate
sudo chown $(whoami):staff /opt/QKD_Mate
```

### 3.2 Preparazione Sistema Bob

#### 🐧 Linux (Ubuntu/Debian)

```bash
# ===== DISPOSITIVO BOB - LINUX =====

# 1. Aggiornamento sistema
sudo apt update && sudo apt upgrade -y

# 2. Installazione Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# 3. Installazione tools di rete
sudo apt install curl netcat-openbsd openssl -y

# 4. Creazione utente dedicato (opzionale ma raccomandato)
sudo useradd -m -s /bin/bash qkd-bob
sudo usermod -aG sudo qkd-bob

# 5. Configurazione firewall
sudo ufw allow ssh
sudo ufw allow out 443/tcp  # Per comunicazioni con KME
sudo ufw --force enable
```

#### 🪟 Windows 10/11

```powershell
# ===== DISPOSITIVO BOB - WINDOWS =====

# 1. Installazione Python 3.10+ (se non già presente)
# Scaricare da https://www.python.org/downloads/windows/
# Assicurarsi di spuntare "Add Python to PATH" durante l'installazione

# 2. Verifica installazione Python
python --version
pip --version

# 3. Installazione Git (se necessario)
# Scaricare da https://git-scm.com/download/win

# 4. Configurazione Windows Defender Firewall
New-NetFirewallRule -DisplayName "QKD HTTPS Out" -Direction Outbound -Protocol TCP -LocalPort 443 -Action Allow

# 5. Creazione directory di lavoro
mkdir C:\QKD_Mate
cd C:\QKD_Mate
```

#### 🍎 macOS

```bash
# ===== DISPOSITIVO BOB - macOS =====

# 1. Installazione Homebrew (se non già presente)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Installazione Python 3.10+
brew install python@3.10

# 3. Installazione tools di rete
brew install curl netcat openssl

# 4. Verifica installazione
python3 --version
pip3 --version

# 5. Creazione directory di lavoro
sudo mkdir -p /opt/QKD_Mate
sudo chown $(whoami):staff /opt/QKD_Mate
```

### 3.3 Download e Setup QKD_Mate

#### 🐧 Linux & 🍎 macOS

```bash
# 1. Download del progetto
cd /opt  # Su macOS: cd /opt
sudo git clone https://github.com/[your-repo]/QKD_Mate.git
sudo chown -R $USER:$USER QKD_Mate  # Su macOS: sudo chown -R $(whoami):staff QKD_Mate
cd QKD_Mate

# 2. Creazione ambiente virtuale Python
python3 -m venv venv
source venv/bin/activate

# 3. Installazione dipendenze
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verifica installazione
python -c "import requests, yaml; print('✓ Dipendenze installate correttamente')"

# 5. Creazione directory certificati
mkdir -p certs
chmod 700 certs  # Solo proprietario può accedere
```

#### 🪟 Windows

```powershell
# 1. Download del progetto
cd C:\
git clone https://github.com/[your-repo]/QKD_Mate.git
cd QKD_Mate

# 2. Creazione ambiente virtuale Python
python -m venv venv
venv\Scripts\activate

# 3. Installazione dipendenze
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Verifica installazione
python -c "import requests, yaml; print('✓ Dipendenze installate correttamente')"

# 5. Creazione directory certificati
mkdir certs
# Su Windows, i permessi sono gestiti tramite proprietà cartella
# Tasto destro su cartella certs > Proprietà > Sicurezza > Avanzate
# Rimuovere tutti gli utenti eccetto il proprietario
```

#### 📝 Note Cross-Platform

**Percorsi predefiniti:**
- **Linux/macOS**: `/opt/QKD_Mate`
- **Windows**: `C:\QKD_Mate`

**Attivazione ambiente virtuale:**
- **Linux/macOS**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`

**Comando Python:**
- **Linux/macOS**: `python3` (o `python` se alias configurato)
- **Windows**: `python`

**Gestione certificati:**
- **Linux/macOS**: Usare `chmod` per permessi
- **Windows**: Usare Proprietà > Sicurezza per ACL

---

## 4. 🔑 Deployment Alice (Master)

### 4.1 Configurazione Certificati Alice

#### 🐧 Linux & 🍎 macOS

```bash
# ===== SU DISPOSITIVO ALICE - LINUX/macOS =====
cd /opt/QKD_Mate

# 1. Copia certificati Alice (ricevuti dall'amministratore KME)
# IMPORTANTE: Sostituisci con i tuoi certificati reali
sudo cp /path/to/received/ca.crt certs/
sudo cp /path/to/received/client_Alice2.crt certs/
sudo cp /path/to/received/client_Alice2.key certs/

# 2. Impostazione permessi sicuri
sudo chown $USER:$USER certs/*  # macOS: sudo chown $(whoami):staff certs/*
chmod 644 certs/ca.crt
chmod 644 certs/client_Alice2.crt
chmod 600 certs/client_Alice2.key  # CRITICO: solo proprietario

# 3. Verifica certificati
openssl x509 -in certs/client_Alice2.crt -text -noout | grep "Subject:"
openssl x509 -in certs/ca.crt -text -noout | grep "Subject:"

# 4. Test validità certificati
openssl verify -CAfile certs/ca.crt certs/client_Alice2.crt
```

#### 🪟 Windows

```powershell
# ===== SU DISPOSITIVO ALICE - WINDOWS =====
cd C:\QKD_Mate

# 1. Copia certificati Alice (ricevuti dall'amministratore KME)
# IMPORTANTE: Sostituisci con i tuoi certificati reali
copy "C:\path\to\received\ca.crt" certs\
copy "C:\path\to\received\client_Alice2.crt" certs\
copy "C:\path\to\received\client_Alice2.key" certs\

# 2. Impostazione permessi sicuri (tramite PowerShell con ACL)
# Rimuovi accesso per tutti gli utenti eccetto il proprietario
$acl = Get-Acl "certs\client_Alice2.key"
$acl.SetAccessRuleProtection($true, $false)
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
$acl.SetAccessRule($accessRule)
Set-Acl "certs\client_Alice2.key" $acl

# 3. Verifica certificati (se OpenSSL installato)
# Tramite Git Bash o OpenSSL per Windows:
openssl x509 -in certs/client_Alice2.crt -text -noout | findstr "Subject:"
openssl x509 -in certs/ca.crt -text -noout | findstr "Subject:"

# 4. Test validità certificati
openssl verify -CAfile certs/ca.crt certs/client_Alice2.crt

# Alternative: Verifica tramite PowerShell (senza OpenSSL)
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("certs\client_Alice2.crt")
$cert.Subject
$cert.NotAfter  # Data scadenza
```

### 4.2 Configurazione Node Manager per Alice

```bash
# 1. Configurazione tramite file YAML (metodo raccomandato)
cat > node_config.yaml << 'EOF'
# Configurazione Nodo Alice (Master SAE)
node_type: alice

# Configurazioni opzionali
monitoring:
  default_interval: 30
  alert_after_failures: 3

diagnostics:
  run_ping_test: true
  run_port_test: true
  ping_timeout: 2
EOF

# 2. Test configurazione
python qkd_node_manager.py --help
```

### 4.3 Test Connettività Alice

#### 🐧 Linux & 🍎 macOS

```bash
# 1. Test connessione di rete al KME
ping -c 3 78.40.171.143

# 2. Test porta 443
nc -zv 78.40.171.143 443

# 3. Test SSL handshake base
echo | openssl s_client -connect 78.40.171.143:443 -verify_return_error

# 4. Test completo con QKD_Mate
python3 qkd_node_manager.py diagnostic

# 5. Test status link
python3 qkd_node_manager.py status
```

#### 🪟 Windows

```powershell
# 1. Test connessione di rete al KME
ping -n 3 78.40.171.143

# 2. Test porta 443
# PowerShell equivalente di netcat:
Test-NetConnection -ComputerName 78.40.171.143 -Port 443

# 3. Test SSL handshake base (se OpenSSL installato)
echo | openssl s_client -connect 78.40.171.143:443 -verify_return_error

# Alternative PowerShell per test SSL:
$tcpClient = New-Object System.Net.Sockets.TcpClient
$tcpClient.Connect("78.40.171.143", 443)
$sslStream = New-Object System.Net.Security.SslStream($tcpClient.GetStream())
$sslStream.AuthenticateAsClient("78.40.171.143")
Write-Host "SSL connection successful"
$sslStream.Close()
$tcpClient.Close()

# 4. Test completo con QKD_Mate
python qkd_node_manager.py diagnostic

# 5. Test status link
python qkd_node_manager.py status
```

---

## 5. 🔄 Deployment Bob (Slave)

### 5.1 Configurazione Certificati Bob

#### 🐧 Linux & 🍎 macOS

```bash
# ===== SU DISPOSITIVO BOB - LINUX/macOS =====
cd /opt/QKD_Mate

# 1. Copia certificati Bob (ricevuti dall'amministratore KME)
sudo cp /path/to/received/ca.crt certs/
sudo cp /path/to/received/client_Bob2.crt certs/
sudo cp /path/to/received/client_Bob2.key certs/

# 2. Impostazione permessi sicuri
sudo chown $USER:$USER certs/*  # macOS: sudo chown $(whoami):staff certs/*
chmod 644 certs/ca.crt
chmod 644 certs/client_Bob2.crt
chmod 600 certs/client_Bob2.key  # CRITICO: solo proprietario

# 3. Verifica certificati
openssl x509 -in certs/client_Bob2.crt -text -noout | grep "Subject:"
openssl verify -CAfile certs/ca.crt certs/client_Bob2.crt
```

#### 🪟 Windows

```powershell
# ===== SU DISPOSITIVO BOB - WINDOWS =====
cd C:\QKD_Mate

# 1. Copia certificati Bob (ricevuti dall'amministratore KME)
copy "C:\path\to\received\ca.crt" certs\
copy "C:\path\to\received\client_Bob2.crt" certs\
copy "C:\path\to\received\client_Bob2.key" certs\

# 2. Impostazione permessi sicuri (tramite PowerShell con ACL)
$acl = Get-Acl "certs\client_Bob2.key"
$acl.SetAccessRuleProtection($true, $false)
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
$acl.SetAccessRule($accessRule)
Set-Acl "certs\client_Bob2.key" $acl

# 3. Verifica certificati
# Tramite Git Bash o OpenSSL per Windows:
openssl x509 -in certs/client_Bob2.crt -text -noout | findstr "Subject:"
openssl verify -CAfile certs/ca.crt certs/client_Bob2.crt

# Alternative PowerShell:
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("certs\client_Bob2.crt")
$cert.Subject
$cert.NotAfter
```

### 5.2 Configurazione Node Manager per Bob

```bash
# 1. Configurazione tramite file YAML
cat > node_config.yaml << 'EOF'
# Configurazione Nodo Bob (Slave SAE)
node_type: bob

# Configurazioni opzionali
monitoring:
  default_interval: 30
  alert_after_failures: 3

diagnostics:
  run_ping_test: true
  run_port_test: true
  ping_timeout: 2
EOF
```

### 5.3 Test Connettività Bob

#### 🐧 Linux & 🍎 macOS

```bash
# 1. Test connessione di rete al KME
ping -c 3 78.40.171.144

# 2. Test porta 443
nc -zv 78.40.171.144 443

# 3. Test completo con QKD_Mate
python3 qkd_node_manager.py diagnostic

# 4. Test status link con Alice
python3 qkd_node_manager.py status
```

#### 🪟 Windows

```powershell
# 1. Test connessione di rete al KME
ping -n 3 78.40.171.144

# 2. Test porta 443
Test-NetConnection -ComputerName 78.40.171.144 -Port 443

# 3. Test completo con QKD_Mate
python qkd_node_manager.py diagnostic

# 4. Test status link con Alice
python qkd_node_manager.py status
```

---

## 6. 🔍 Test di Connettività

### 6.1 Verifica Bidirezionale

**Su Alice:**
```bash
# Test che Alice veda Bob
python examples/get_status_bob.py
```

**Su Bob:**
```bash
# Test che Bob veda Alice
python examples/get_status_alice.py
```

### 6.2 Interpretazione Risultati Status

**Risposta tipica di successo:**
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

**Indicatori di Salute:**
- ✅ `stored_key_count > 0`: Chiavi disponibili
- ✅ `stored_key_count / max_key_count > 0.2`: Buffer sano
- ⚠️ `stored_key_count < 10`: Buffer basso
- ❌ `stored_key_count = 0`: Link quantistico inattivo

---

## 7. 🔐 Scambio Chiavi Quantistiche

### 7.1 Flusso Completo Manuale

#### Step 1: Alice Richiede Chiavi

**Su Alice:**
```bash
# Richiesta singola chiave
python qkd_node_manager.py keys 1

# Richiesta multipla (più efficiente)
python qkd_node_manager.py keys 5

# Usando script diretto
python examples/fetch_keys.py --mode master --number 3 --size 256
```

**Output atteso:**
```
✓ 3 chiavi ricevute con successo
   Chiave 1: ID=550e8400-e29b-41d4-a716-446655440000
            Chiave=A1B2C3D4E5F6...
   Chiave 2: ID=6ba7b810-9dad-11d1-80b4-00c04fd430c8
            Chiave=F6E5D4C3B2A1...
   Chiave 3: ID=6ba7b811-9dad-11d1-80b4-00c04fd430c8
            Chiave=1A2B3C4D5E6F...

💡 PROSSIMO PASSO:
   Comunica questi key_ID a Bob tramite canale sicuro:
   - 550e8400-e29b-41d4-a716-446655440000
   - 6ba7b810-9dad-11d1-80b4-00c04fd430c8
   - 6ba7b811-9dad-11d1-80b4-00c04fd430c8
```

#### Step 2: Comunicazione Key_ID (Canale Classico)

I key_ID possono essere trasmessi tramite canali normali (email, SMS, chat) poiché da soli non rivelano le chiavi. **IMPORTANTE**: Il canale deve essere autenticato per evitare attacchi man-in-the-middle.

**Metodi sicuri:**
- Email firmata digitalmente
- Messaggio autenticato su app sicura
- Chiamata vocale con verifica identità
- Sistema di messaggistica aziendale

#### Step 3: Bob Recupera le Chiavi

**Su Bob:**
```bash
# Recupero tramite node manager (modalità interattiva)
python qkd_node_manager.py
# Scegli opzione 3, inserisci key_ID separati da virgola

# Recupero diretto con script
python examples/fetch_keys.py --mode slave --key-ids \
  "550e8400-e29b-41d4-a716-446655440000" \
  "6ba7b810-9dad-11d1-80b4-00c04fd430c8" \
  "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
```

**Output atteso:**
```
✓ 3 chiavi recuperate con successo
   Chiave 1: ID=550e8400-e29b-41d4-a716-446655440000
            Chiave=A1B2C3D4E5F6...
   Chiave 2: ID=6ba7b810-9dad-11d1-80b4-00c04fd430c8
            Chiave=F6E5D4C3B2A1...
   Chiave 3: ID=6ba7b811-9dad-11d1-80b4-00c04fd430c8
            Chiave=1A2B3C4D5E6F...
```

### 7.2 Script Automatizzato Completo

**Esempio completo con verifica:**
```bash
# Su Alice e Bob simultaneamente
python examples/fetch_keys.py --mode full --number 1 --size 256
```

Questo script dimostra il flusso completo ma richiede entrambi i certificati sulla stessa macchina (solo per test).

### 7.3 Programmazione dello Scambio

**Script Python per automazione:**
```python
#!/usr/bin/env python3
"""
Script di automazione scambio chiavi QKD
"""
from src.alice_client import alice_client
from src.bob_client import bob_client
import json
import time

def scambio_automatico_alice(num_keys=1):
    """Alice richiede chiavi e salva key_IDs"""
    alice = alice_client()
    
    # Richiedi chiavi
    response = alice.get_key("Bob2", number=num_keys, size=256)
    
    # Estrai key_IDs
    key_ids = [key['key_ID'] for key in response['keys']]
    
    # Salva per comunicazione a Bob
    with open('key_ids.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'key_ids': key_ids,
            'keys': response['keys']
        }, f)
    
    print(f"✓ {len(key_ids)} chiavi generate")
    print(f"✓ Key_IDs salvati in key_ids.json")
    return key_ids

def scambio_automatico_bob():
    """Bob legge key_IDs e recupera chiavi"""
    bob = bob_client()
    
    # Leggi key_IDs (simulazione ricezione da Alice)
    with open('key_ids.json', 'r') as f:
        data = json.load(f)
    
    key_ids = data['key_ids']
    
    # Recupera chiavi
    response = bob.get_key_with_ids("Alice2", key_ids)
    
    print(f"✓ {len(response['keys'])} chiavi recuperate")
    return response['keys']

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "alice":
        scambio_automatico_alice(3)
    elif len(sys.argv) > 1 and sys.argv[1] == "bob":
        scambio_automatico_bob()
    else:
        print("Uso: python script.py [alice|bob]")
```

---

## 8. 📱 Integrazione in App di Messaggistica

### 8.1 Architettura di Integrazione

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   App Alice     │    │   QKD_Mate      │    │   KME Alice     │
│                 │    │   Client        │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Chat UI     │◄┼────┤►│ QKD Manager │◄┼────┤►│ Key Store   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Crypto      │◄┼────┤►│ Key Buffer  │ │    │ │ QKD Engine  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 8.2 Implementazione Classe QKDManager

**File: `qkd_messaging_manager.py`**
```python
#!/usr/bin/env python3
"""
QKD Manager per Applicazioni di Messaggistica
"""
import threading
import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from src.alice_client import alice_client
from src.bob_client import bob_client
from src.utils import QKDClientError

class QKDMessagingManager:
    """
    Manager per integrare QKD in applicazioni di messaggistica.
    
    Funzionalità:
    - Buffer automatico di chiavi quantistiche
    - Rotazione chiavi per Perfect Forward Secrecy
    - Gestione automatica richieste/recuperi
    - API semplice per applicazioni
    """
    
    def __init__(self, node_type: str, partner_id: str, min_keys: int = 10):
        """
        Inizializza il manager QKD.
        
        Args:
            node_type: "alice" o "bob"
            partner_id: ID del partner ("Alice2" o "Bob2")
            min_keys: Numero minimo di chiavi nel buffer
        """
        self.node_type = node_type.lower()
        self.partner_id = partner_id
        self.min_keys = min_keys
        
        # Buffer chiavi locali
        self.key_buffer: List[Dict] = []
        self.used_key_ids: set = set()
        
        # Client QKD
        if self.node_type == "alice":
            self.client = alice_client()
            self.is_master = True
        elif self.node_type == "bob":
            self.client = bob_client()
            self.is_master = False
        else:
            raise ValueError("node_type deve essere 'alice' o 'bob'")
        
        # Thread per mantenimento buffer
        self._running = False
        self._buffer_thread = None
        
        # Lock per thread safety
        self._lock = threading.Lock()
        
        print(f"✓ QKDMessagingManager inizializzato per {node_type}")
    
    def start(self):
        """Avvia il manager e il thread di mantenimento buffer."""
        self._running = True
        self._buffer_thread = threading.Thread(target=self._maintain_buffer)
        self._buffer_thread.daemon = True
        self._buffer_thread.start()
        print("✓ QKD Manager avviato")
    
    def stop(self):
        """Ferma il manager."""
        self._running = False
        if self._buffer_thread:
            self._buffer_thread.join(timeout=5)
        print("✓ QKD Manager fermato")
    
    def _maintain_buffer(self):
        """Thread per mantenere il buffer di chiavi sempre pieno."""
        while self._running:
            try:
                with self._lock:
                    current_keys = len(self.key_buffer)
                
                if current_keys < self.min_keys:
                    needed = self.min_keys - current_keys
                    print(f"🔄 Buffer basso ({current_keys}/{self.min_keys}), richiedo {needed} chiavi")
                    
                    if self.is_master:
                        self._request_new_keys(needed)
                    else:
                        print("⚠️ Bob non può richiedere chiavi autonomamente")
                
                time.sleep(30)  # Controlla ogni 30 secondi
                
            except Exception as e:
                print(f"❌ Errore mantenimento buffer: {e}")
                time.sleep(60)  # Attendi di più in caso di errore
    
    def _request_new_keys(self, count: int):
        """Richiede nuove chiavi (solo Alice)."""
        try:
            response = self.client.get_key(self.partner_id, number=count, size=256)
            
            with self._lock:
                for key_data in response.get('keys', []):
                    if key_data['key_ID'] not in self.used_key_ids:
                        self.key_buffer.append({
                            'key_id': key_data['key_ID'],
                            'key': key_data['key'],
                            'timestamp': time.time(),
                            'used': False
                        })
            
            print(f"✓ {len(response.get('keys', []))} nuove chiavi aggiunte al buffer")
            
        except QKDClientError as e:
            print(f"❌ Errore richiesta chiavi: {e}")
    
    def add_keys_from_partner(self, key_ids: List[str]):
        """
        Aggiunge chiavi al buffer usando key_ID ricevuti dal partner (solo Bob).
        
        Args:
            key_ids: Lista di key_ID ricevuti da Alice
        """
        if self.is_master:
            print("⚠️ Alice non dovrebbe usare questa funzione")
            return
        
        try:
            response = self.client.get_key_with_ids(self.partner_id, key_ids)
            
            with self._lock:
                for key_data in response.get('keys', []):
                    if key_data['key_ID'] not in self.used_key_ids:
                        self.key_buffer.append({
                            'key_id': key_data['key_ID'],
                            'key': key_data['key'],
                            'timestamp': time.time(),
                            'used': False
                        })
            
            print(f"✓ {len(response.get('keys', []))} chiavi recuperate e aggiunte al buffer")
            
        except QKDClientError as e:
            print(f"❌ Errore recupero chiavi: {e}")
    
    def get_encryption_key(self, message_id: str) -> Optional[bytes]:
        """
        Ottiene una chiave per crittografare un messaggio.
        
        Args:
            message_id: ID univoco del messaggio
            
        Returns:
            bytes: Chiave per crittografia o None se non disponibile
        """
        with self._lock:
            # Trova una chiave non usata
            for key_entry in self.key_buffer:
                if not key_entry['used']:
                    # Marca come usata
                    key_entry['used'] = True
                    key_entry['message_id'] = message_id
                    self.used_key_ids.add(key_entry['key_id'])
                    
                    # Converti hex in bytes
                    key_bytes = bytes.fromhex(key_entry['key'])
                    
                    print(f"🔐 Chiave assegnata al messaggio {message_id}")
                    return key_bytes
            
            print(f"⚠️ Nessuna chiave disponibile per messaggio {message_id}")
            return None
    
    def get_decryption_key(self, message_id: str, key_hint: str) -> Optional[bytes]:
        """
        Ottiene una chiave per decrittografare un messaggio.
        
        Args:
            message_id: ID del messaggio
            key_hint: Hint per identificare la chiave (es: primi 8 char key_ID)
            
        Returns:
            bytes: Chiave per decrittografia o None se non trovata
        """
        with self._lock:
            # Cerca chiave per hint
            for key_entry in self.key_buffer:
                if key_entry['key_id'].startswith(key_hint):
                    key_bytes = bytes.fromhex(key_entry['key'])
                    print(f"🔓 Chiave trovata per messaggio {message_id}")
                    return key_bytes
            
            print(f"❌ Chiave non trovata per messaggio {message_id}")
            return None
    
    def get_buffer_status(self) -> Dict:
        """Ottiene informazioni sullo stato del buffer."""
        with self._lock:
            total_keys = len(self.key_buffer)
            used_keys = sum(1 for k in self.key_buffer if k['used'])
            available_keys = total_keys - used_keys
            
            return {
                'total_keys': total_keys,
                'used_keys': used_keys,
                'available_keys': available_keys,
                'buffer_health': 'good' if available_keys >= self.min_keys else 'low'
            }
    
    def cleanup_old_keys(self, max_age_hours: int = 24):
        """Rimuove chiavi vecchie dal buffer."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        with self._lock:
            old_count = len(self.key_buffer)
            self.key_buffer = [
                k for k in self.key_buffer 
                if (current_time - k['timestamp']) < max_age_seconds
            ]
            new_count = len(self.key_buffer)
            
            if old_count != new_count:
                print(f"🧹 Rimosse {old_count - new_count} chiavi vecchie")
```

### 8.3 Implementazione App di Messaggistica

**File: `secure_messenger.py`**
```python
#!/usr/bin/env python3
"""
Applicazione di Messaggistica con Crittografia Quantistica
"""
import json
import time
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from qkd_messaging_manager import QKDMessagingManager

class QuantumSecureMessenger:
    """
    App di messaggistica con crittografia quantistica.
    """
    
    def __init__(self, user_name: str, node_type: str):
        """
        Inizializza il messenger.
        
        Args:
            user_name: Nome utente (Alice o Bob)
            node_type: Tipo nodo QKD ("alice" o "bob")
        """
        self.user_name = user_name
        self.partner_name = "Bob" if user_name == "Alice" else "Alice"
        self.partner_id = "Bob2" if user_name == "Alice" else "Alice2"
        
        # Inizializza QKD Manager
        self.qkd_manager = QKDMessagingManager(
            node_type=node_type,
            partner_id=self.partner_id,
            min_keys=5
        )
        
        # Storage messaggi
        self.messages = []
        
        print(f"🚀 Quantum Secure Messenger avviato per {user_name}")
    
    def start(self):
        """Avvia il messenger."""
        self.qkd_manager.start()
        print("✅ Messenger pronto per comunicazioni sicure")
    
    def stop(self):
        """Ferma il messenger."""
        self.qkd_manager.stop()
        print("👋 Messenger fermato")
    
    def _derive_key_from_quantum(self, quantum_key: bytes, message_id: str) -> bytes:
        """Deriva una chiave Fernet dalla chiave quantistica."""
        # Usa message_ID come salt per derivazione deterministica
        salt = hashlib.sha256(message_id.encode()).digest()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        derived_key = kdf.derive(quantum_key)
        return base64.urlsafe_b64encode(derived_key)
    
    def send_message(self, text: str) -> Dict:
        """
        Invia un messaggio crittografato quantisticamente.
        
        Args:
            text: Testo del messaggio
            
        Returns:
            Dict: Messaggio crittografato con metadati
        """
        # Genera ID univoco messaggio
        message_id = hashlib.sha256(
            f"{time.time()}{text}{self.user_name}".encode()
        ).hexdigest()[:16]
        
        # Ottieni chiave quantistica
        quantum_key = self.qkd_manager.get_encryption_key(message_id)
        if not quantum_key:
            raise Exception("❌ Nessuna chiave quantistica disponibile")
        
        # Deriva chiave Fernet dalla chiave quantistica
        fernet_key = self._derive_key_from_quantum(quantum_key, message_id)
        fernet = Fernet(fernet_key)
        
        # Crittografa messaggio
        encrypted_text = fernet.encrypt(text.encode())
        
        # Crea messaggio completo
        message = {
            'id': message_id,
            'from': self.user_name,
            'to': self.partner_name,
            'timestamp': time.time(),
            'encrypted_content': base64.b64encode(encrypted_text).decode(),
            'key_hint': quantum_key.hex()[:8],  # Primi 8 char per identificazione
            'quantum_secured': True
        }
        
        # Salva in cronologia locale
        self.messages.append({
            **message,
            'direction': 'sent',
            'decrypted_content': text
        })
        
        print(f"📤 Messaggio inviato (ID: {message_id})")
        print(f"🔐 Crittografato con chiave quantistica")
        
        return message
    
    def receive_message(self, encrypted_message: Dict) -> str:
        """
        Riceve e decrittografa un messaggio.
        
        Args:
            encrypted_message: Messaggio crittografato ricevuto
            
        Returns:
            str: Testo decrittografato
        """
        message_id = encrypted_message['id']
        key_hint = encrypted_message['key_hint']
        
        # Ottieni chiave quantistica per decrittografia
        quantum_key = self.qkd_manager.get_decryption_key(message_id, key_hint)
        if not quantum_key:
            raise Exception(f"❌ Chiave quantistica non trovata per {message_id}")
        
        # Deriva chiave Fernet
        fernet_key = self._derive_key_from_quantum(quantum_key, message_id)
        fernet = Fernet(fernet_key)
        
        # Decrittografa messaggio
        encrypted_content = base64.b64decode(encrypted_message['encrypted_content'])
        decrypted_text = fernet.decrypt(encrypted_content).decode()
        
        # Salva in cronologia locale
        self.messages.append({
            **encrypted_message,
            'direction': 'received',
            'decrypted_content': decrypted_text
        })
        
        print(f"📥 Messaggio ricevuto da {encrypted_message['from']}")
        print(f"🔓 Decrittografato con chiave quantistica")
        print(f"💬 Contenuto: {decrypted_text}")
        
        return decrypted_text
    
    def show_status(self):
        """Mostra stato del sistema."""
        buffer_status = self.qkd_manager.get_buffer_status()
        
        print(f"\n📊 === STATO QUANTUM MESSENGER ({self.user_name}) ===")
        print(f"👤 Utente: {self.user_name}")
        print(f"🤝 Partner: {self.partner_name}")
        print(f"🔑 Chiavi disponibili: {buffer_status['available_keys']}")
        print(f"📈 Stato buffer: {buffer_status['buffer_health'].upper()}")
        print(f"💬 Messaggi totali: {len(self.messages)}")
        
        if buffer_status['buffer_health'] == 'low':
            print("⚠️  ATTENZIONE: Buffer chiavi basso!")
    
    def add_partner_keys(self, key_ids: List[str]):
        """Aggiunge chiavi ricevute dal partner (solo per Bob)."""
        self.qkd_manager.add_keys_from_partner(key_ids)

# Esempio di utilizzo
def demo_alice():
    """Demo per Alice (sender)."""
    alice = QuantumSecureMessenger("Alice", "alice")
    alice.start()
    
    try:
        time.sleep(2)  # Attendi buffer iniziale
        
        # Invia messaggi
        msg1 = alice.send_message("Ciao Bob! Questo messaggio è protetto da crittografia quantistica!")
        msg2 = alice.send_message("Le nostre comunicazioni sono quantisticamente sicure 🔐")
        
        # Mostra stato
        alice.show_status()
        
        # Simula invio a Bob (in pratica useresti rete/API)
        print("\n📡 Messaggi da inviare a Bob:")
        print(json.dumps(msg1, indent=2))
        print(json.dumps(msg2, indent=2))
        
    finally:
        alice.stop()

def demo_bob():
    """Demo per Bob (receiver)."""
    bob = QuantumSecureMessenger("Bob", "bob")
    bob.start()
    
    try:
        # Simula ricezione key_IDs da Alice
        # In pratica questi arriverebbero tramite canale sicuro
        key_ids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
        ]
        bob.add_partner_keys(key_ids)
        
        time.sleep(2)  # Attendi recupero chiavi
        
        # Simula messaggi ricevuti da Alice
        received_msg1 = {
            'id': 'abc123',
            'from': 'Alice',
            'to': 'Bob',
            'timestamp': time.time(),
            'encrypted_content': 'base64_encrypted_content_here',
            'key_hint': '550e8400',
            'quantum_secured': True
        }
        
        # Decrittografa (simulato)
        # bob.receive_message(received_msg1)
        
        # Mostra stato
        bob.show_status()
        
    finally:
        bob.stop()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "bob":
        demo_bob()
    else:
        demo_alice()
```

### 8.4 Script di Integrazione Completa

**File: `integration_demo.py`**
```python
#!/usr/bin/env python3
"""
Demo completa di integrazione QKD in app di messaggistica
"""
import time
import json
import threading
from secure_messenger import QuantumSecureMessenger

def simulate_network_channel():
    """Simula canale di rete per scambio messaggi."""
    return {
        'send_message': lambda msg: print(f"📡 Inviato via rete: {msg['id']}"),
        'send_key_ids': lambda ids: print(f"🔑 Key_IDs inviati: {ids}")
    }

def alice_scenario():
    """Scenario completo per Alice."""
    print("🚀 === SCENARIO ALICE (MASTER) ===")
    
    alice = QuantumSecureMessenger("Alice", "alice")
    network = simulate_network_channel()
    
    alice.start()
    
    try:
        # Attendi inizializzazione buffer
        print("⏳ Attendo inizializzazione buffer chiavi...")
        time.sleep(5)
        
        # Controlla stato
        alice.show_status()
        
        # Invia primo messaggio
        print("\n📝 Invio primo messaggio...")
        msg1 = alice.send_message("Ciao Bob! Comunicazione quantistica attiva! 🔐")
        network['send_message'](msg1)
        
        # Invia secondo messaggio
        print("\n📝 Invio secondo messaggio...")
        msg2 = alice.send_message("I nostri messaggi sono protetti dalla fisica quantistica!")
        network['send_message'](msg2)
        
        # Simula invio key_IDs a Bob
        key_ids_to_send = ["550e8400-e29b-41d4", "6ba7b810-9dad-11d1"]
        network['send_key_ids'](key_ids_to_send)
        
        # Stato finale
        print("\n📊 Stato finale:")
        alice.show_status()
        
        # Mantieni attivo per demo
        print("\n⏸  Premi Ctrl+C per terminare...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Demo Alice terminata")
    finally:
        alice.stop()

def bob_scenario():
    """Scenario completo per Bob."""
    print("🚀 === SCENARIO BOB (SLAVE) ===")
    
    bob = QuantumSecureMessenger("Bob", "bob")
    
    bob.start()
    
    try:
        # Simula ricezione key_IDs da Alice
        print("📩 Ricezione key_IDs da Alice...")
        received_key_ids = ["550e8400-e29b-41d4", "6ba7b810-9dad-11d1"]
        bob.add_partner_keys(received_key_ids)
        
        # Attendi recupero chiavi
        print("⏳ Recupero chiavi quantistiche...")
        time.sleep(3)
        
        # Controlla stato
        bob.show_status()
        
        # Simula ricezione messaggi crittografati
        print("\n📥 Simulazione ricezione messaggi...")
        
        # Messaggio 1 (simulato)
        fake_encrypted_msg1 = {
            'id': 'msg001',
            'from': 'Alice',
            'to': 'Bob',
            'timestamp': time.time(),
            'encrypted_content': 'gAAAAABh...simulato...',
            'key_hint': '550e8400',
            'quantum_secured': True
        }
        
        print("📨 Messaggio 1 ricevuto (simulato)")
        # bob.receive_message(fake_encrypted_msg1)  # Richiederebbe vera crittografia
        
        # Stato finale
        print("\n📊 Stato finale:")
        bob.show_status()
        
        # Mantieni attivo per demo
        print("\n⏸  Premi Ctrl+C per terminare...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Demo Bob terminata")
    finally:
        bob.stop()

if __name__ == "__main__":
    import sys
    
    print("🔐 === DEMO INTEGRAZIONE QKD MESSAGING ===")
    print("Questa demo mostra l'integrazione completa di QKD")
    print("in un'applicazione di messaggistica sicura.\n")
    
    if len(sys.argv) > 1 and sys.argv[1].lower() == "bob":
        bob_scenario()
    else:
        alice_scenario()
```

---

## 9. 📊 Monitoraggio e Manutenzione

### 9.1 Script di Monitoraggio Automatico

**File: `monitoring_service.py`**
```python
#!/usr/bin/env python3
"""
Servizio di monitoraggio automatico per nodi QKD
"""
import time
import json
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from src.alice_client import alice_client
from src.bob_client import bob_client

class QKDMonitoringService:
    """Servizio per monitoraggio continuo nodi QKD."""
    
    def __init__(self, node_type: str, config_file: str = "monitoring_config.json"):
        self.node_type = node_type
        self.config = self._load_config(config_file)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'qkd_{node_type}_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Client QKD
        if node_type == "alice":
            self.client = alice_client()
            self.partner_id = "Bob2"
        else:
            self.client = bob_client()
            self.partner_id = "Alice2"
        
        # Statistiche
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'last_success': None,
            'last_failure': None,
            'consecutive_failures': 0
        }
    
    def _load_config(self, config_file: str) -> dict:
        """Carica configurazione monitoraggio."""
        default_config = {
            'check_interval': 60,
            'alert_threshold': 3,
            'email_alerts': False,
            'email_config': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'to_addresses': []
            },
            'key_thresholds': {
                'critical': 5,
                'warning': 20,
                'optimal': 50
            }
        }
        
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            self.logger.info(f"Config file {config_file} non trovato, uso default")
        
        return default_config
    
    def check_node_health(self) -> dict:
        """Verifica salute del nodo QKD."""
        try:
            start_time = time.time()
            status = self.client.get_status(self.partner_id)
            response_time = time.time() - start_time
            
            # Analizza risposta
            stored_keys = status.get('stored_key_count', 0)
            max_keys = status.get('max_key_count', 1)
            fill_percentage = (stored_keys / max_keys) * 100 if max_keys > 0 else 0
            
            # Determina stato salute
            if stored_keys <= self.config['key_thresholds']['critical']:
                health_status = 'CRITICAL'
            elif stored_keys <= self.config['key_thresholds']['warning']:
                health_status = 'WARNING'
            elif stored_keys >= self.config['key_thresholds']['optimal']:
                health_status = 'OPTIMAL'
            else:
                health_status = 'GOOD'
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'status': 'SUCCESS',
                'health': health_status,
                'response_time': response_time,
                'stored_keys': stored_keys,
                'max_keys': max_keys,
                'fill_percentage': fill_percentage,
                'raw_response': status
            }
            
            self.stats['successful_checks'] += 1
            self.stats['last_success'] = result['timestamp']
            self.stats['consecutive_failures'] = 0
            
            return result
            
        except Exception as e:
            result = {
                'timestamp': datetime.now().isoformat(),
                'status': 'FAILURE',
                'error': str(e),
                'error_type': type(e).__name__
            }
            
            self.stats['failed_checks'] += 1
            self.stats['last_failure'] = result['timestamp']
            self.stats['consecutive_failures'] += 1
            
            return result
    
    def send_alert(self, message: str, severity: str = 'WARNING'):
        """Invia alert via email se configurato."""
        if not self.config['email_alerts']:
            return
        
        try:
            email_config = self.config['email_config']
            
            msg = MIMEText(message)
            msg['Subject'] = f'QKD Alert [{severity}] - Nodo {self.node_type.upper()}'
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['to_addresses'])
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Alert email inviato: {severity}")
            
        except Exception as e:
            self.logger.error(f"Errore invio email: {e}")
    
    def run_monitoring(self):
        """Esegue monitoraggio continuo."""
        self.logger.info(f"🚀 Avvio monitoraggio nodo {self.node_type.upper()}")
        
        try:
            while True:
                self.stats['total_checks'] += 1
                
                # Esegui controllo
                result = self.check_node_health()
                
                # Log risultato
                if result['status'] == 'SUCCESS':
                    self.logger.info(
                        f"✅ Controllo #{self.stats['total_checks']}: "
                        f"Salute={result['health']}, "
                        f"Chiavi={result['stored_keys']}, "
                        f"Tempo={result['response_time']:.2f}s"
                    )
                    
                    # Alert per stati critici
                    if result['health'] == 'CRITICAL':
                        message = (
                            f"STATO CRITICO per nodo {self.node_type.upper()}!\n"
                            f"Chiavi disponibili: {result['stored_keys']}\n"
                            f"Soglia critica: {self.config['key_thresholds']['critical']}\n"
                            f"Il link quantistico potrebbe essere inattivo."
                        )
                        self.send_alert(message, 'CRITICAL')
                    
                else:
                    self.logger.error(
                        f"❌ Controllo #{self.stats['total_checks']}: "
                        f"Errore={result['error']}"
                    )
                    
                    # Alert per fallimenti consecutivi
                    if self.stats['consecutive_failures'] >= self.config['alert_threshold']:
                        message = (
                            f"FALLIMENTI CONSECUTIVI per nodo {self.node_type.upper()}!\n"
                            f"Fallimenti: {self.stats['consecutive_failures']}\n"
                            f"Ultimo errore: {result['error']}\n"
                            f"Verificare connettività e certificati."
                        )
                        self.send_alert(message, 'CRITICAL')
                
                # Statistiche periodiche
                if self.stats['total_checks'] % 60 == 0:  # Ogni ora se check_interval=60s
                    uptime = (self.stats['successful_checks'] / self.stats['total_checks']) * 100
                    self.logger.info(f"📊 Statistiche: Uptime {uptime:.1f}% ({self.stats['total_checks']} controlli)")
                
                # Attendi prossimo controllo
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoraggio interrotto dall'utente")
        except Exception as e:
            self.logger.critical(f"💥 Errore critico nel monitoraggio: {e}")
            self.send_alert(f"Errore critico nel servizio di monitoraggio: {e}", 'CRITICAL')

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2 or sys.argv[1] not in ['alice', 'bob']:
        print("Uso: python monitoring_service.py [alice|bob]")
        sys.exit(1)
    
    node_type = sys.argv[1]
    service = QKDMonitoringService(node_type)
    service.run_monitoring()
```

### 9.2 Configurazione Monitoraggio

**File: `monitoring_config.json`**
```json
{
  "check_interval": 60,
  "alert_threshold": 3,
  "email_alerts": true,
  "email_config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-monitoring@gmail.com",
    "password": "your-app-password",
    "to_addresses": [
      "admin@yourcompany.com",
      "qkd-team@yourcompany.com"
    ]
  },
  "key_thresholds": {
    "critical": 5,
    "warning": 20,
    "optimal": 100
  },
  "logging": {
    "level": "INFO",
    "max_log_size_mb": 50,
    "backup_count": 5
  }
}
```

### 9.3 Servizio di Sistema per Monitoraggio

#### 🐧 Linux - Servizio Systemd

**File: `/etc/systemd/system/qkd-monitoring-alice.service`**
```ini
[Unit]
Description=QKD Monitoring Service - Alice Node
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=qkd-alice
Group=qkd-alice
WorkingDirectory=/opt/QKD_Mate
Environment=PATH=/opt/QKD_Mate/venv/bin
ExecStart=/opt/QKD_Mate/venv/bin/python monitoring_service.py alice
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Sicurezza
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/QKD_Mate

[Install]
WantedBy=multi-user.target
```

**Attivazione servizio Linux:**
```bash
# Copia file servizio
sudo cp qkd-monitoring-alice.service /etc/systemd/system/

# Ricarica systemd
sudo systemctl daemon-reload

# Abilita e avvia servizio
sudo systemctl enable qkd-monitoring-alice
sudo systemctl start qkd-monitoring-alice

# Verifica stato
sudo systemctl status qkd-monitoring-alice

# Visualizza log
sudo journalctl -u qkd-monitoring-alice -f
```

#### 🪟 Windows - Servizio Windows

**File: `install_windows_service.ps1`**
```powershell
# Script per installare servizio Windows QKD Monitoring
# Richiede privilegi amministratore

# Installa NSSM (Non-Sucking Service Manager)
# Scarica da: https://nssm.cc/download
# Oppure: choco install nssm

# Configura servizio
$serviceName = "QKDMonitoringAlice"
$pythonExe = "C:\QKD_Mate\venv\Scripts\python.exe"
$scriptPath = "C:\QKD_Mate\monitoring_service.py"
$workingDir = "C:\QKD_Mate"

# Installa servizio
nssm install $serviceName $pythonExe "$scriptPath alice"
nssm set $serviceName AppDirectory $workingDir
nssm set $serviceName DisplayName "QKD Monitoring Service - Alice"
nssm set $serviceName Description "Servizio di monitoraggio per nodo QKD Alice"
nssm set $serviceName Start SERVICE_AUTO_START

# Configura log
nssm set $serviceName AppStdout "$workingDir\logs\service_stdout.log"
nssm set $serviceName AppStderr "$workingDir\logs\service_stderr.log"
nssm set $serviceName AppRotateFiles 1
nssm set $serviceName AppRotateOnline 1
nssm set $serviceName AppRotateSeconds 86400
nssm set $serviceName AppRotateBytes 1048576

# Avvia servizio
Start-Service $serviceName

Write-Host "Servizio QKD Monitoring installato e avviato"
Write-Host "Controlla stato con: Get-Service $serviceName"
```

**Gestione servizio Windows:**
```powershell
# Verifica stato
Get-Service QKDMonitoringAlice

# Avvia/ferma servizio
Start-Service QKDMonitoringAlice
Stop-Service QKDMonitoringAlice

# Rimuovi servizio (se necessario)
Stop-Service QKDMonitoringAlice
nssm remove QKDMonitoringAlice confirm
```

#### 🍎 macOS - LaunchDaemon

**File: `/Library/LaunchDaemons/com.qkd.monitoring.alice.plist`**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.qkd.monitoring.alice</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/opt/QKD_Mate/venv/bin/python</string>
        <string>/opt/QKD_Mate/monitoring_service.py</string>
        <string>alice</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/opt/QKD_Mate</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/opt/QKD_Mate/logs/monitoring_alice.log</string>
    
    <key>StandardErrorPath</key>
    <string>/opt/QKD_Mate/logs/monitoring_alice_error.log</string>
    
    <key>UserName</key>
    <string>_qkd</string>
    
    <key>GroupName</key>
    <string>_qkd</string>
</dict>
</plist>
```

**Gestione LaunchDaemon macOS:**
```bash
# Crea utente dedicato (opzionale)
sudo dscl . -create /Users/_qkd
sudo dscl . -create /Users/_qkd UserShell /usr/bin/false
sudo dscl . -create /Users/_qkd RealName "QKD Service User"
sudo dscl . -create /Users/_qkd UniqueID 501
sudo dscl . -create /Users/_qkd PrimaryGroupID 20

# Crea directory log
sudo mkdir -p /opt/QKD_Mate/logs
sudo chown _qkd:_qkd /opt/QKD_Mate/logs

# Installa e avvia servizio
sudo cp com.qkd.monitoring.alice.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.qkd.monitoring.alice.plist

# Verifica stato
sudo launchctl list | grep qkd

# Ferma servizio
sudo launchctl unload /Library/LaunchDaemons/com.qkd.monitoring.alice.plist
```

---

## 10. 🔧 Troubleshooting

### 10.1 Problemi Comuni e Soluzioni

#### 🚨 Errore: Certificate verify failed

**Sintomi:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Cause e Soluzioni:**

1. **Certificato scaduto:**
   ```bash
   # Verifica scadenza
   openssl x509 -in certs/client_Alice2.crt -text -noout | grep "Not After"
   
   # Soluzione: Richiedere nuovi certificati all'amministratore KME
   ```

2. **Data/ora sistema incorretta:**
   ```bash
   # Verifica data/ora
   date
   
   # Sincronizza se necessario
   sudo ntpdate -s time.nist.gov
   # oppure
   sudo timedatectl set-ntp true
   ```

3. **CA non corrispondente:**
   ```bash
   # Verifica chain di certificazione
   openssl verify -CAfile certs/ca.crt certs/client_Alice2.crt
   
   # Se fallisce, richiedere CA corretta
   ```

#### 🌐 Errore: Connection refused

**Sintomi:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Diagnosi e Soluzioni:**

1. **Test connettività base:**

   **🐧 Linux & 🍎 macOS:**
   ```bash
   # Test ping
   ping -c 3 78.40.171.143
   
   # Test porta
   nc -zv 78.40.171.143 443
   
   # Test DNS (se applicabile)
   nslookup 78.40.171.143
   ```

   **🪟 Windows:**
   ```powershell
   # Test ping
   ping -n 3 78.40.171.143
   
   # Test porta
   Test-NetConnection -ComputerName 78.40.171.143 -Port 443
   
   # Test DNS
   nslookup 78.40.171.143
   
   # Alternative con telnet (se abilitato)
   telnet 78.40.171.143 443
   ```

2. **Verifica firewall:**

   **🐧 Linux:**
   ```bash
   # Controlla regole locali
   sudo ufw status
   
   # Permetti traffico HTTPS
   sudo ufw allow out 443/tcp
   
   # Test da altra macchina
   curl -k https://78.40.171.143:443
   ```

   **🪟 Windows:**
   ```powershell
   # Controlla firewall Windows
   Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*QKD*"}
   
   # Crea regola outbound per HTTPS
   New-NetFirewallRule -DisplayName "QKD HTTPS Out" -Direction Outbound -Protocol TCP -RemotePort 443 -Action Allow
   
   # Test con PowerShell
   Invoke-WebRequest -Uri "https://78.40.171.143:443" -SkipCertificateCheck
   ```

   **🍎 macOS:**
   ```bash
   # Verifica stato firewall
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   
   # Permetti connessioni per Python (se necessario)
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
   
   # Test connessione
   curl -k https://78.40.171.143:443
   ```

3. **Verifica routing:**

   **🐧 Linux & 🍎 macOS:**
   ```bash
   # Traceroute al KME
   traceroute 78.40.171.143
   
   # Verifica gateway
   ip route show  # Linux
   netstat -rn    # macOS
   ```

   **🪟 Windows:**
   ```powershell
   # Traceroute al KME
   tracert 78.40.171.143
   
   # Verifica routing table
   route print
   
   # Informazioni interfacce di rete
   ipconfig /all
   ```

#### 🔐 Errore: HTTP 401 Unauthorized

**Sintomi:**
```
HTTP 401: Unauthorized
```

**Cause e Soluzioni:**

1. **SAE_ID non registrato:**
   - Contattare amministratore KME
   - Verificare che Alice2/Bob2 siano abilitati
   - Richiedere log dal KME per debug

2. **Certificato non autorizzato:**
   ```bash
   # Verifica Subject del certificato
   openssl x509 -in certs/client_Alice2.crt -subject -noout
   
   # Deve corrispondere alla registrazione sul KME
   ```

#### 📦 Errore: HTTP 503 Service Unavailable

**Sintomi:**
```
HTTP 503: Service Unavailable
```

**Significato e Azioni:**

1. **KME temporaneamente non disponibile:**
   - Attendere qualche minuto
   - Verificare con amministratore KME
   - Controllare manutenzione programmata

2. **Nessuna chiave disponibile:**
   - Il link quantistico potrebbe essere inattivo
   - Verificare stato fisico dei dispositivi QKD
   - Richiedere diagnostica al team hardware

#### 🔧 Errore: Key_ID non trovato

**Sintomi:**
```
HTTP 400: Key ID not found
```

**Cause e Soluzioni:**

1. **Key_ID già consumato:**
   - Le chiavi QKD sono one-time use
   - Richiedere nuove chiavi

2. **Key_ID non valido:**
   - Verificare copia/incolla corretta
   - Controllare formato UUID

3. **Timeout key_ID:**
   - I key_ID possono scadere
   - Usare chiavi entro timeframe specificato

#### 🖥️ Problemi Specifici per Piattaforma

**🪟 Windows Specifici:**

1. **Errore: 'python' non riconosciuto:**
   ```powershell
   # Verifica installazione Python
   where python
   
   # Se non trovato, aggiungi Python al PATH
   # Oppure usa py launcher
   py -3 qkd_node_manager.py
   ```

2. **Errore permessi certificati:**
   ```powershell
   # Verifica proprietario file
   Get-Acl "certs\client_Alice2.key" | Format-List
   
   # Reset permessi se necessario
   icacls "certs\client_Alice2.key" /reset
   icacls "certs\client_Alice2.key" /grant:r "$env:USERNAME:(F)" /inheritance:r
   ```

3. **Errore SSL con PowerShell:**
   ```powershell
   # Forza TLS 1.2
   [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
   
   # Test connessione SSL
   $cert = [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
   Invoke-WebRequest -Uri "https://78.40.171.143:443"
   ```

**🍎 macOS Specifici:**

1. **Errore certificati Keychain:**
   ```bash
   # Verifica certificati in Keychain
   security find-certificate -a -c "client_Alice2"
   
   # Importa certificato se necessario (solo per test)
   security add-certificates certs/client_Alice2.crt
   ```

2. **Errore permessi con SIP (System Integrity Protection):**
   ```bash
   # Usa directory utente invece di /opt se problemi
   mkdir -p ~/QKD_Mate
   cd ~/QKD_Mate
   
   # Oppure disabilita SIP temporaneamente (sconsigliato in produzione)
   ```

3. **Errore Python versioni multiple:**
   ```bash
   # Verifica versioni Python disponibili
   ls -la /usr/bin/python*
   
   # Usa versione specifica
   python3.10 qkd_node_manager.py
   
   # Oppure crea alias
   alias python=python3.10
   ```

4. **Errore network tools mancanti:**
   ```bash
   # Installa network tools se mancanti
   brew install netcat
   brew install nmap  # Per test avanzati
   
   # Alternative native macOS
   nc -z 78.40.171.143 443  # invece di nc -zv
   ```

**Cross-Platform - Errori Ambiente Virtuale:**

1. **Ambiente virtuale non attivato:**
   ```bash
   # Linux/macOS
   source venv/bin/activate
   which python  # Dovrebbe mostrare path in venv
   
   # Windows
   venv\Scripts\activate
   where python  # Dovrebbe mostrare path in venv
   ```

2. **Dipendenze mancanti dopo aggiornamento:**
   ```bash
   # Reinstalla dipendenze
   pip install --force-reinstall -r requirements.txt
   
   # Verifica versioni
   pip list | grep requests
   pip list | grep yaml
   ```

### 10.2 Script di Diagnostica Avanzata

**File: `advanced_diagnostics.py`**
```python
#!/usr/bin/env python3
"""
Script di diagnostica avanzata per problemi QKD
"""
import subprocess
import socket
import ssl
import requests
import json
import time
from datetime import datetime
from src.alice_client import alice_client
from src.bob_client import bob_client

class QKDDiagnostics:
    """Diagnostica avanzata per sistemi QKD."""
    
    def __init__(self, node_type: str):
        self.node_type = node_type
        
        if node_type == "alice":
            self.client = alice_client()
            self.kme_ip = "78.40.171.143"
            self.partner_id = "Bob2"
        else:
            self.client = bob_client()
            self.kme_ip = "78.40.171.144"
            self.partner_id = "Alice2"
        
        self.results = {}
    
    def test_network_connectivity(self):
        """Test completo connettività di rete."""
        print("🌐 === TEST CONNETTIVITÀ DI RETE ===")
        
        # Test 1: Ping
        try:
            result = subprocess.run(
                ['ping', '-c', '3', '-W', '2', self.kme_ip],
                capture_output=True, text=True, timeout=10
            )
            ping_success = result.returncode == 0
            ping_time = "N/A"
            
            if ping_success:
                # Estrai tempo medio
                for line in result.stdout.split('\n'):
                    if 'avg' in line:
                        ping_time = line.split('/')[-2] + "ms"
                        break
        except:
            ping_success = False
            ping_time = "N/A"
        
        print(f"   Ping {self.kme_ip}: {'✅' if ping_success else '❌'} ({ping_time})")
        
        # Test 2: Porta 443
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.kme_ip, 443))
            port_open = result == 0
            sock.close()
        except:
            port_open = False
        
        print(f"   Porta 443: {'✅' if port_open else '❌'}")
        
        # Test 3: SSL handshake
        ssl_ok = False
        ssl_version = "N/A"
        if port_open:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((self.kme_ip, 443), timeout=5) as sock:
                    with context.wrap_socket(sock) as ssock:
                        ssl_ok = True
                        ssl_version = ssock.version()
            except:
                ssl_ok = False
        
        print(f"   SSL Handshake: {'✅' if ssl_ok else '❌'} ({ssl_version})")
        
        self.results['network'] = {
            'ping': ping_success,
            'port_443': port_open,
            'ssl_handshake': ssl_ok
        }
    
    def test_certificates(self):
        """Test validità e configurazione certificati."""
        print("\n🔐 === TEST CERTIFICATI ===")
        
        cert_prefix = f"client_{self.node_type.title()}2"
        cert_files = {
            'ca': 'certs/ca.crt',
            'cert': f'certs/{cert_prefix}.crt',
            'key': f'certs/{cert_prefix}.key'
        }
        
        cert_results = {}
        
        for name, path in cert_files.items():
            try:
                # Verifica esistenza
                with open(path, 'r') as f:
                    content = f.read()
                
                if name == 'key':
                    # Verifica chiave privata
                    valid = '-----BEGIN PRIVATE KEY-----' in content or '-----BEGIN RSA PRIVATE KEY-----' in content
                    
                    # Verifica permessi
                    import os
                    stat = os.stat(path)
                    perms_ok = not (stat.st_mode & 0o077)
                    
                    cert_results[name] = {
                        'exists': True,
                        'valid_format': valid,
                        'secure_permissions': perms_ok
                    }
                    
                    print(f"   {name.upper()}: {'✅' if valid else '❌'} "
                          f"(Permessi: {'✅' if perms_ok else '❌'})")
                else:
                    # Verifica certificato
                    valid = '-----BEGIN CERTIFICATE-----' in content
                    
                    if valid and name == 'cert':
                        # Verifica scadenza
                        try:
                            result = subprocess.run(
                                ['openssl', 'x509', '-in', path, '-checkend', '86400'],
                                capture_output=True
                            )
                            not_expired = result.returncode == 0
                        except:
                            not_expired = False
                        
                        cert_results[name] = {
                            'exists': True,
                            'valid_format': valid,
                            'not_expired': not_expired
                        }
                        
                        print(f"   {name.upper()}: {'✅' if valid else '❌'} "
                              f"(Scadenza: {'✅' if not_expired else '⚠️'})")
                    else:
                        cert_results[name] = {
                            'exists': True,
                            'valid_format': valid
                        }
                        print(f"   {name.upper()}: {'✅' if valid else '❌'}")
                
            except FileNotFoundError:
                cert_results[name] = {'exists': False}
                print(f"   {name.upper()}: ❌ (Non trovato)")
            except Exception as e:
                cert_results[name] = {'exists': True, 'error': str(e)}
                print(f"   {name.upper()}: ❌ (Errore: {e})")
        
        self.results['certificates'] = cert_results
    
    def test_qkd_api(self):
        """Test API QKD complete."""
        print("\n🔑 === TEST API QKD ===")
        
        # Test 1: Status
        try:
            start_time = time.time()
            status = self.client.get_status(self.partner_id)
            response_time = time.time() - start_time
            
            print(f"   Status API: ✅ ({response_time:.2f}s)")
            print(f"   Chiavi disponibili: {status.get('stored_key_count', 'N/A')}")
            print(f"   Dimensione chiavi: {status.get('key_size', 'N/A')} bit")
            
            self.results['api_status'] = {
                'success': True,
                'response_time': response_time,
                'stored_keys': status.get('stored_key_count', 0)
            }
            
        except Exception as e:
            print(f"   Status API: ❌ ({e})")
            self.results['api_status'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test 2: Richiesta chiavi (solo Alice)
        if self.node_type == "alice":
            try:
                start_time = time.time()
                keys = self.client.get_key(self.partner_id, number=1, size=256)
                response_time = time.time() - start_time
                
                key_count = len(keys.get('keys', []))
                print(f"   Richiesta chiavi: ✅ ({key_count} chiavi, {response_time:.2f}s)")
                
                self.results['key_request'] = {
                    'success': True,
                    'keys_received': key_count,
                    'response_time': response_time
                }
                
            except Exception as e:
                print(f"   Richiesta chiavi: ❌ ({e})")
                self.results['key_request'] = {
                    'success': False,
                    'error': str(e)
                }
    
    def generate_report(self):
        """Genera report diagnostico completo."""
        print("\n📋 === REPORT DIAGNOSTICO ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Nodo: {self.node_type.upper()}")
        print(f"KME: {self.kme_ip}:443")
        print("-" * 50)
        
        # Calcola punteggio salute
        total_tests = 0
        passed_tests = 0
        
        # Network tests
        if 'network' in self.results:
            for test, result in self.results['network'].items():
                total_tests += 1
                if result:
                    passed_tests += 1
        
        # Certificate tests
        if 'certificates' in self.results:
            for cert, data in self.results['certificates'].items():
                if isinstance(data, dict):
                    total_tests += len([k for k in data.keys() if k != 'error'])
                    passed_tests += len([v for v in data.values() if v is True])
        
        # API tests
        if 'api_status' in self.results:
            total_tests += 1
            if self.results['api_status']['success']:
                passed_tests += 1
        
        if 'key_request' in self.results:
            total_tests += 1
            if self.results['key_request']['success']:
                passed_tests += 1
        
        # Calcola percentuale
        health_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Punteggio salute: {health_percentage:.1f}% ({passed_tests}/{total_tests})")
        
        if health_percentage >= 90:
            print("Stato: 🟢 ECCELLENTE")
        elif health_percentage >= 70:
            print("Stato: 🟡 BUONO")
        elif health_percentage >= 50:
            print("Stato: 🟠 PROBLEMI MINORI")
        else:
            print("Stato: 🔴 PROBLEMI CRITICI")
        
        # Raccomandazioni
        print("\n💡 RACCOMANDAZIONI:")
        
        if 'network' in self.results:
            if not self.results['network']['ping']:
                print("   • Verificare connettività di rete al KME")
            if not self.results['network']['port_443']:
                print("   • Controllare firewall e apertura porta 443")
            if not self.results['network']['ssl_handshake']:
                print("   • Verificare configurazione SSL del KME")
        
        if 'certificates' in self.results:
            for cert, data in self.results['certificates'].items():
                if not data.get('exists', True):
                    print(f"   • Installare certificato {cert}")
                if not data.get('secure_permissions', True):
                    print(f"   • Correggere permessi certificato {cert}: chmod 600")
                if not data.get('not_expired', True):
                    print(f"   • Rinnovare certificato {cert} scaduto")
        
        if 'api_status' in self.results and not self.results['api_status']['success']:
            print("   • Verificare configurazione client e certificati")
            print("   • Contattare amministratore KME per verifica SAE_ID")
        
        # Salva report su file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'node_type': self.node_type,
            'kme_endpoint': f"{self.kme_ip}:443",
            'health_percentage': health_percentage,
            'tests_passed': passed_tests,
            'tests_total': total_tests,
            'detailed_results': self.results
        }
        
        filename = f"qkd_diagnostic_report_{self.node_type}_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report salvato in: {filename}")
    
    def run_full_diagnostics(self):
        """Esegue diagnostica completa."""
        print(f"🔧 === DIAGNOSTICA AVANZATA NODO {self.node_type.upper()} ===")
        
        self.test_network_connectivity()
        self.test_certificates()
        self.test_qkd_api()
        self.generate_report()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2 or sys.argv[1] not in ['alice', 'bob']:
        print("Uso: python advanced_diagnostics.py [alice|bob]")
        sys.exit(1)
    
    diagnostics = QKDDiagnostics(sys.argv[1])
    diagnostics.run_full_diagnostics()
```

---

## 11. 🔒 Sicurezza e Best Practices

### 11.1 Sicurezza dei Certificati

**Gestione Sicura:**
```bash
# 1. Creazione directory protetta
sudo mkdir -p /etc/qkd/certs
sudo chmod 700 /etc/qkd/certs
sudo chown qkd-user:qkd-user /etc/qkd/certs

# 2. Installazione certificati
sudo cp certificati_ricevuti/* /etc/qkd/certs/
sudo chmod 644 /etc/qkd/certs/*.crt
sudo chmod 600 /etc/qkd/certs/*.key
sudo chown qkd-user:qkd-user /etc/qkd/certs/*

# 3. Backup sicuro (crittografato)
tar czf - /etc/qkd/certs | gpg --symmetric --output certs_backup.tar.gz.gpg

# 4. Rotazione periodica
# Script per verificare scadenza e richiedere rinnovo
openssl x509 -in /etc/qkd/certs/client_Alice2.crt -checkend 2592000 # 30 giorni
```

**Monitoring Certificati:**
```python
#!/usr/bin/env python3
"""
Monitor scadenza certificati QKD
"""
import subprocess
import datetime
import smtplib
from email.mime.text import MIMEText

def check_cert_expiry(cert_path, days_warning=30):
    """Verifica scadenza certificato."""
    try:
        # Controlla se scade nei prossimi N giorni
        seconds_warning = days_warning * 24 * 3600
        result = subprocess.run([
            'openssl', 'x509', '-in', cert_path, 
            '-checkend', str(seconds_warning)
        ], capture_output=True)
        
        return result.returncode != 0  # True se sta scadendo
        
    except Exception as e:
        print(f"Errore controllo certificato {cert_path}: {e}")
        return True  # Assume scadenza in caso di errore

def send_expiry_alert(cert_path, days_left):
    """Invia alert scadenza certificato."""
    message = f"""
ALERT: Certificato QKD in scadenza

Certificato: {cert_path}
Giorni rimanenti: {days_left}

Azione richiesta:
1. Contattare amministratore KME per rinnovo
2. Programmare sostituzione certificato
3. Testare nuovo certificato in ambiente di staging

Questo è un alert automatico del sistema QKD.
"""
    
    # Configurare SMTP secondo le proprie esigenze
    print(f"ALERT: {cert_path} scade tra {days_left} giorni!")

# Uso
if check_cert_expiry('/etc/qkd/certs/client_Alice2.crt'):
    send_expiry_alert('/etc/qkd/certs/client_Alice2.crt', 30)
```

### 11.2 Hardening del Sistema

**Configurazione Firewall:**
```bash
#!/bin/bash
# Script hardening firewall per nodi QKD

# Reset regole
sudo ufw --force reset

# Policy di default: nega tutto
sudo ufw default deny incoming
sudo ufw default deny outgoing

# Permetti SSH (modifica porta se necessario)
sudo ufw allow in 22/tcp

# Permetti solo HTTPS verso KME
sudo ufw allow out 443/tcp

# Permetti DNS
sudo ufw allow out 53/udp
sudo ufw allow out 53/tcp

# Permetti NTP per sincronizzazione orario
sudo ufw allow out 123/udp

# Attiva firewall
sudo ufw --force enable

# Verifica regole
sudo ufw status verbose
```

**Configurazione Sistema:**
```bash
#!/bin/bash
# Script hardening sistema per QKD

# 1. Aggiornamenti automatici di sicurezza
sudo apt install unattended-upgrades -y
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades

# 2. Configurazione SSH sicura
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
sudo tee /etc/ssh/sshd_config.d/qkd-hardening.conf << 'EOF'
# Hardening SSH per nodi QKD
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
Protocol 2
EOF

sudo systemctl restart ssh

# 3. Configurazione log audit
sudo apt install auditd -y
sudo tee -a /etc/audit/rules.d/qkd.rules << 'EOF'
# Audit rules per QKD
-w /opt/QKD_Mate/certs -p rwxa -k qkd_certs
-w /opt/QKD_Mate/config -p rwxa -k qkd_config
-w /opt/QKD_Mate/src -p rwxa -k qkd_code
EOF

sudo systemctl restart auditd

# 4. Configurazione fail2ban
sudo apt install fail2ban -y
sudo tee /etc/fail2ban/jail.d/qkd.conf << 'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

sudo systemctl restart fail2ban

echo "✅ Hardening completato"
```

### 11.3 Backup e Recovery

**Script Backup Completo:**
```bash
#!/bin/bash
# Backup completo configurazione QKD

BACKUP_DIR="/backup/qkd"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="qkd_backup_${DATE}.tar.gz.gpg"

# Crea directory backup
sudo mkdir -p $BACKUP_DIR

# Backup elementi critici
sudo tar czf - \
    /opt/QKD_Mate/config \
    /opt/QKD_Mate/certs \
    /opt/QKD_Mate/node_config.yaml \
    /opt/QKD_Mate/monitoring_config.json \
    /etc/systemd/system/qkd-*.service \
    /var/log/qkd_*.log \
    | gpg --symmetric --cipher-algo AES256 --output "$BACKUP_DIR/$BACKUP_FILE"

# Verifica backup
if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo "✅ Backup creato: $BACKUP_DIR/$BACKUP_FILE"
    
    # Pulizia backup vecchi (mantieni ultimi 7 giorni)
    find $BACKUP_DIR -name "qkd_backup_*.tar.gz.gpg" -mtime +7 -delete
    
    # Sync su storage remoto (opzionale)
    # rsync -av $BACKUP_DIR/ backup-server:/backups/qkd/
else
    echo "❌ Errore creazione backup"
    exit 1
fi
```

**Procedura Recovery:**
```bash
#!/bin/bash
# Procedura recovery da backup

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo "Uso: $0 <backup_file.tar.gz.gpg>"
    exit 1
fi

echo "🔄 Avvio procedura recovery..."

# 1. Stop servizi
sudo systemctl stop qkd-monitoring-alice 2>/dev/null
sudo systemctl stop qkd-monitoring-bob 2>/dev/null

# 2. Backup configurazione corrente
sudo cp -r /opt/QKD_Mate /opt/QKD_Mate.recovery.backup

# 3. Estrazione backup
cd /tmp
gpg --decrypt "$BACKUP_FILE" | sudo tar xzf - -C /

# 4. Ripristino permessi
sudo chown -R qkd-user:qkd-user /opt/QKD_Mate
sudo chmod 700 /opt/QKD_Mate/certs
sudo chmod 600 /opt/QKD_Mate/certs/*.key
sudo chmod 644 /opt/QKD_Mate/certs/*.crt

# 5. Riavvio servizi
sudo systemctl daemon-reload
sudo systemctl start qkd-monitoring-alice 2>/dev/null
sudo systemctl start qkd-monitoring-bob 2>/dev/null

echo "✅ Recovery completato"
echo "🔍 Verifica funzionamento con: python qkd_node_manager.py diagnostic"
```

### 11.4 Procedure Operative Standard

**Checklist Pre-Deploy:**
- [ ] Sistema operativo aggiornato
- [ ] Python 3.10+ installato
- [ ] Dipendenze installate (requirements.txt)
- [ ] Certificati validi e con permessi corretti
- [ ] Connettività KME testata
- [ ] Firewall configurato
- [ ] Monitoring configurato
- [ ] Backup procedure implementate
- [ ] Documentazione aggiornata

**Checklist Post-Deploy:**
- [ ] Test diagnostico completo passato
- [ ] Status API funzionante
- [ ] Scambio chiavi test completato
- [ ] Monitoring attivo e funzionante
- [ ] Log rotation configurata
- [ ] Alert email funzionanti
- [ ] Performance baseline stabilita
- [ ] Procedura escalation definita

**Manutenzione Periodica:**
- **Giornaliera**: Controllo log e alert
- **Settimanale**: Verifica performance e uptime
- **Mensile**: Test backup/recovery, aggiornamenti sicurezza
- **Trimestrale**: Revisione certificati, test disaster recovery
- **Annuale**: Audit sicurezza completo, aggiornamento documentazione

---

## 🎯 Conclusione

Questa procedura fornisce una guida completa per implementare un sistema di comunicazione quantisticamente sicuro utilizzando QKD_Mate su **Linux, Windows e macOS**. L'integrazione in applicazioni reali richiede:

1. **Pianificazione accurata** dell'architettura di rete
2. **Implementazione graduale** con test approfonditi  
3. **Monitoraggio continuo** per garantire disponibilità
4. **Sicurezza a più livelli** per proteggere l'infrastruttura
5. **Procedure operative** ben definite per manutenzione

### 📋 Riepilogo Cross-Platform

| Aspetto | 🐧 Linux | 🪟 Windows | 🍎 macOS |
|---------|----------|------------|----------|
| **Directory di lavoro** | `/opt/QKD_Mate` | `C:\QKD_Mate` | `/opt/QKD_Mate` |
| **Ambiente virtuale** | `source venv/bin/activate` | `venv\Scripts\activate` | `source venv/bin/activate` |
| **Comando Python** | `python3` | `python` | `python3` |
| **Gestione permessi** | `chmod/chown` | ACL/PowerShell | `chmod/chown` |
| **Firewall** | `ufw` | Windows Defender | Preferenze Sistema |
| **Servizio sistema** | systemd | NSSM/Windows Service | LaunchDaemon |
| **Test rete** | `nc/ping -c` | `Test-NetConnection/ping -n` | `nc/ping -c` |
| **Package manager** | `apt` | Chocolatey/Manual | Homebrew |

### 🚀 Vantaggi Multi-Piattaforma

- **Flessibilità**: Deploy su qualsiasi sistema operativo
- **Compatibilità**: Stesso codice Python su tutte le piattaforme  
- **Manutenzione**: Procedure unificate con adattamenti specifici
- **Scalabilità**: Supporto per ambienti misti Linux/Windows/macOS
- **Testing**: Possibilità di test cross-platform

La tecnologia QKD offre sicurezza teoricamente assoluta, ora disponibile su tutti i principali sistemi operativi con implementazione e gestione professionale per realizzare il suo pieno potenziale in ambienti produttivi eterogenei.

**Per supporto tecnico e domande:**
- Consultare la documentazione nel repository
- Utilizzare gli script di diagnostica forniti (ora cross-platform)
- Contattare il team di sviluppo per problemi specifici della piattaforma

🔐 **La crittografia quantistica è il futuro della sicurezza delle comunicazioni - ora su Linux, Windows e macOS!**
