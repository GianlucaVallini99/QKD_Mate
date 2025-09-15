#!/bin/bash

# =============================================================================
# CONFIGURAZIONE GIT E CLONAZIONE REPOSITORY ALICE
# =============================================================================

echo "🔧 Configurazione Git per Alice..."

# 1. CONFIGURAZIONE GIT (se necessario)
echo "📝 Configurazione Git..."
read -p "Inserisci il tuo nome: " USER_NAME
read -p "Inserisci la tua email aziendale: " USER_EMAIL

git config --global user.name "$USER_NAME"
git config --global user.email "$USER_EMAIL"

# Configurazioni aggiuntive raccomandate
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.autocrlf input

echo "✅ Git configurato correttamente"

# 2. CREAZIONE DIRECTORY DI LAVORO
echo "📁 Creazione directory di lavoro..."
WORK_DIR="$HOME/alice-workspace"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "Directory di lavoro: $WORK_DIR"

# 3. CLONAZIONE REPOSITORY ALICE
echo "📥 Clonazione repository Alice..."
echo ""
echo "🔍 Opzioni di clonazione:"
echo "1. Repository pubblica GitHub"
echo "2. Repository aziendale privata"
echo "3. Fork personalizzato"
echo ""
read -p "Seleziona opzione (1-3): " REPO_OPTION

case $REPO_OPTION in
    1)
        echo "Clonazione da repository pubblica..."
        # Esempi di possibili repository Alice pubbliche
        echo "Repository Alice comuni:"
        echo "- https://github.com/alice-ai/alice"
        echo "- https://github.com/aliceai/core"
        read -p "Inserisci URL repository: " REPO_URL
        git clone "$REPO_URL" alice
        ;;
    2)
        echo "Clonazione da repository aziendale..."
        read -p "Inserisci URL repository aziendale: " REPO_URL
        read -p "Inserisci username: " USERNAME
        git clone "https://$USERNAME@$REPO_URL" alice
        ;;
    3)
        echo "Clonazione da fork personalizzato..."
        read -p "Inserisci URL del tuo fork: " REPO_URL
        git clone "$REPO_URL" alice
        ;;
    *)
        echo "⚠️  Opzione non valida"
        exit 1
        ;;
esac

# 4. VERIFICA CLONAZIONE
if [ -d "alice" ]; then
    cd alice
    echo "✅ Repository Alice clonata con successo!"
    echo "📍 Posizione: $(pwd)"
    echo "🌿 Branch corrente: $(git branch --show-current)"
    echo "📊 Ultimo commit: $(git log -1 --oneline)"
else
    echo "❌ Errore durante la clonazione"
    exit 1
fi

echo ""
echo "🔄 Prossimi passi:"
echo "1. Installare dipendenze Python/Node.js"
echo "2. Configurare ambiente virtuale"
echo "3. Installare pacchetti Alice"