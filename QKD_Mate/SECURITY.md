# Security Policy

## 🔐 Sicurezza in QKD_Mate

Questo progetto gestisce comunicazioni sensibili con dispositivi di Quantum Key Distribution. La sicurezza è la nostra massima priorità.

## Pratiche di Sicurezza Implementate

### 1. Autenticazione mTLS (Mutual TLS)
- **Autenticazione bidirezionale**: Sia client che server verificano reciprocamente l'identità
- **Certificati X.509**: Utilizzo di certificati standard industriali
- **Verifica hostname**: Abilitata di default per prevenire attacchi MITM

### 2. Gestione Certificati
- **Separazione**: Ogni nodo (Alice/Bob) ha certificati dedicati
- **Permessi file**: Chiavi private con permessi 600 (solo proprietario)
- **Directory protetta**: La cartella `certs/` è esclusa dal versionamento

### 3. Comunicazioni Sicure
- **Solo HTTPS**: Tutte le comunicazioni su TLS 1.2+
- **No credenziali hardcoded**: Autenticazione solo via certificati
- **Timeout configurabili**: Prevenzione DoS con timeout appropriati

## Linee Guida di Sicurezza

### Per gli Sviluppatori

1. **MAI committare certificati o chiavi**
   - Usa sempre `.gitignore` per escludere `certs/`
   - Verifica prima di ogni commit

2. **Gestione errori sicura**
   - Non esporre stack trace in produzione
   - Log solo informazioni non sensibili

3. **Dipendenze**
   - Mantieni aggiornate le librerie
   - Usa `pip audit` per verificare vulnerabilità

### Per gli Operatori

1. **Protezione certificati**
   ```bash
   chmod 700 certs/
   chmod 600 certs/*.key
   ```

2. **Rotazione certificati**
   - Pianifica rotazione periodica
   - Testa nuovi certificati prima del deployment

3. **Monitoraggio**
   - Controlla log per tentativi di accesso anomali
   - Monitora certificati in scadenza

## Segnalazione Vulnerabilità

Se scopri una vulnerabilità di sicurezza:

1. **NON** aprire una issue pubblica
2. Invia una email a: security@[tuo-dominio].com
3. Includi:
   - Descrizione dettagliata
   - Passi per riprodurre
   - Impatto potenziale
   - Possibili mitigazioni

Risponderemo entro 48 ore.

## Gestione Incidenti

In caso di compromissione:

1. **Isola il sistema**
   - Disconnetti dalla rete se necessario
   - Preserva log per analisi

2. **Revoca certificati**
   - Contatta la CA per revocare certificati compromessi
   - Genera e distribuisci nuovi certificati

3. **Analisi**
   - Verifica log di sistema
   - Identifica vettore di attacco
   - Documenta lezioni apprese

## Audit di Sicurezza

### Checklist Periodica

- [ ] Certificati non scaduti
- [ ] Permessi file corretti su chiavi private
- [ ] Nessun certificato in repository Git
- [ ] Dipendenze aggiornate
- [ ] Log non contengono dati sensibili
- [ ] Backup sicuri dei certificati

### Tool Consigliati

```bash
# Verifica scadenza certificati
openssl x509 -in certs/client_Alice2.crt -noout -dates

# Audit dipendenze Python
pip-audit

# Verifica permessi
ls -la certs/

# Cerca certificati nel codice
git grep -E "(BEGIN|END) (CERTIFICATE|PRIVATE KEY)"
```

## Compliance

Il progetto segue:
- Best practices OWASP per applicazioni web
- Standard NIST per gestione chiavi crittografiche
- Linee guida industriali per QKD

## Contatti

- Security Team: security@[tuo-dominio].com
- Emergenze H24: +XX XXX XXXXXXX