# Security Policy

## 🔐 Sicurezza in QKD_Mate

Questo progetto gestisce comunicazioni sensibili con dispositivi QKD. La sicurezza è la nostra massima priorità.

## Pratiche di Sicurezza

### Autenticazione mTLS
- Autenticazione bidirezionale client-server
- Certificati X.509 dedicati per ogni nodo
- Comunicazioni solo su HTTPS/TLS 1.2+

### Gestione Certificati
- Chiavi private con permessi 600 (solo proprietario)
- Directory `certs/` esclusa dal versionamento
- Rotazione periodica programmata

## Linee Guida

### Per Sviluppatori
- **MAI committare certificati**: verifica con `git grep "BEGIN.*KEY\|BEGIN.*CERTIFICATE"`
- Gestione errori sicura (no stack trace in produzione)
- Mantieni dipendenze aggiornate

### Per Operatori
```bash
# Protezione certificati
chmod 700 certs/
chmod 600 certs/*.key

# Verifica scadenza
openssl x509 -in certs/client_Alice2.crt -noout -dates

# Audit dipendenze
pip-audit
```

## Segnalazione Vulnerabilità

Se scopri una vulnerabilità:
1. **NON** aprire issue pubblica
2. Invia email a: security@[tuo-dominio].com
3. Includi: descrizione, passi riproduzione, impatto

Risponderemo entro 48 ore.

## Checklist Sicurezza
- [ ] Certificati non scaduti
- [ ] Permessi file corretti
- [ ] Nessun certificato in Git
- [ ] Dipendenze aggiornate
- [ ] Log sicuri

## Contatti
- Security Team: security@[tuo-dominio].com