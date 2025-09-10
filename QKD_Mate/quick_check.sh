#!/bin/bash
# Script rapido per verificare lo stato dei nodi QKD

echo "🔐 Verifica Rapida Nodi QKD"
echo "=========================="

# Verifica se i certificati sono presenti
echo "📋 Verifica certificati..."
if [ -f "certs/client_Alice2.crt" ] && [ -f "certs/client_Alice2.key" ] && 
   [ -f "certs/client_Bob2.crt" ] && [ -f "certs/client_Bob2.key" ] && 
   [ -f "certs/ca.crt" ]; then
    echo "✅ Certificati presenti"
else
    echo "❌ Certificati mancanti - inserisci i certificati nella directory certs/"
    echo "💡 Consulta certs/README.md per le istruzioni"
    exit 1
fi

echo ""
echo "🔗 Test connettività nodi..."

# Test Alice
echo -n "Alice (78.40.171.143): "
if timeout 10 python3 examples/get_status_alice.py >/dev/null 2>&1; then
    echo "🟢 ATTIVO"
    alice_status="OK"
else
    echo "🔴 INATTIVO"
    alice_status="FAIL"
fi

# Test Bob  
echo -n "Bob   (78.40.171.144): "
if timeout 10 python3 examples/get_status_bob.py >/dev/null 2>&1; then
    echo "🟢 ATTIVO" 
    bob_status="OK"
else
    echo "🔴 INATTIVO"
    bob_status="FAIL"
fi

echo ""
echo "📊 RIEPILOGO:"
if [ "$alice_status" = "OK" ] && [ "$bob_status" = "OK" ]; then
    echo "✅ Entrambi i nodi sono operativi!"
elif [ "$alice_status" = "OK" ] || [ "$bob_status" = "OK" ]; then
    echo "⚠️  Solo un nodo è operativo"
else
    echo "❌ Nessun nodo è raggiungibile"
fi

echo ""
echo "💡 Per dettagli completi esegui: python3 check_nodes_status.py"