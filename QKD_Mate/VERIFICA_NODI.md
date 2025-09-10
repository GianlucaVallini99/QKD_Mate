# 🔐 Come Verificare se i Nodi QKD sono Attivi

Dopo aver inserito i certificati, hai diversi modi per verificare se i due nodi (Alice e Bob) sono attivi e raggiungibili.

## 📋 Prerequisiti

1. **Certificati necessari nella directory `certs/`:**
   - `client_Alice2.crt` - Certificato client per Alice
   - `client_Alice2.key` - Chiave privata per Alice  
   - `client_Bob2.crt` - Certificato client per Bob
   - `client_Bob2.key` - Chiave privata per Bob
   - `ca.crt` - Certificato della Certificate Authority

2. **Permessi corretti sui certificati:**
   ```bash
   chmod 600 certs/*.key    # Chiavi private
   chmod 644 certs/*.crt    # Certificati pubblici
   ```

## 🛠️ Metodi di Verifica

### 1. ✅ Verifica Completa (Raccomandato)
```bash
python3 check_nodes_status.py
```
**Cosa fa:**
- Verifica presenza di tutti i certificati
- Testa la connettività con entrambi i nodi
- Mostra tempi di risposta dettagliati
- Fornisce un riepilogo completo dello stato

### 2. ⚡ Verifica Rapida
```bash
./quick_check.sh
```
**Cosa fa:**
- Controllo veloce dei certificati
- Test di connettività base
- Output sintetico con stato dei nodi

### 3. 🔍 Verifica Singoli Nodi

#### Solo Alice:
```bash
python3 examples/get_status_alice.py
```

#### Solo Bob:
```bash
python3 examples/get_status_bob.py
```

## 📊 Interpretazione dei Risultati

### ✅ Entrambi i nodi attivi
```
Alice (78.40.171.143:443): 🟢 ATTIVO
Bob   (78.40.171.144:443): 🟢 ATTIVO
```
**Significato:** Sistema QKD completamente operativo, puoi procedere con lo scambio di chiavi.

### ⚠️ Solo un nodo attivo
```
Alice (78.40.171.143:443): 🟢 ATTIVO
Bob   (78.40.171.144:443): 🔴 INATTIVO
```
**Azioni da fare:**
- Verifica i certificati del nodo inattivo
- Controlla la connettività di rete
- Verifica che il servizio QKD sia avviato sul server

### ❌ Nessun nodo raggiungibile
```
Alice (78.40.171.143:443): 🔴 INATTIVO
Bob   (78.40.171.144:443): 🔴 INATTIVO
```
**Possibili cause:**
- Certificati mancanti o non corretti
- Problemi di rete/firewall
- Servizi QKD non avviati sui server
- Configurazione endpoints errata

## 🔧 Risoluzione Problemi

### Errore: "Certificati mancanti"
1. Copia tutti i certificati nella directory `certs/`
2. Verifica i nomi dei file (devono corrispondere esattamente)
3. Controlla i permessi dei file

### Errore: "Connection timeout"
1. Verifica la connettività di rete:
   ```bash
   ping 78.40.171.143  # Alice
   ping 78.40.171.144  # Bob
   ```
2. Controlla che le porte 443 siano aperte
3. Verifica i certificati SSL

### Errore: "SSL Certificate verification failed"
1. Controlla che il certificato CA sia corretto
2. Verifica che i certificati client non siano scaduti
3. Assicurati che i certificati corrispondano agli endpoints

## 📁 Struttura File

```
QKD_Mate/
├── certs/                     # Directory certificati
│   ├── client_Alice2.crt
│   ├── client_Alice2.key
│   ├── client_Bob2.crt
│   ├── client_Bob2.key
│   ├── ca.crt
│   └── README.md
├── config/                    # Configurazioni nodi
│   ├── alice.yaml
│   ├── bob.yaml
│   └── common.yaml
├── examples/                  # Script di test individuali
│   ├── get_status_alice.py
│   └── get_status_bob.py
├── check_nodes_status.py      # Script verifica completa
└── quick_check.sh            # Script verifica rapida
```

## 🚀 Prossimi Passi

Una volta verificato che entrambi i nodi sono attivi:

1. **Test scambio chiavi:**
   ```bash
   python3 examples/fetch_keys.py
   ```

2. **Monitoraggio continuo:**
   - Esegui periodicamente le verifiche
   - Monitora i log per eventuali errori
   - Controlla la qualità delle chiavi generate

## 💡 Suggerimenti

- **Automatizzazione:** Puoi aggiungere `check_nodes_status.py` a un cron job per monitoraggio automatico
- **Log:** Tutti gli script supportano il redirect dell'output per logging
- **Debug:** Usa `-v` o `--verbose` per output più dettagliato (se supportato)

---

**Nota:** Gli indirizzi IP configurati sono:
- Alice: `78.40.171.143:443`
- Bob: `78.40.171.144:443`