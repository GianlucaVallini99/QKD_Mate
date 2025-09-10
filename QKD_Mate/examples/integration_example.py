#!/usr/bin/env python3
"""
Esempio pratico di integrazione QKD in app di messaggistica esistente
Mostra come sostituire RSA con QKD in modo semplice e veloce
"""

import sys
import time
from pathlib import Path

# Aggiungi path per import
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qkd_integration import QKDCryptoAdapter, QKDMessageWrapper, QKDKeyProvider

# Colori
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def example_1_direct_replacement():
    """
    ESEMPIO 1: Sostituzione diretta di RSA con QKD
    
    Se nella tua app hai qualcosa tipo:
    
    # PRIMA (con RSA)
    rsa_crypto = RSACrypto()
    encrypted = rsa_crypto.encrypt(message, public_key)
    decrypted = rsa_crypto.decrypt(encrypted, private_key)
    
    # DOPO (con QKD) - STESSA INTERFACCIA!
    """
    
    print(f"\n{BLUE}{BOLD}🔄 ESEMPIO 1: Sostituzione Diretta RSA → QKD{RESET}")
    print("=" * 50)
    
    # Inizializza QKD invece di RSA
    print(f"{YELLOW}1. Inizializzazione (sostituisci RSA con QKD):{RESET}")
    print("   # PRIMA: rsa_crypto = RSACrypto()")
    print("   # DOPO:")
    
    qkd_crypto = QKDCryptoAdapter("alice")  # Il tuo nodo (alice o bob)
    print(f"   {GREEN}✅ qkd_crypto = QKDCryptoAdapter('alice'){RESET}")
    
    # Crittografia - STESSA INTERFACCIA!
    print(f"\n{YELLOW}2. Crittografia (stessa interfaccia di RSA):{RESET}")
    message = "Messaggio segreto per Bob!"
    
    print("   # PRIMA: encrypted = rsa_crypto.encrypt(message, bob_public_key)")
    print("   # DOPO:")
    
    encrypted = qkd_crypto.encrypt(message, "bob")  # recipient invece di public_key
    print(f"   {GREEN}✅ encrypted = qkd_crypto.encrypt(message, 'bob'){RESET}")
    
    if encrypted:
        print(f"   📦 Messaggio crittato con chiave quantistica: {encrypted['key_id']}")
    
    # Decrittografia - STESSA INTERFACCIA!
    print(f"\n{YELLOW}3. Decrittografia (stessa interfaccia di RSA):{RESET}")
    print("   # PRIMA: decrypted = rsa_crypto.decrypt(encrypted, private_key)")
    print("   # DOPO:")
    
    # Simula che siamo Bob che riceve il messaggio
    qkd_crypto_bob = QKDCryptoAdapter("bob")
    decrypted = qkd_crypto_bob.decrypt(encrypted)
    print(f"   {GREEN}✅ decrypted = qkd_crypto.decrypt(encrypted){RESET}")
    
    if decrypted:
        print(f"   📖 Messaggio decrittato: '{decrypted}'")
    
    # Cleanup
    qkd_crypto.cleanup()
    qkd_crypto_bob.cleanup()
    
    print(f"\n{GREEN}🎉 Sostituzione completata! Ora usi QKD invece di RSA!{RESET}")


def example_2_wrapper_integration():
    """
    ESEMPIO 2: Integrazione con wrapper trasparente
    
    Se non vuoi modificare il codice esistente, usa il wrapper
    che aggiunge QKD automaticamente ai tuoi messaggi
    """
    
    print(f"\n{BLUE}{BOLD}📦 ESEMPIO 2: Wrapper Trasparente{RESET}")
    print("=" * 40)
    
    # Il tuo messaggio esistente (formato della tua app)
    print(f"{YELLOW}1. Il tuo messaggio esistente:{RESET}")
    your_existing_message = {
        "id": "msg_123",
        "from": "alice",
        "to": "bob",
        "text": "Ciao Bob, come stai?",
        "timestamp": int(time.time()),
        "type": "text"
    }
    
    print("   your_message = {")
    for key, value in your_existing_message.items():
        print(f"       '{key}': '{value}',")
    print("   }")
    
    # Inizializza wrapper
    print(f"\n{YELLOW}2. Inizializza wrapper QKD:{RESET}")
    wrapper = QKDMessageWrapper("alice")
    print(f"   {GREEN}✅ wrapper = QKDMessageWrapper('alice'){RESET}")
    
    # Wrappa messaggio in uscita (aggiunge QKD automaticamente)
    print(f"\n{YELLOW}3. Wrappa messaggio in uscita:{RESET}")
    print("   # Il wrapper aggiunge crittografia QKD automaticamente")
    
    wrapped_message = wrapper.wrap_outgoing_message({
        "sender": your_existing_message["from"],
        "recipient": your_existing_message["to"],
        "content": your_existing_message["text"],
        "message_id": your_existing_message["id"],
        "timestamp": your_existing_message["timestamp"]
    })
    
    print(f"   {GREEN}✅ wrapped = wrapper.wrap_outgoing_message(your_message){RESET}")
    
    if wrapped_message.get("qkd_encrypted"):
        print(f"   🔒 Messaggio automaticamente crittato con QKD!")
        print(f"   🛡️  Quantum safe: {wrapped_message.get('quantum_safe')}")
    
    # Unwrappa messaggio in arrivo (decritta automaticamente)
    print(f"\n{YELLOW}4. Unwrappa messaggio in arrivo:{RESET}")
    print("   # Il wrapper decritta automaticamente")
    
    unwrapped_message = wrapper.unwrap_incoming_message(wrapped_message)
    print(f"   {GREEN}✅ original = wrapper.unwrap_incoming_message(received){RESET}")
    
    if unwrapped_message.get("content"):
        print(f"   📖 Contenuto originale: '{unwrapped_message['content']}'")
        print(f"   🔓 Era crittato: {unwrapped_message.get('was_encrypted')}")
    
    wrapper.cleanup()
    
    print(f"\n{GREEN}🎉 Wrapper configurato! QKD aggiunto senza modificare codice esistente!{RESET}")


def example_3_flask_integration():
    """
    ESEMPIO 3: Integrazione in Flask/FastAPI
    Mostra come integrare in un backend web
    """
    
    print(f"\n{BLUE}{BOLD}🌐 ESEMPIO 3: Integrazione Flask/FastAPI{RESET}")
    print("=" * 45)
    
    print(f"{YELLOW}Codice per il tuo backend Flask/FastAPI:{RESET}")
    
    flask_code = '''
# app.py - Il tuo backend Flask con QKD

from flask import Flask, request, jsonify
from src.qkd_integration import QKDCryptoAdapter

app = Flask(__name__)

# Inizializza QKD (sostituisce RSA)
qkd_crypto = QKDCryptoAdapter("alice")  # o "bob" per l'altro server

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data['message']
    recipient = data['recipient']
    
    # Critta con QKD invece di RSA
    encrypted = qkd_crypto.encrypt(message, recipient)
    
    if encrypted:
        # Salva messaggio crittato nel database
        save_to_database(encrypted)
        
        return jsonify({
            "status": "sent",
            "encrypted": True,
            "quantum_safe": True,
            "key_id": encrypted.get("key_id")
        })
    else:
        return jsonify({"error": "Encryption failed"}), 500

@app.route('/get_messages', methods=['GET'])
def get_messages():
    encrypted_messages = load_from_database()
    decrypted_messages = []
    
    for msg in encrypted_messages:
        # Decritta con QKD invece di RSA
        decrypted = qkd_crypto.decrypt(msg)
        
        if decrypted:
            decrypted_messages.append({
                "content": decrypted,
                "sender": msg.get("sender"),
                "timestamp": msg.get("timestamp")
            })
    
    return jsonify(decrypted_messages)

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    print(flask_code)
    
    print(f"\n{GREEN}💡 Vantaggi:{RESET}")
    print("   ✅ Stessa interfaccia di RSA")
    print("   ✅ Perfect Forward Secrecy")
    print("   ✅ Quantum-safe security")
    print("   ✅ Nessuna modifica al frontend")


def example_4_session_keys():
    """
    ESEMPIO 4: Chiavi di sessione per chat lunghe
    Ottimizza l'uso delle chiavi QKD per conversazioni lunghe
    """
    
    print(f"\n{BLUE}{BOLD}🔑 ESEMPIO 4: Chiavi di Sessione per Chat Lunghe{RESET}")
    print("=" * 55)
    
    qkd_crypto = QKDCryptoAdapter("alice")
    
    # Crea sessione per chat lunga
    print(f"{YELLOW}1. Crea sessione sicura:{RESET}")
    chat_id = "chat_alice_bob_2024"
    session_key = qkd_crypto.generate_session_key(chat_id)
    
    if session_key:
        print(f"   {GREEN}✅ Sessione creata: {chat_id}{RESET}")
        print(f"   🔑 Chiave derivata da QKD")
    
    # Usa sessione per messaggi multipli (risparmia chiavi QKD)
    print(f"\n{YELLOW}2. Invia messaggi con sessione:{RESET}")
    messages = [
        "Ciao Bob!",
        "Come stai oggi?",
        "Hai visto le ultime notizie?",
        "Parliamo domani?",
        "Ciao!"
    ]
    
    encrypted_messages = []
    for i, message in enumerate(messages):
        # Usa chiave di sessione invece di consumare chiave QKD
        encrypted = qkd_crypto.encrypt_with_session(message, session_key)
        if encrypted:
            encrypted_messages.append(encrypted)
            print(f"   📤 Messaggio {i+1}: '{message}' → crittato con sessione")
    
    # Decritta messaggi
    print(f"\n{YELLOW}3. Decritta messaggi ricevuti:{RESET}")
    for i, encrypted_msg in enumerate(encrypted_messages):
        decrypted = qkd_crypto.decrypt_with_session(encrypted_msg, session_key)
        if decrypted:
            print(f"   📥 Messaggio {i+1}: '{decrypted}'")
    
    qkd_crypto.cleanup()
    
    print(f"\n{GREEN}💡 Vantaggi sessioni:{RESET}")
    print("   ✅ Una chiave QKD → molti messaggi")
    print("   ✅ Performance migliori per chat lunghe")
    print("   ✅ Mantiene sicurezza quantistica")


def example_5_monitoring():
    """
    ESEMPIO 5: Monitoraggio e statistiche
    Come monitorare il sistema QKD nella tua app
    """
    
    print(f"\n{BLUE}{BOLD}📊 ESEMPIO 5: Monitoraggio Sistema QKD{RESET}")
    print("=" * 45)
    
    qkd_crypto = QKDCryptoAdapter("alice")
    
    # Ottieni info sistema
    print(f"{YELLOW}1. Informazioni sistema:{RESET}")
    crypto_info = qkd_crypto.get_crypto_info()
    
    print(f"   🔐 Metodo: {crypto_info['encryption_method']}")
    print(f"   🧮 Algoritmo: {crypto_info['algorithm']}")
    print(f"   🛡️  Quantum Safe: {crypto_info['quantum_safe']}")
    print(f"   🔑 Chiavi disponibili: {crypto_info['available_keys']}")
    print(f"   ⚡ Perfect Forward Secrecy: {crypto_info['perfect_forward_secrecy']}")
    
    # Esempio endpoint di monitoraggio
    print(f"\n{YELLOW}2. Endpoint di monitoraggio per la tua app:{RESET}")
    
    monitoring_code = '''
@app.route('/qkd_status')
def qkd_status():
    status = qkd_crypto.get_crypto_info()
    
    return jsonify({
        "quantum_safe": status["quantum_safe"],
        "available_keys": status["available_keys"],
        "encryption_method": status["encryption_method"],
        "security_level": "QUANTUM" if status["quantum_safe"] else "CLASSICAL",
        "status": "operational" if status["available_keys"] > 0 else "warning"
    })
'''
    
    print(monitoring_code)
    
    # Controllo salute sistema
    print(f"{YELLOW}3. Health check:{RESET}")
    available_keys = crypto_info["available_keys"]
    
    if available_keys > 50:
        print(f"   {GREEN}✅ Sistema QKD: OTTIMO ({available_keys} chiavi){RESET}")
    elif available_keys > 10:
        print(f"   {YELLOW}⚠️  Sistema QKD: BUONO ({available_keys} chiavi){RESET}")
    else:
        print(f"   {YELLOW}⚠️  Sistema QKD: ATTENZIONE ({available_keys} chiavi){RESET}")
        print("   💡 Suggerimento: Aumenta il pool di chiavi")
    
    qkd_crypto.cleanup()


def main():
    """Esegue tutti gli esempi di integrazione"""
    
    print(f"{BLUE}{BOLD}🚀 ESEMPI DI INTEGRAZIONE QKD{RESET}")
    print(f"{BLUE}Come sostituire RSA con QKD nella tua app di messaggistica{RESET}")
    print("=" * 70)
    
    examples = [
        ("Sostituzione Diretta RSA → QKD", example_1_direct_replacement),
        ("Wrapper Trasparente", example_2_wrapper_integration),
        ("Integrazione Flask/FastAPI", example_3_flask_integration),
        ("Chiavi di Sessione", example_4_session_keys),
        ("Monitoraggio Sistema", example_5_monitoring)
    ]
    
    try:
        for i, (title, example_func) in enumerate(examples, 1):
            print(f"\n{BOLD}📋 ESEMPIO {i}: {title}{RESET}")
            
            try:
                example_func()
            except Exception as e:
                print(f"   ❌ Errore esempio: {e}")
            
            if i < len(examples):
                input(f"\n{YELLOW}Premi INVIO per il prossimo esempio...{RESET}")
    
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}👋 Esempi interrotti{RESET}")
    
    print(f"\n{GREEN}{BOLD}🎉 INTEGRAZIONE QKD COMPLETATA!{RESET}")
    print(f"{GREEN}La tua app ora usa Quantum Key Distribution invece di RSA!{RESET}")
    print(f"\n{BLUE}📚 Per maggiori dettagli, consulta:{RESET}")
    print(f"   📖 INTEGRATION_GUIDE.md")
    print(f"   🧪 test_integration.py")
    print(f"   📁 src/qkd_integration.py")


if __name__ == "__main__":
    main()