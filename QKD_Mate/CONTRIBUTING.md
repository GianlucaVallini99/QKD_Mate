# Contributing to QKD_Mate

Grazie per il tuo interesse nel contribuire a QKD_Mate! 🎉

## Come Contribuire

### 1. Segnalazione Bug

Prima di segnalare un bug:
- Verifica che non sia già stato segnalato nelle [Issues](https://github.com/[username]/QKD_Mate/issues)
- Usa l'ultima versione del codice
- Raccogli informazioni dettagliate sull'errore

Quando segnali un bug, includi:
- Descrizione chiara del problema
- Passi per riprodurre
- Output di errore completo
- Versione Python e OS
- Configurazione utilizzata (alice/bob)

### 2. Suggerire Miglioramenti

Per suggerire nuove funzionalità:
1. Apri una [Issue](https://github.com/[username]/QKD_Mate/issues/new)
2. Usa il tag "enhancement"
3. Descrivi:
   - Il problema che risolve
   - Come dovrebbe funzionare
   - Possibili alternative

### 3. Contribuire con Codice

#### Setup Ambiente di Sviluppo

1. Fork il repository
2. Clone il tuo fork:
   ```bash
   git clone https://github.com/[tuo-username]/QKD_Mate.git
   cd QKD_Mate
   ```

3. Crea un virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oppure
   venv\Scripts\activate  # Windows
   ```

4. Installa in modalità sviluppo:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # se presente
   ```

#### Workflow di Sviluppo

1. Crea un branch per la tua feature:
   ```bash
   git checkout -b feature/nome-feature
   ```

2. Fai le tue modifiche seguendo lo stile del codice

3. Testa le modifiche:
   ```bash
   # Test manuali
   python qkd_node_manager.py diagnostic
   
   # Se ci sono test automatici
   pytest
   ```

4. Commit con messaggi chiari:
   ```bash
   git commit -m "feat: aggiunge supporto per [feature]"
   ```

5. Push al tuo fork:
   ```bash
   git push origin feature/nome-feature
   ```

6. Apri una Pull Request

### 4. Stile del Codice

#### Python Style Guide

- Segui [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usa nomi descrittivi per variabili e funzioni
- Documenta le funzioni con docstring
- Massimo 88 caratteri per linea (Black formatter)

Esempio:
```python
def check_node_status(self, timeout: int = 30) -> tuple[bool, dict]:
    """
    Verifica lo stato del nodo QKD.
    
    Args:
        timeout: Timeout in secondi per la richiesta
        
    Returns:
        Tupla (success, response_data)
        - success: True se il nodo è attivo
        - response_data: Dizionario con la risposta o None
    """
    try:
        # Codice qui
        pass
    except Exception as e:
        # Gestione errori
        pass
```

#### Commit Messages

Usa [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nuova funzionalità
- `fix:` correzione bug
- `docs:` modifiche documentazione
- `style:` formattazione, manca punto e virgola, etc
- `refactor:` refactoring codice
- `test:` aggiunta test
- `chore:` task di manutenzione

### 5. Testing

Prima di inviare una PR:

1. **Test Funzionali**
   - Testa con nodo Alice
   - Testa con nodo Bob
   - Verifica tutti i comandi

2. **Test Edge Cases**
   - Certificati mancanti
   - Nodo non raggiungibile
   - Timeout di rete

3. **Security Check**
   ```bash
   # Verifica che non ci siano certificati
   git diff --name-only | xargs grep -l "BEGIN.*KEY\|BEGIN.*CERTIFICATE" || echo "OK"
   ```

### 6. Documentazione

Aggiorna la documentazione se:
- Aggiungi nuove funzionalità
- Cambi comportamenti esistenti
- Aggiungi nuove dipendenze

File da considerare:
- `README.md` - documentazione principale
- `README_NODE_MANAGER.md` - guida utente
- Docstring nel codice
- Commenti per logica complessa

### 7. Pull Request

Quando apri una PR:

1. **Titolo chiaro**: Descrivi cosa fa la PR
2. **Descrizione dettagliata**:
   - Problema risolto
   - Approccio utilizzato
   - Test effettuati
3. **Checklist**:
   - [ ] Codice testato localmente
   - [ ] Documentazione aggiornata
   - [ ] Nessun certificato committato
   - [ ] Segue lo stile del progetto

### 8. Code Review

Durante la review:
- Rispondi ai commenti in modo costruttivo
- Fai update basati sul feedback
- Chiedi chiarimenti se necessario

## Domande?

- Apri una [Discussion](https://github.com/[username]/QKD_Mate/discussions)
- Contatta i maintainer

## Riconoscimenti

Tutti i contributori saranno riconosciuti nel file AUTHORS.md.

Grazie per contribuire a rendere QKD_Mate migliore! 🚀