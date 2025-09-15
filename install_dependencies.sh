#!/bin/bash

# =============================================================================
# INSTALLAZIONE DIPENDENZE ALICE
# =============================================================================

echo "📦 Installazione dipendenze per Alice..."

# Assicurati di essere nella directory di Alice
if [ ! -f "requirements.txt" ] && [ ! -f "package.json" ] && [ ! -f "pyproject.toml" ]; then
    echo "⚠️  File di configurazione non trovati. Assicurati di essere nella directory di Alice."
    exit 1
fi

# 1. RILEVAMENTO TIPO PROGETTO
echo "🔍 Rilevamento tipo progetto..."

if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    PROJECT_TYPE="python"
    echo "🐍 Progetto Python rilevato"
elif [ -f "package.json" ]; then
    PROJECT_TYPE="nodejs"
    echo "🟢 Progetto Node.js rilevato"
else
    echo "❓ Tipo progetto non chiaro, procedendo con installazione generica"
    PROJECT_TYPE="generic"
fi

# 2. INSTALLAZIONE DIPENDENZE PYTHON
if [ "$PROJECT_TYPE" = "python" ]; then
    echo "🐍 Configurazione ambiente Python..."
    
    # Installazione Python e pip se necessario
    if command -v apt &> /dev/null; then
        sudo apt install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    fi
    
    # Creazione ambiente virtuale
    echo "🏗️  Creazione ambiente virtuale..."
    python3 -m venv alice_env
    source alice_env/bin/activate
    
    # Aggiornamento pip
    pip install --upgrade pip
    
    # Installazione dipendenze
    if [ -f "requirements.txt" ]; then
        echo "📋 Installazione da requirements.txt..."
        pip install -r requirements.txt
    fi
    
    if [ -f "pyproject.toml" ]; then
        echo "📋 Installazione da pyproject.toml..."
        pip install -e .
    fi
    
    echo "✅ Ambiente Python configurato"
    echo "💡 Per attivare l'ambiente: source alice_env/bin/activate"
fi

# 3. INSTALLAZIONE DIPENDENZE NODE.JS
if [ "$PROJECT_TYPE" = "nodejs" ]; then
    echo "🟢 Configurazione ambiente Node.js..."
    
    # Installazione Node.js se necessario
    if ! command -v node &> /dev/null; then
        echo "📥 Installazione Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    # Installazione dipendenze
    echo "📦 Installazione dipendenze npm..."
    npm install
    
    echo "✅ Ambiente Node.js configurato"
fi

# 4. DIPENDENZE SISTEMA AGGIUNTIVE
echo "🔧 Installazione dipendenze sistema..."

# Dipendenze comuni per AI/ML
if command -v apt &> /dev/null; then
    sudo apt install -y \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        portaudio19-dev \
        espeak espeak-data \
        libespeak1 libespeak-dev \
        festival festvox-kallpc16k
elif command -v yum &> /dev/null; then
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y openssl-devel libffi-devel python3-devel
fi

# 5. VERIFICA INSTALLAZIONE
echo "🔍 Verifica installazione..."

if [ "$PROJECT_TYPE" = "python" ]; then
    source alice_env/bin/activate
    python3 -c "import sys; print(f'Python: {sys.version}')"
    pip list | head -10
elif [ "$PROJECT_TYPE" = "nodejs" ]; then
    node --version
    npm --version
    npm list --depth=0 | head -10
fi

echo "✅ Installazione dipendenze completata!"
echo ""
echo "🔄 Prossimi passi:"
echo "1. Configurare Alice per l'ambiente aziendale"
echo "2. Testare l'installazione"
echo "3. Configurare servizi e integrazioni"