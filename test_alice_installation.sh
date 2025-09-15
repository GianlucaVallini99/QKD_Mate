#!/bin/bash

# =============================================================================
# TEST E VERIFICA INSTALLAZIONE ALICE
# =============================================================================

echo "🧪 Test installazione Alice..."

# 1. VERIFICA FILE E DIRECTORY
echo "📁 Verifica struttura file..."

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - MANCANTE"
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1/"
    else
        echo "❌ $1/ - MANCANTE"
    fi
}

# Verifica directory principali
check_dir "$HOME/alice-workspace/alice"
check_dir "$HOME/.alice"
check_dir "$HOME/alice-data"

# Verifica file di configurazione
check_file "$HOME/.alice/config.yaml"
check_file "$HOME/.alice/environment.sh"

# 2. VERIFICA DIPENDENZE
echo ""
echo "📦 Verifica dipendenze..."

# Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ Python3 non trovato"
fi

# Pip
if command -v pip &> /dev/null; then
    echo "✅ Pip: $(pip --version | cut -d' ' -f2)"
else
    echo "❌ Pip non trovato"
fi

# Git
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version | cut -d' ' -f3)"
else
    echo "❌ Git non trovato"
fi

# Node.js (se necessario)
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
fi

# 3. VERIFICA AMBIENTE VIRTUALE PYTHON
echo ""
echo "🐍 Verifica ambiente virtuale Python..."

if [ -d "$HOME/alice-workspace/alice/alice_env" ]; then
    echo "✅ Ambiente virtuale trovato"
    
    # Attiva ambiente e verifica pacchetti
    source "$HOME/alice-workspace/alice/alice_env/bin/activate"
    
    echo "📋 Pacchetti installati:"
    pip list | head -10
    
    # Verifica pacchetti specifici comuni per AI
    python3 -c "
import sys
packages = ['requests', 'numpy', 'pandas', 'flask', 'fastapi', 'sqlalchemy']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg} - non installato')
" 2>/dev/null
else
    echo "❌ Ambiente virtuale non trovato"
fi

# 4. VERIFICA CONFIGURAZIONE
echo ""
echo "⚙️  Verifica configurazione..."

if [ -f "$HOME/.alice/config.yaml" ]; then
    echo "📋 Configurazione Alice:"
    grep -E "^[[:space:]]*[a-zA-Z].*:" "$HOME/.alice/config.yaml" | head -10
fi

# 5. VERIFICA SERVIZIO
echo ""
echo "🔧 Verifica servizio systemd..."

if [ -f "/etc/systemd/system/alice.service" ]; then
    echo "✅ File servizio alice.service trovato"
    
    # Verifica stato servizio
    if systemctl is-enabled alice.service &>/dev/null; then
        echo "✅ Servizio abilitato"
    else
        echo "⚠️  Servizio non abilitato"
    fi
    
    if systemctl is-active alice.service &>/dev/null; then
        echo "✅ Servizio attivo"
    else
        echo "⚠️  Servizio non attivo"
    fi
else
    echo "❌ File servizio non trovato"
fi

# 6. VERIFICA CONNETTIVITÀ
echo ""
echo "🌐 Verifica connettività..."

# Test porta Alice
if command -v nc &> /dev/null; then
    if nc -z localhost 8080 2>/dev/null; then
        echo "✅ Porta 8080 aperta"
    else
        echo "⚠️  Porta 8080 non raggiungibile"
    fi
fi

# Test connessione internet
if ping -c 1 google.com &>/dev/null; then
    echo "✅ Connessione internet attiva"
else
    echo "❌ Connessione internet non disponibile"
fi

# 7. VERIFICA PERMESSI
echo ""
echo "🔐 Verifica permessi..."

# Permessi directory
if [ -w "$HOME/alice-workspace" ]; then
    echo "✅ Permessi scrittura workspace"
else
    echo "❌ Permessi scrittura workspace"
fi

if [ -w "$HOME/.alice" ]; then
    echo "✅ Permessi scrittura config"
else
    echo "❌ Permessi scrittura config"
fi

# 8. RIEPILOGO E RACCOMANDAZIONI
echo ""
echo "📊 RIEPILOGO TEST"
echo "=================="

echo ""
echo "🔄 PROSSIMI PASSI RACCOMANDATI:"
echo "1. Se ci sono errori, risolverli prima di procedere"
echo "2. Personalizzare la configurazione in ~/.alice/config.yaml"
echo "3. Avviare Alice: sudo systemctl start alice"
echo "4. Verificare i log: sudo journalctl -u alice -f"
echo "5. Testare l'interfaccia web: http://localhost:8080"
echo ""
echo "📞 SUPPORTO:"
echo "- Log Alice: /var/log/alice/alice.log"
echo "- Log sistema: sudo journalctl -u alice"
echo "- Configurazione: ~/.alice/config.yaml"