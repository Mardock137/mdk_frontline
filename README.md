# MDK Frontline

- **Versione Python utilizzata**: `3.14.4`
- **Versione progetto**: `0.7.0`

## 📋 Indice

- [📄 Descrizione](#-descrizione)
- [🚀 Avvio rapido](#-avvio-rapido)
- [📚 Documentazione](#-documentazione)

---

## 📄 Descrizione

MDK Frontline è un prodotto SaaS multi-tenant di customer support AI sviluppato da [MDK-137 OÜ](https://mdk137.com). Sostituisce il team umano di customer support di un'azienda, gestendo in autonomia le richieste dei clienti finali tramite una live chat dedicata.

L'azienda acquirente configura il sistema da una dashboard aziendale caricando i propri documenti (FAQ, policy, manuali, listini), che vengono usati come base di conoscenza dall'agente AI. La vendita e l'accesso iniziale avvengono esclusivamente tramite il sito MDK-137.

---

## 🚀 Avvio rapido

### Backend

Tutti i comandi vanno eseguiti dalla cartella `backend/`.

1. Creare l'ambiente virtuale:

   ```bash
   python -m venv .venv
   ```

2. Attivare l'ambiente virtuale:

   - Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
   - macOS / Linux: `source .venv/bin/activate`

3. Installare le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```

4. Copiare `.env.example` in `.env` e inserire le chiavi API reali.

5. Avviare il server di sviluppo:

   ```bash
   uvicorn main:app --reload
   ```

6. Verificare che il server risponda aprendo [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

Per eseguire la suite di test (sempre dalla cartella `backend/`):

```bash
pytest
```

### Frontend

Tutti i comandi vanno eseguiti dalla cartella `frontend/`.

1. Installare le dipendenze (una volta sola):

   ```bash
   npm install
   ```

2. Copiare `.env.local.example` in `.env.local` e inserire i valori.

3. Avviare il server di sviluppo:

   ```bash
   npm run dev
   ```

4. Aprire nel browser:
   - **Dashboard aziendale**: `http://localhost:3000/dashboard`
   - **Live chat** (cliente finale): `http://localhost:3000/chat/[slug]`

> Backend e frontend vanno avviati in parallelo (due terminali separati).

---

## 📚 Documentazione

- [Struttura della repo](docs/repo_structure.md)
- [Architettura](docs/architecture.md)
- [Configurazione](docs/config.md)
- [Sistema di logging](docs/observability.md)
- [Endpoints API](docs/api_endpoints.md)
- [Sistema RAG](docs/rag.md)
- [Frontend](docs/frontend.md)
- [Deploy](docs/deploy.md)
