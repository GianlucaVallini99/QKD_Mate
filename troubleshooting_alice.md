# 🔧 Troubleshooting Alice - Problemi Comuni

## Problemi di Installazione

### ❌ Errore: "Repository non trovata"
```bash
# Verifica URL repository
git ls-remote [URL_REPOSITORY]

# Controlla credenziali
git config --list | grep user
```

### ❌ Errore: "Dipendenze mancanti"
```bash
# Reinstalla dipendenze base
sudo apt update && sudo apt install -y python3-dev build-essential

# Verifica ambiente virtuale
source alice_env/bin/activate
pip install --upgrade pip setuptools wheel
```

### ❌ Errore: "Permessi negati"
```bash
# Correggi permessi
sudo chown -R $USER:$USER ~/alice-workspace
chmod -R 755 ~/alice-workspace
```

## Problemi di Configurazione

### ❌ Alice non si avvia
```bash
# Verifica configurazione
cat ~/.alice/config.yaml

# Controlla log
sudo journalctl -u alice -n 50

# Verifica porta
sudo netstat -tlnp | grep 8080
```

### ❌ Errore database
```bash
# Ricrea database
rm ~/alice-data/alice.db
sqlite3 ~/alice-data/alice.db "CREATE TABLE users (id INTEGER PRIMARY KEY);"
```

## Problemi di Rete

### ❌ Connessione rifiutata
```bash
# Verifica firewall
sudo ufw status
sudo ufw allow 8080/tcp

# Test connettività locale
curl -v http://localhost:8080
```

### ❌ Proxy aziendale
```bash
# Configura proxy
export http_proxy=http://proxy.azienda.com:8080
export https_proxy=http://proxy.azienda.com:8080

# Aggiorna configurazione Git
git config --global http.proxy http://proxy.azienda.com:8080
```

## Comandi Utili per Debug

```bash
# Status completo sistema
systemctl status alice
ps aux | grep alice
netstat -tlnp | grep alice

# Log in tempo reale
tail -f /var/log/alice/alice.log
sudo journalctl -u alice -f

# Test componenti
python3 -c "import alice; print('Alice importata correttamente')"
curl -s http://localhost:8080/api/health | jq .
```

## Contatti Supporto

- **Log Alice**: `/var/log/alice/alice.log`
- **Configurazione**: `~/.alice/config.yaml`
- **Ambiente**: `source ~/.alice/environment.sh`
- **Servizio**: `sudo systemctl [start|stop|restart] alice`