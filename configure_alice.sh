#!/bin/bash

# =============================================================================
# CONFIGURAZIONE ALICE PER AMBIENTE AZIENDALE
# =============================================================================

echo "⚙️  Configurazione Alice per ambiente aziendale..."

# 1. CREAZIONE FILE DI CONFIGURAZIONE
echo "📝 Creazione file di configurazione..."

# Directory di configurazione
CONFIG_DIR="$HOME/.alice"
mkdir -p "$CONFIG_DIR"

# File di configurazione principale
cat > "$CONFIG_DIR/config.yaml" << 'EOF'
# =============================================================================
# CONFIGURAZIONE ALICE - AMBIENTE AZIENDALE
# =============================================================================

# Configurazioni generali
alice:
  name: "Alice Aziendale"
  version: "1.0.0"
  environment: "production"
  
# Configurazioni di rete
network:
  proxy:
    enabled: false
    http_proxy: ""
    https_proxy: ""
  
  firewall:
    allowed_ports: [8080, 8443, 9000]
    
# Configurazioni database
database:
  type: "sqlite"  # o "postgresql", "mysql"
  host: "localhost"
  port: 5432
  name: "alice_db"
  user: ""
  password: ""
  
# Configurazioni API
api:
  host: "0.0.0.0"
  port: 8080
  debug: false
  cors_enabled: true
  
# Configurazioni sicurezza
security:
  encryption_key: ""  # Da generare
  jwt_secret: ""      # Da generare
  session_timeout: 3600
  
# Configurazioni logging
logging:
  level: "INFO"
  file: "/var/log/alice/alice.log"
  max_size: "100MB"
  backup_count: 5
  
# Configurazioni AI/ML
ai:
  model_path: "./models"
  cache_size: "1GB"
  gpu_enabled: false
  
# Integrazioni aziendali
integrations:
  ldap:
    enabled: false
    server: ""
    base_dn: ""
    
  email:
    smtp_server: ""
    smtp_port: 587
    username: ""
    password: ""
    
  calendar:
    provider: "outlook"  # o "google", "exchange"
    api_key: ""
EOF

echo "✅ File di configurazione creato: $CONFIG_DIR/config.yaml"

# 2. CONFIGURAZIONE VARIABILI AMBIENTE
echo "🌍 Configurazione variabili d'ambiente..."

cat > "$CONFIG_DIR/environment.sh" << 'EOF'
#!/bin/bash

# Variabili d'ambiente Alice
export ALICE_HOME="$HOME/.alice"
export ALICE_CONFIG="$ALICE_HOME/config.yaml"
export ALICE_LOG_LEVEL="INFO"
export ALICE_PORT="8080"

# Percorsi
export ALICE_DATA_DIR="$HOME/alice-data"
export ALICE_MODELS_DIR="$HOME/alice-models"
export ALICE_CACHE_DIR="/tmp/alice-cache"

# Creazione directory
mkdir -p "$ALICE_DATA_DIR" "$ALICE_MODELS_DIR" "$ALICE_CACHE_DIR"

echo "✅ Variabili d'ambiente Alice configurate"
EOF

chmod +x "$CONFIG_DIR/environment.sh"

# 3. CONFIGURAZIONE SERVIZIO SYSTEMD
echo "🔧 Configurazione servizio systemd..."

sudo tee /etc/systemd/system/alice.service > /dev/null << 'EOF'
[Unit]
Description=Alice AI Assistant
After=network.target

[Service]
Type=simple
User=alice
Group=alice
WorkingDirectory=/home/alice/alice-workspace/alice
Environment=ALICE_CONFIG=/home/alice/.alice/config.yaml
ExecStart=/home/alice/alice-workspace/alice/alice_env/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 4. CREAZIONE UTENTE ALICE (se necessario)
echo "👤 Configurazione utente Alice..."

if ! id "alice" &>/dev/null; then
    echo "Creazione utente alice..."
    sudo useradd -m -s /bin/bash alice
    sudo usermod -aG sudo alice
    echo "✅ Utente alice creato"
else
    echo "✅ Utente alice già esistente"
fi

# 5. CONFIGURAZIONE PERMESSI
echo "🔐 Configurazione permessi..."

# Permessi directory
sudo chown -R alice:alice "$HOME/alice-workspace"
sudo chown -R alice:alice "$CONFIG_DIR"

# Permessi log
sudo mkdir -p /var/log/alice
sudo chown alice:alice /var/log/alice

echo "✅ Permessi configurati"

# 6. CONFIGURAZIONE DATABASE
echo "🗄️  Configurazione database..."

if command -v sqlite3 &> /dev/null; then
    echo "Inizializzazione database SQLite..."
    sqlite3 "$HOME/alice-data/alice.db" "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);"
    echo "✅ Database SQLite inizializzato"
fi

# 7. CONFIGURAZIONE FIREWALL
echo "🛡️  Configurazione firewall..."

if command -v ufw &> /dev/null; then
    sudo ufw allow 8080/tcp
    sudo ufw allow 8443/tcp
    echo "✅ Regole firewall configurate"
fi

echo ""
echo "✅ Configurazione Alice completata!"
echo ""
echo "📋 Riepilogo configurazione:"
echo "- File config: $CONFIG_DIR/config.yaml"
echo "- Variabili env: $CONFIG_DIR/environment.sh"
echo "- Servizio: /etc/systemd/system/alice.service"
echo "- Database: $HOME/alice-data/alice.db"
echo "- Log: /var/log/alice/alice.log"
echo ""
echo "🔄 Per completare l'installazione:"
echo "1. Modifica $CONFIG_DIR/config.yaml con i tuoi parametri"
echo "2. Esegui: source $CONFIG_DIR/environment.sh"
echo "3. Avvia Alice: sudo systemctl start alice"
echo "4. Abilita avvio automatico: sudo systemctl enable alice"