# QKD Node Manager - Guida all'uso

Script unificato per la gestione di un singolo nodo QKD (Alice o Bob).

## Configurazione Iniziale

### Metodo 1: Modifica diretta dello script
Apri `qkd_node_manager.py` e modifica la riga:
```python
NODE_TYPE = "alice"  # Cambia in "bob" per gestire il nodo Bob
```

### Metodo 2: Usa il file di configurazione (consigliato)
Modifica `node_config.yaml`:
```yaml
node_type: alice  # oppure "bob"
```

## Preparazione certificati

Prima di utilizzare lo script, assicurati di avere i certificati nella cartella `certs/`:

### Per il nodo Alice:
```
certs/
├── ca.crt
├── client_Alice2.crt
└── client_Alice2.key
```

### Per il nodo Bob:
```
certs/
├── ca.crt
├── client_Bob2.crt
└── client_Bob2.key
```

Proteggi le chiavi private:
```bash
chmod 600 certs/*.key
```

## Utilizzo

### Modalità interattiva (menu)
```bash
python qkd_node_manager.py
```

### Modalità comando diretto

#### Verifica stato del nodo
```bash
python qkd_node_manager.py status
```

#### Monitoraggio continuo
```bash
# Controllo ogni 30 secondi (default)
python qkd_node_manager.py monitor

# Controllo ogni 10 secondi
python qkd_node_manager.py monitor 10
```

#### Richiesta chiavi quantistiche
```bash
# Richiedi 1 chiave (default)
python qkd_node_manager.py keys

# Richiedi 5 chiavi
python qkd_node_manager.py keys 5
```

#### Diagnostica completa
```bash
python qkd_node_manager.py diagnostic
```

## Funzionalità

1. **Verifica stato**: Controlla se il nodo è attivo e raggiungibile
2. **Monitoraggio continuo**: Verifica periodicamente lo stato con statistiche di uptime
3. **Richiesta chiavi**: Ottiene chiavi quantistiche dal nodo
4. **Diagnostica**: Test completo di certificati, rete e connettività

## Deployment su dispositivi separati

### Dispositivo per Alice:
1. Copia l'intero progetto QKD_Mate
2. Configura `NODE_TYPE = "alice"` o modifica `node_config.yaml`
3. Inserisci solo i certificati di Alice in `certs/`
4. Esegui lo script

### Dispositivo per Bob:
1. Copia l'intero progetto QKD_Mate
2. Configura `NODE_TYPE = "bob"` o modifica `node_config.yaml`
3. Inserisci solo i certificati di Bob in `certs/`
4. Esegui lo script

## Troubleshooting

- **"certificate verify failed"**: Verifica validità certificati e data/ora sistema
- **"connection refused"**: Controlla firewall e raggiungibilità IP
- **"MANCANTE"**: Certificato non trovato nella cartella certs/

## Note sulla sicurezza

- I certificati sono specifici per ogni nodo
- Le chiavi private devono avere permessi 600
- Non condividere i certificati tra dispositivi
- Ogni dispositivo deve gestire solo il proprio nodo