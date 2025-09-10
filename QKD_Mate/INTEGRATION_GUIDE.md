# 🔗 Guida Integrazione QKD per App di Messaggistica

Questa guida ti mostra come integrare il sistema QKD nella tua app di messaggistica esistente, sostituendo RSA con chiavi quantistiche.

## 🎯 Tre Modi di Integrazione

### 1. **QKD Crypto Adapter** (Sostituzione Completa RSA)
**Migliore per:** App che vogliono sostituire completamente RSA con QKD

```python
from src.qkd_integration import QKDCryptoAdapter

# Invece di RSA
# crypto = RSACrypto()

# Usa QKD (stessa interfaccia!)
crypto = QKDCryptoAdapter("alice")  # o "bob"

# Crittografia (stesso utilizzo di RSA)
message = "Hello World!"
encrypted = crypto.encrypt(message, recipient_id="bob")

# Decrittografia
decrypted = crypto.decrypt(encrypted)
print(decrypted)  # "Hello World!"

# Cleanup
crypto.cleanup()
```

### 2. **QKD Message Wrapper** (Wrapper Trasparente)
**Migliore per:** App esistenti che vogliono aggiungere QKD senza modificare il codice

```python
from src.qkd_integration import QKDMessageWrapper

wrapper = QKDMessageWrapper("alice")

# Il tuo messaggio esistente
original_message = {
    "message_id": "123",
    "sender": "alice",
    "recipient": "bob", 
    "content": "Messaggio segreto!",
    "timestamp": 1234567890
}

# Wrappa con QKD (automatico)
encrypted_message = wrapper.wrap_outgoing_message(original_message)

# Invia come sempre...
send_message(encrypted_message)

# Lato ricevente
def on_message_received(message):
    # Unwrappa automaticamente
    decrypted = wrapper.unwrap_incoming_message(message)
    display_message(decrypted)
```

### 3. **QKD Key Provider** (Solo Chiavi)
**Migliore per:** App che vogliono solo le chiavi quantistiche

```python
from src.qkd_integration import QKDKeyProvider

provider = QKDKeyProvider("alice")

# Ottieni chiave quantistica
quantum_key = provider.get_encryption_key(32)  # 32 bytes

# Usa con la tua crittografia esistente
encrypted = your_crypto_function(message, quantum_key)
```

## 🚀 Integrazione Rapida - 5 Minuti

### Step 1: Inizializza QKD
```python
# Nel tuo main.py o app.py
from src.qkd_integration import create_qkd_integration

# Scegli il tipo di nodo
NODE_TYPE = "alice"  # o "bob"

# Crea integrazione (scegli il tipo)
qkd = create_qkd_integration(NODE_TYPE, "adapter")  # o "wrapper" o "provider"
```

### Step 2: Sostituisci la Crittografia
```python
# PRIMA (con RSA)
def send_message(content, recipient):
    encrypted = rsa_encrypt(content, recipient_public_key)
    transmit(encrypted)

# DOPO (con QKD)
def send_message(content, recipient):
    encrypted = qkd.encrypt(content, recipient)
    transmit(encrypted)
```

### Step 3: Sostituisci la Decrittografia
```python
# PRIMA (con RSA)
def receive_message(encrypted_data):
    decrypted = rsa_decrypt(encrypted_data, private_key)
    return decrypted

# DOPO (con QKD)
def receive_message(encrypted_data):
    decrypted = qkd.decrypt(encrypted_data)
    return decrypted
```

## 📱 Esempi per Framework Popolari

### Flask/FastAPI Backend
```python
from flask import Flask, request, jsonify
from src.qkd_integration import QKDCryptoAdapter

app = Flask(__name__)
qkd_crypto = QKDCryptoAdapter("alice")

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data['message']
    recipient = data['recipient']
    
    # Critta con QKD
    encrypted = qkd_crypto.encrypt(message, recipient)
    
    # Salva/invia il messaggio crittato
    store_message(encrypted)
    
    return jsonify({"status": "sent", "encrypted": True})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    encrypted_messages = load_messages()
    decrypted_messages = []
    
    for msg in encrypted_messages:
        decrypted = qkd_crypto.decrypt(msg)
        if decrypted:
            decrypted_messages.append({
                "content": decrypted,
                "timestamp": msg.get("timestamp"),
                "sender": msg.get("sender")
            })
    
    return jsonify(decrypted_messages)
```

### React/JavaScript Frontend
```javascript
// Lato frontend - chiama API backend con QKD
class QuantumMessenger {
    constructor(nodeType) {
        this.nodeType = nodeType;
        this.apiUrl = '/api';
    }
    
    async sendMessage(content, recipient) {
        const response = await fetch(`${this.apiUrl}/send_message`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: content,
                recipient: recipient,
                sender: this.nodeType
            })
        });
        
        return response.json();
    }
    
    async getMessages() {
        const response = await fetch(`${this.apiUrl}/get_messages`);
        return response.json();
    }
}

// Utilizzo
const messenger = new QuantumMessenger('alice');
await messenger.sendMessage('Ciao Bob!', 'bob');
```

### Django Integration
```python
# models.py
from django.db import models
from src.qkd_integration import QKDMessageWrapper

class QuantumMessage(models.Model):
    sender = models.CharField(max_length=50)
    recipient = models.CharField(max_length=50)
    encrypted_content = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    qkd_encrypted = models.BooleanField(default=True)

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

qkd_wrapper = QKDMessageWrapper("alice")

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Wrappa con QKD
        wrapped = qkd_wrapper.wrap_outgoing_message(data)
        
        # Salva in database
        QuantumMessage.objects.create(
            sender=wrapped['sender'],
            recipient=wrapped['recipient'],
            encrypted_content=wrapped['encrypted_content'],
            qkd_encrypted=wrapped['qkd_encrypted']
        )
        
        return JsonResponse({"status": "sent"})

def get_messages(request):
    messages = QuantumMessage.objects.all()
    decrypted_messages = []
    
    for msg in messages:
        # Unwrappa messaggio QKD
        unwrapped = qkd_wrapper.unwrap_incoming_message({
            'encrypted_content': msg.encrypted_content,
            'sender': msg.sender,
            'qkd_encrypted': msg.qkd_encrypted
        })
        
        decrypted_messages.append(unwrapped)
    
    return JsonResponse(decrypted_messages, safe=False)
```

## ⚙️ Configurazione Avanzata

### Configurazione Key Manager
```python
from src.qkd_integration import QKDKeyProvider

# Configurazione personalizzata
config = {
    "min_keys": 100,        # Pool minimo per app busy
    "max_keys": 500,        # Pool massimo
    "auto_refill": True,    # Riempimento automatico
    "maintenance_interval": 15  # Controllo ogni 15 secondi
}

provider = QKDKeyProvider("alice", config)
```

### Sessioni Sicure per Chat Lunghe
```python
# Crea sessione per chat lunga (risparmia chiavi QKD)
session_key = qkd_crypto.generate_session_key("chat_alice_bob_2024")

# Usa sessione per messaggi multipli
for message in long_conversation:
    encrypted = qkd_crypto.encrypt_with_session(message, session_key)
    send(encrypted)
```

### Monitoraggio e Statistiche
```python
# Controlla stato sistema QKD
status = qkd_crypto.get_crypto_info()
print(f"Chiavi disponibili: {status['available_keys']}")
print(f"Quantum safe: {status['quantum_safe']}")

# Statistiche dettagliate
provider_status = provider.get_provider_status()
print(f"Uptime: {provider_status['uptime']}")
```

## 🔧 Troubleshooting

### Problema: "Nessuna chiave quantistica disponibile"
```python
# Verifica connessione ai nodi QKD
from src.alice_client import alice_client

client = alice_client()
try:
    status = client.get("status")
    print("QKD node OK:", status)
except Exception as e:
    print("QKD node ERROR:", e)
```

### Problema: "Decrittografia fallita"
```python
# Verifica formato messaggio
if encrypted_data.get("encryption_type") == "QKD":
    print("Formato QKD corretto")
else:
    print("Formato non riconosciuto:", encrypted_data.keys())
```

### Problema: Performance
```python
# Usa sessioni per chat lunghe
session_key = qkd_crypto.generate_session_key(f"chat_{chat_id}")

# Oppure aumenta il pool di chiavi
provider = QKDKeyProvider("alice", {"min_keys": 200, "max_keys": 1000})
```

## 🚦 Best Practices

### 1. **Gestione Errori**
```python
def safe_encrypt(message, recipient):
    try:
        encrypted = qkd_crypto.encrypt(message, recipient)
        if encrypted:
            return encrypted
        else:
            # Fallback a crittografia tradizionale se necessario
            return fallback_encrypt(message, recipient)
    except Exception as e:
        log.error(f"QKD encryption failed: {e}")
        return fallback_encrypt(message, recipient)
```

### 2. **Pool di Chiavi Ottimale**
```python
# Per app con pochi messaggi
config = {"min_keys": 20, "max_keys": 100}

# Per app con molti messaggi
config = {"min_keys": 100, "max_keys": 500}

# Per app enterprise
config = {"min_keys": 500, "max_keys": 2000}
```

### 3. **Cleanup Appropriato**
```python
import atexit

# Registra cleanup automatico
atexit.register(qkd_crypto.cleanup)

# O usa context manager
class QKDApp:
    def __enter__(self):
        self.qkd = QKDCryptoAdapter("alice")
        return self.qkd
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.qkd.cleanup()

# Utilizzo
with QKDApp() as qkd:
    encrypted = qkd.encrypt("Hello!")
```

## 📊 Metriche e Monitoring

```python
# Integra metriche nella tua app
def get_app_stats():
    qkd_stats = qkd_crypto.get_crypto_info()
    
    return {
        "encryption_method": qkd_stats["encryption_method"],
        "quantum_safe": qkd_stats["quantum_safe"],
        "available_keys": qkd_stats["available_keys"],
        "messages_sent": get_message_count(),
        "uptime": get_uptime(),
        "security_level": "QUANTUM" if qkd_stats["quantum_safe"] else "CLASSICAL"
    }
```

## 🎉 Conclusione

Con questa integrazione, la tua app di messaggistica ora usa **Quantum Key Distribution** invece di RSA, fornendo:

- ✅ **Perfect Forward Secrecy**
- ✅ **Quantum-Safe Security**  
- ✅ **Compatibilità** con codice esistente
- ✅ **Performance** ottimizzate
- ✅ **Monitoraggio** completo

La sicurezza della tua app è ora **a prova di computer quantistici**! 🔮