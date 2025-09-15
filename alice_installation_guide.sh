#!/bin/bash

# =============================================================================
# GUIDA INSTALLAZIONE ALICE - Computer Aziendale
# =============================================================================

echo "🚀 Avvio installazione Alice..."

# 1. CONTROLLO SISTEMA OPERATIVO
echo "📋 Controllo sistema operativo..."
if command -v lsb_release &> /dev/null; then
    DISTRO=$(lsb_release -si)
    VERSION=$(lsb_release -sr)
    echo "Sistema rilevato: $DISTRO $VERSION"
elif [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$NAME
    VERSION=$VERSION_ID
    echo "Sistema rilevato: $DISTRO $VERSION"
else
    echo "⚠️  Impossibile rilevare il sistema operativo"
    exit 1
fi

# 2. AGGIORNAMENTO SISTEMA
echo "🔄 Aggiornamento sistema..."
if command -v apt &> /dev/null; then
    sudo apt update && sudo apt upgrade -y
elif command -v yum &> /dev/null; then
    sudo yum update -y
elif command -v pacman &> /dev/null; then
    sudo pacman -Syu --noconfirm
else
    echo "⚠️  Gestore pacchetti non riconosciuto"
fi

# 3. INSTALLAZIONE DIPENDENZE BASE
echo "📦 Installazione dipendenze base..."
if command -v apt &> /dev/null; then
    sudo apt install -y git curl wget gnupg2 software-properties-common
elif command -v yum &> /dev/null; then
    sudo yum install -y git curl wget gnupg2
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm git curl wget gnupg
fi

# 4. CONTROLLO GIT
echo "🔍 Controllo configurazione Git..."
if ! git config --get user.name &> /dev/null; then
    echo "⚠️  Git non configurato. Configurazione necessaria:"
    echo "git config --global user.name 'Il Tuo Nome'"
    echo "git config --global user.email 'tua.email@azienda.com'"
fi

echo "✅ Preparazione sistema completata!"
echo ""
echo "🔄 Prossimi passi:"
echo "1. Configurare Git (se necessario)"
echo "2. Clonare la repository Alice"
echo "3. Installare le dipendenze specifiche"
echo "4. Configurare Alice per l'ambiente aziendale"