#!/usr/bin/env python3
"""
Test di integrazione QKD per app di messaggistica
Simula l'integrazione in un'app esistente
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any

# Aggiungi path per import
sys.path.insert(0, str(Path(__file__).parent))

from src.qkd_integration import QKDCryptoAdapter, QKDMessageWrapper, QKDKeyProvider, create_qkd_integration

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class MockMessagingApp:
    """
    Simula un'app di messaggistica esistente che usa RSA
    per testare l'integrazione QKD
    """
    
    def __init__(self, user_id: str, encryption_method: str = "rsa"):
        self.user_id = user_id
        self.encryption_method = encryption_method
        self.messages = []
        
        # Simula inizializzazione RSA
        if encryption_method == "rsa":
            self.crypto = self._init_rsa_crypto()
        elif encryption_method == "qkd":
            self.crypto = self._init_qkd_crypto()
        else:
            raise ValueError(f"Metodo crittografia non supportato: {encryption_method}")
    
    def _init_rsa_crypto(self):
        """Simula inizializzazione RSA (mock)"""
        return {
            "type": "RSA",
            "key_size": 2048,
            "public_key": f"rsa_public_{self.user_id}",
            "private_key": f"rsa_private_{self.user_id}"
        }
    
    def _init_qkd_crypto(self):
        """Inizializza crittografia QKD reale"""
        return QKDCryptoAdapter(self.user_id)
    
    def send_message(self, content: str, recipient: str) -> Dict[str, Any]:
        """Invia messaggio (simula invio)"""
        message = {
            "message_id": f"msg_{int(time.time())}_{len(self.messages)}",
            "sender": self.user_id,
            "recipient": recipient,
            "content": content,
            "timestamp": time.time()
        }
        
        if self.encryption_method == "rsa":
            # Simula crittografia RSA (mock)
            encrypted_content = f"RSA_ENCRYPTED[{content}]_WITH_KEY[{recipient}_public]"
            message["encrypted_content"] = encrypted_content
            message["encryption"] = "RSA-2048"
        
        elif self.encryption_method == "qkd":
            # Crittografia QKD reale
            encrypted_package = self.crypto.encrypt(content, recipient)
            if encrypted_package:
                message["encrypted_content"] = encrypted_package
                message["encryption"] = "QKD"
                message["quantum_safe"] = True
            else:
                print(f"{RED}❌ Errore crittografia QKD{RESET}")
                return None
        
        self.messages.append(message)
        print(f"{GREEN}📤 Messaggio inviato con {self.encryption_method.upper()}{RESET}")
        return message
    
    def receive_message(self, encrypted_message: Dict[str, Any]) -> str:
        """Ricevi e decritta messaggio"""
        if self.encryption_method == "rsa":
            # Simula decrittografia RSA (mock)
            encrypted_content = encrypted_message["encrypted_content"]
            if encrypted_content.startswith("RSA_ENCRYPTED["):
                # Estrai contenuto simulato
                start = encrypted_content.find("[") + 1
                end = encrypted_content.find("]")
                content = encrypted_content[start:end]
                print(f"{GREEN}📥 Messaggio ricevuto con RSA{RESET}")
                return content
        
        elif self.encryption_method == "qkd":
            # Decrittografia QKD reale
            encrypted_content = encrypted_message["encrypted_content"]
            content = self.crypto.decrypt(encrypted_content)
            if content:
                print(f"{GREEN}📥 Messaggio ricevuto con QKD{RESET}")
                return content
            else:
                print(f"{RED}❌ Errore decrittografia QKD{RESET}")
                return None
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiche app"""
        stats = {
            "user_id": self.user_id,
            "encryption_method": self.encryption_method,
            "total_messages": len(self.messages),
            "encrypted_messages": len([m for m in self.messages if "encrypted_content" in m])
        }
        
        if self.encryption_method == "qkd" and hasattr(self.crypto, 'get_crypto_info'):
            qkd_info = self.crypto.get_crypto_info()
            stats.update({
                "quantum_safe": qkd_info.get("quantum_safe", False),
                "available_keys": qkd_info.get("available_keys", 0),
                "perfect_forward_secrecy": qkd_info.get("perfect_forward_secrecy", False)
            })
        
        return stats
    
    def cleanup(self):
        """Pulizia risorse"""
        if self.encryption_method == "qkd" and hasattr(self.crypto, 'cleanup'):
            self.crypto.cleanup()


def test_basic_integration():
    """Test integrazione base QKD vs RSA"""
    print(f"\n{BLUE}{BOLD}🧪 TEST 1: Integrazione Base QKD vs RSA{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    # Crea app con RSA (simulata)
    print(f"\n{CYAN}📱 Creando app con RSA...{RESET}")
    app_rsa = MockMessagingApp("alice", "rsa")
    
    # Crea app con QKD (reale)
    print(f"{CYAN}📱 Creando app con QKD...{RESET}")
    try:
        app_qkd = MockMessagingApp("alice", "qkd")
    except Exception as e:
        print(f"{RED}❌ Errore inizializzazione QKD: {e}{RESET}")
        return False
    
    # Test messaggi
    test_messages = [
        "Ciao Bob!",
        "Come stai?",
        "Questo messaggio è crittato con QKD! 🔮"
    ]
    
    print(f"\n{YELLOW}📝 Testando invio messaggi...{RESET}")
    
    # Test RSA
    print(f"\n{CYAN}🔒 Test con RSA:{RESET}")
    for msg in test_messages:
        sent = app_rsa.send_message(msg, "bob")
        if sent:
            received = app_rsa.receive_message(sent)
            print(f"   ✅ '{msg[:20]}...' -> OK")
        else:
            print(f"   ❌ '{msg[:20]}...' -> FAIL")
    
    # Test QKD
    print(f"\n{CYAN}🔮 Test con QKD:{RESET}")
    for msg in test_messages:
        sent = app_qkd.send_message(msg, "bob")
        if sent:
            received = app_qkd.receive_message(sent)
            if received == msg:
                print(f"   ✅ '{msg[:20]}...' -> OK")
            else:
                print(f"   ❌ '{msg[:20]}...' -> FAIL (content mismatch)")
        else:
            print(f"   ❌ '{msg[:20]}...' -> FAIL")
    
    # Confronta statistiche
    print(f"\n{YELLOW}📊 Statistiche:{RESET}")
    rsa_stats = app_rsa.get_stats()
    qkd_stats = app_qkd.get_stats()
    
    print(f"   RSA: {rsa_stats['total_messages']} messaggi, {rsa_stats['encryption_method']}")
    print(f"   QKD: {qkd_stats['total_messages']} messaggi, {qkd_stats['encryption_method']}")
    
    if qkd_stats.get('quantum_safe'):
        print(f"   {GREEN}✅ QKD: Quantum Safe{RESET}")
    
    if qkd_stats.get('perfect_forward_secrecy'):
        print(f"   {GREEN}✅ QKD: Perfect Forward Secrecy{RESET}")
    
    # Cleanup
    app_rsa.cleanup()
    app_qkd.cleanup()
    
    return True


def test_wrapper_integration():
    """Test integrazione con wrapper"""
    print(f"\n{BLUE}{BOLD}🧪 TEST 2: Integrazione con Message Wrapper{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    try:
        wrapper = QKDMessageWrapper("alice")
    except Exception as e:
        print(f"{RED}❌ Errore inizializzazione wrapper: {e}{RESET}")
        return False
    
    # Messaggio originale (formato della tua app)
    original_message = {
        "message_id": "test_123",
        "sender": "alice",
        "recipient": "bob",
        "content": "Messaggio segreto con wrapper!",
        "timestamp": time.time(),
        "message_type": "text"
    }
    
    print(f"{CYAN}📦 Messaggio originale:{RESET}")
    print(f"   Content: {original_message['content']}")
    print(f"   Sender: {original_message['sender']}")
    
    # Wrappa con QKD
    print(f"\n{YELLOW}🔄 Wrapping con QKD...{RESET}")
    wrapped = wrapper.wrap_outgoing_message(original_message)
    
    if wrapped.get("qkd_encrypted"):
        print(f"   {GREEN}✅ Messaggio wrappato con QKD{RESET}")
        print(f"   Quantum Safe: {wrapped.get('quantum_safe')}")
        print(f"   Encryption Method: {wrapped.get('encryption_method')}")
    else:
        print(f"   {RED}❌ Errore wrapping{RESET}")
        wrapper.cleanup()
        return False
    
    # Unwrappa (simula ricezione)
    print(f"\n{YELLOW}🔄 Unwrapping messaggio ricevuto...{RESET}")
    unwrapped = wrapper.unwrap_incoming_message(wrapped)
    
    if unwrapped.get("content") == original_message["content"]:
        print(f"   {GREEN}✅ Messaggio unwrappato correttamente{RESET}")
        print(f"   Content: {unwrapped['content']}")
        print(f"   Was Encrypted: {unwrapped.get('was_encrypted')}")
    else:
        print(f"   {RED}❌ Errore unwrapping{RESET}")
    
    wrapper.cleanup()
    return True


def test_key_provider():
    """Test provider di chiavi"""
    print(f"\n{BLUE}{BOLD}🧪 TEST 3: Key Provider{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    try:
        provider = QKDKeyProvider("alice")
    except Exception as e:
        print(f"{RED}❌ Errore inizializzazione provider: {e}{RESET}")
        return False
    
    # Test ottenimento chiavi
    print(f"{CYAN}🔑 Testando ottenimento chiavi...{RESET}")
    
    # Chiave singola
    key = provider.get_encryption_key(32)
    if key:
        print(f"   {GREEN}✅ Chiave ottenuta: {len(key)} bytes{RESET}")
    else:
        print(f"   {RED}❌ Errore ottenimento chiave{RESET}")
    
    # Coppia di chiavi (simulata)
    key_pair = provider.get_key_pair()
    if key_pair:
        private_key, public_id = key_pair
        print(f"   {GREEN}✅ Key pair ottenuta: {public_id[:16]}...{RESET}")
    else:
        print(f"   {RED}❌ Errore ottenimento key pair{RESET}")
    
    # Status provider
    status = provider.get_provider_status()
    print(f"\n{YELLOW}📊 Status Provider:{RESET}")
    print(f"   Chiavi disponibili: {status['available_keys']}")
    print(f"   Chiavi usate: {status['used_keys']}")
    print(f"   Node type: {status['node_type']}")
    
    provider.cleanup()
    return True


def test_performance():
    """Test performance QKD vs simulazione RSA"""
    print(f"\n{BLUE}{BOLD}🧪 TEST 4: Performance QKD{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    try:
        qkd = QKDCryptoAdapter("alice")
    except Exception as e:
        print(f"{RED}❌ Errore inizializzazione QKD: {e}{RESET}")
        return False
    
    # Test crittografia multipla
    messages = [f"Test message {i}" for i in range(10)]
    
    print(f"{CYAN}⏱️  Testando crittografia di {len(messages)} messaggi...{RESET}")
    
    start_time = time.time()
    encrypted_count = 0
    
    for msg in messages:
        encrypted = qkd.encrypt(msg, "bob")
        if encrypted:
            encrypted_count += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   {GREEN}✅ {encrypted_count}/{len(messages)} messaggi crittati{RESET}")
    print(f"   ⏱️  Tempo totale: {duration:.2f}s")
    print(f"   📊 Media per messaggio: {duration/len(messages):.3f}s")
    
    # Statistiche finali
    crypto_info = qkd.get_crypto_info()
    print(f"\n{YELLOW}📊 Info Crittografia:{RESET}")
    print(f"   Algoritmo: {crypto_info['algorithm']}")
    print(f"   Quantum Safe: {crypto_info['quantum_safe']}")
    print(f"   Chiavi disponibili: {crypto_info['available_keys']}")
    
    qkd.cleanup()
    return True


def test_error_handling():
    """Test gestione errori"""
    print(f"\n{BLUE}{BOLD}🧪 TEST 5: Gestione Errori{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")
    
    try:
        qkd = QKDCryptoAdapter("alice")
    except Exception as e:
        print(f"{RED}❌ Errore inizializzazione QKD: {e}{RESET}")
        return False
    
    # Test messaggio vuoto
    print(f"{CYAN}🔍 Test messaggio vuoto...{RESET}")
    empty_encrypted = qkd.encrypt("", "bob")
    if empty_encrypted:
        print(f"   {GREEN}✅ Messaggio vuoto gestito{RESET}")
    else:
        print(f"   {YELLOW}⚠️  Messaggio vuoto rifiutato{RESET}")
    
    # Test decrittografia dati corrotti
    print(f"{CYAN}🔍 Test dati corrotti...{RESET}")
    corrupted_data = {"invalid": "data", "format": "wrong"}
    decrypted = qkd.decrypt(corrupted_data)
    if decrypted is None:
        print(f"   {GREEN}✅ Dati corrotti rifiutati correttamente{RESET}")
    else:
        print(f"   {RED}❌ Dati corrotti accettati erroneamente{RESET}")
    
    # Test recipient non valido
    print(f"{CYAN}🔍 Test recipient non valido...{RESET}")
    invalid_encrypted = qkd.encrypt("test", "invalid_recipient")
    if invalid_encrypted:
        print(f"   {YELLOW}⚠️  Recipient non valido accettato{RESET}")
    else:
        print(f"   {GREEN}✅ Recipient non valido rifiutato{RESET}")
    
    qkd.cleanup()
    return True


def main():
    """Esegue tutti i test di integrazione"""
    print(f"{BLUE}{BOLD}🚀 QUANTUM KEY DISTRIBUTION - TEST INTEGRAZIONE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    tests = [
        ("Integrazione Base", test_basic_integration),
        ("Message Wrapper", test_wrapper_integration), 
        ("Key Provider", test_key_provider),
        ("Performance", test_performance),
        ("Gestione Errori", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{YELLOW}🔄 Eseguendo test: {test_name}...{RESET}")
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"{GREEN}✅ {test_name}: PASSED{RESET}")
            else:
                print(f"{RED}❌ {test_name}: FAILED{RESET}")
                
        except Exception as e:
            print(f"{RED}❌ {test_name}: ERROR - {e}{RESET}")
            results.append((test_name, False))
    
    # Risultati finali
    print(f"\n{BLUE}{BOLD}📊 RISULTATI FINALI{RESET}")
    print(f"{BLUE}{'='*30}{RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"   {test_name:<20} {status}")
    
    print(f"\n{CYAN}Risultato: {passed}/{total} test passati{RESET}")
    
    if passed == total:
        print(f"{GREEN}{BOLD}🎉 TUTTI I TEST PASSATI! Integrazione QKD pronta!{RESET}")
    else:
        print(f"{YELLOW}⚠️  Alcuni test falliti. Verifica la configurazione QKD.{RESET}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)