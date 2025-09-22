#!/bin/bash

# QKD_Mate Quick Start Script per Unix/Linux/macOS

echo ""
echo "======================================"
echo "  QKD_Mate - Quick Start"  
echo "======================================"
echo ""

# Controlla se Python è disponibile
if ! command -v python3 &> /dev/null; then
    echo "ERRORE: python3 non trovato"
    echo "Installa Python 3.10+ e riprova"
    exit 1
fi

# Controlla versione Python
python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERRORE: Python 3.10+ richiesto"
    echo "Versione attuale: $(python3 --version)"
    exit 1
fi

# Avvia quick start
python3 quick_start.py

echo ""
echo "Premi INVIO per uscire..."
read