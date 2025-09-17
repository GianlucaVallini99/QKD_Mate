# Contributing to QKD_Mate

Grazie per il tuo interesse nel contribuire a QKD_Mate! 🎉

## Come Contribuire

### 1. Segnalazione Bug
- Verifica che non sia già stato segnalato nelle Issues
- Includi: descrizione, passi per riprodurre, output errore, versione Python/OS

### 2. Setup Ambiente di Sviluppo
```bash
git clone https://github.com/[tuo-username]/QKD_Mate.git
cd QKD_Mate
python -m venv venv
source venv/bin/activate  # Linux/Mac o venv\Scripts\activate su Windows
pip install -r requirements.txt
```

### 3. Workflow di Sviluppo
1. Crea branch: `git checkout -b feature/nome-feature`
2. Fai modifiche seguendo PEP 8
3. Testa: `python qkd_node_manager.py diagnostic`
4. Commit: `git commit -m "feat: descrizione"`
5. Push e apri Pull Request

### 4. Regole Importanti
- **Mai committare certificati** (verifica con `git grep "BEGIN.*KEY\|BEGIN.*CERTIFICATE"`)
- Documenta funzioni con docstring
- Testa con entrambi i nodi (Alice e Bob)
- Aggiorna README se aggiungi funzionalità

### 5. Commit Messages
Usa [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` nuova funzionalità
- `fix:` correzione bug  
- `docs:` modifiche documentazione
- `refactor:` refactoring codice

## Domande?
Apri una Discussion o contatta i maintainer.

Grazie per contribuire! 🚀