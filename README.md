# MDK Frontline

[![Backend CI](https://github.com/Mardock137/mdk_frontline/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Mardock137/mdk_frontline/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/Mardock137/mdk_frontline/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Mardock137/mdk_frontline/actions/workflows/frontend-ci.yml)

- **Versione Python utilizzata**: `3.14.4`
- **Versione progetto**: `0.9.0`

## 📋 Indice

- [📄 Descrizione](#-descrizione)
- [🛠️ Stack](#️-stack)
- [🔐 Variabili d'ambiente](#-variabili-dambiente)
- [🚀 Avvio rapido](#-avvio-rapido)
- [📚 Documentazione](#-documentazione)

---

## 📄 Descrizione

MDK Frontline è un prodotto SaaS multi-tenant di customer support AI sviluppato da [MDK-137 OÜ](https://mdk137.com). Sostituisce il team umano di customer support di un'azienda, gestendo in autonomia le richieste dei clienti finali tramite una live chat dedicata.

L'azienda acquirente configura il sistema da una dashboard aziendale caricando i propri documenti (FAQ, policy, manuali, listini), che vengono usati come base di conoscenza dall'agente AI. La vendita e l'accesso iniziale avvengono esclusivamente tramite il sito MDK-137.

> **MDK Frontline non gestisce registrazione, pagamenti o checkout.** L'accesso alla dashboard avviene tramite redirect dal sito MDK-137, dove il cliente ha già acquistato il prodotto. Autenticazione e gestione abbonamenti sono responsabilità del sito MDK-137, non di questo progetto.

---

## 🛠️ Stack

| Componente    | Tecnologia                              |
|---------------|-----------------------------------------|
| Backend       | Python 3.14 · FastAPI · Pydantic        |
| Database      | Supabase (PostgreSQL + pgvector)        |
| File storage  | Supabase Storage                        |
| LLM           | Anthropic Claude (`claude-sonnet-4-6`)  |
| Embedding     | Voyage AI (`voyage-3`)                  |
| Frontend      | Next.js 16 · React 19 · Tailwind CSS v4 |
| UI components | shadcn/ui                               |

---

## 🔐 Variabili d'ambiente

### Backend (`backend/.env`)

| Variabile                   | Descrizione                                                            |
|-----------------------------|------------------------------------------------------------------------|
| `ANTHROPIC_API_KEY`         | Chiave API Anthropic (Claude)                                          |
| `VOYAGE_API_KEY`            | Chiave API Voyage AI (embedding)                                       |
| `SUPABASE_URL`              | URL del progetto Supabase                                              |
| `SUPABASE_ANON_KEY`         | Chiave pubblica Supabase                                               |
| `SUPABASE_SERVICE_ROLE_KEY` | Chiave privata Supabase (bypassa RLS)                                  |
| `DEV_COMPANY_ID`            | UUID dell'azienda usata in sviluppo (temporanea, MVP only)             |
| `FRONTEND_URL`              | Origine CORS permessa (`*` in sviluppo, URL esatto in produzione)      |
| `CHAT_RATE_LIMIT`           | Limite richieste per IP sull'endpoint chat (default: `20/minute`)      |
| `TRUST_PROXY_HEADERS`       | Legge l'IP da `X-Forwarded-For` dietro proxy fidato (default: `false`) |
| `LOG_LEVEL`                 | Livello di logging (default: `INFO`)                                   |

### Frontend (`frontend/.env.local`)

| Variabile             | Descrizione                                                     |
|-----------------------|-----------------------------------------------------------------|
| `NEXT_PUBLIC_API_URL` | URL base del backend FastAPI (default: `http://localhost:8000`) |

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
   - **Dashboard** (`http://localhost:3000/dashboard`) — area admin per l'azienda cliente (gestione documenti, ticket, configurazione agente)
   - **Live chat** (`http://localhost:3000/chat/[slug]`) — pagina pubblica usata dagli utenti finali dell'azienda cliente per chattare con l'agente AI

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
