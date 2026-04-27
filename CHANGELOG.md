<!-- markdownlint-disable -->
# 📋 Changelog

## 0.7.6 — 2026-04-27

### Fixed

- **Fixture test condivise** (`backend/tests/conftest.py`, `backend/tests/api/test_agent.py`, `backend/tests/api/test_config.py`, `backend/tests/agents/test_support_agent.py`): centralizzate le fixture `company_id` e `conversation_id` in `conftest.py`, rimuovendo le duplicazioni locali nei moduli di test.
- **Copertura `BaseAgent` completata** (`backend/tests/agents/test_base_agent.py`): aggiunti test sul contratto della classe astratta, inclusi i casi di istanziazione vietata, sottoclasse concreta valida e verifica del metodo `run()` asincrono.
- **Errori infrastrutturali coperti** (`backend/tests/api/test_agent.py`, `backend/tests/api/test_config.py`, `backend/tests/api/test_dashboard.py`): aggiunti test `500` per i casi in cui l'agente o Supabase sollevano errori non gestiti.
- **Test agente meno fragile** (`backend/tests/agents/test_support_agent.py`): riscritto il test del tool sconosciuto per verificare il risultato finale dell'agente invece di dipendere dalla struttura interna di `call_args_list`.
- **Suite verificata**: i test aggiornati passano correttamente.

## 0.7.5 — 2026-04-27

### Fixed

- **Classi custom dei bottoni** (`frontend/components/ui/button.tsx`): corretto il merge di `className` nei componenti `Button`, così le classi passate dal chiamante non vengono più ignorate o scartate in modo silenzioso.
- **Toast piu' sicuri** (`frontend/components/ui/toast.tsx`): i timeout di auto-dismiss vengono ora tracciati e cancellati quando `ToastProvider` viene smontato, evitando aggiornamenti di stato dopo l'unmount. In più gli ID dei toast usano `crypto.randomUUID()` al posto di `Math.random()`.
- **Chat pubblica senza race condition** (`frontend/app/chat/[slug]/page.tsx`, `frontend/lib/api.ts`): il caricamento iniziale della configurazione usa `AbortController` e cleanup nel `useEffect`, così una navigazione rapida non provoca più `setState` su un componente già smontato.

## 0.7.4 — 2026-04-27

### Fixed

- **Tool agente non bloccanti** (`backend/tools/ticket.py`, `backend/tools/escalation.py`, `backend/agents/support_agent.py`): `create_ticket` ed `escalate` sono stati convertiti in funzioni asincrone e ora eseguono le chiamate Supabase con `asyncio.to_thread`, evitando di bloccare l'event loop durante le richieste FastAPI.
- **Client Voyage riusabile** (`backend/integrations/embedding_interfaces/voyage_embedding.py`): il client HTTP verso Voyage AI viene ora creato una sola volta nell'istanza `VoyageEmbedding` e riutilizzato per tutte le richieste di embedding, evitando la creazione di una nuova connessione a ogni chiamata.
- **Stats dashboard ottimizzate** (`backend/api/dashboard.py`): il conteggio ticket non scarica più tutte le righe in memoria. Ora usa query di count direttamente sul database per `open`, `in_progress`, `closed` ed escalation aperte.
- **Test aggiornati** (`backend/tests/tools/test_ticket.py`, `backend/tests/tools/test_escalation.py`, `backend/tests/agents/test_support_agent.py`, `backend/tests/api/test_dashboard.py`): allineati ai tool asincroni e alla nuova strategia di count lato DB. Suite verificata con test tutti passati.

## 0.7.3 — 2026-04-26

### Fixed

- **Pipeline di ingestione documenti** (`backend/rag/ingestion.py`): spostati upload su storage e aggiornamento di `storage_path` dentro il blocco `try/except`, così un errore in queste fasi marca correttamente il documento come `ERROR` invece di lasciarlo bloccato in `PROCESSING`.
- **Sanitizzazione filename upload** (`backend/rag/ingestion.py`): il path storage ora usa `Path(filename).name`, così vengono rimossi eventuali componenti di directory dal nome file inviato dall'utente.
- **Escalation piu' robusta** (`backend/tools/escalation.py`): inserimento ticket e update della conversazione sono gestiti separatamente. Se l'insert fallisce viene restituito un errore controllato; se fallisce solo l'update della conversazione, il problema viene loggato ma il ticket creato non va perso.
- **Test aggiornati**: aggiunti casi mirati in `backend/tests/rag/test_ingestion.py` e `backend/tests/tools/test_escalation.py` per coprire storage failure, sanitizzazione filename, ticket insert failure e conversation update failure.

## 0.7.2 — 2026-04-26

### Fixed

- **CORS backend** (`backend/main.py`): corretta la configurazione di `allow_credentials` quando `FRONTEND_URL` vale `*`. Prima il backend inviava una combinazione CORS non valida (`*` + credentials abilitate), che poteva far rifiutare le risposte dal browser.
- **Loghi esterni nella chat** (`frontend/next.config.ts`): aggiunti `remotePatterns` per permettere il caricamento di immagini remote via `next/image`, necessario per supportare loghi aziendali ospitati su domini esterni.
- **Crash nei tool dell'agente** (`backend/agents/support_agent.py`): i parametri dei tool ora vengono letti in modo sicuro con `.get()` invece di causare un crash se Claude omette un campo richiesto. Nei casi incompleti viene restituito un messaggio d'errore controllato invece di un `500`.
- **Test aggiornati** (`backend/tests/agents/test_support_agent.py`): aggiunti 3 test per verificare che `search_knowledge`, `create_ticket` ed `escalate` non vadano in crash quando ricevono input incompleto.

## 0.7.1 — 2026-04-26

### Fixed

- **Sicurezza endpoint chat** (`backend/api/agent.py`): aggiunta verifica cross-tenant su `conversation_id` per impedire il riuso di conversazioni appartenenti a un'altra company. Se la conversazione non appartiene al tenant corrente, l'endpoint ritorna `404`.
- **`AnthropicInterface`** (`backend/integrations/llm_interfaces/anthropic_interface.py`): corretta la gestione delle risposte con più blocchi `text`, che prima sovrascrivevano i segmenti precedenti. Ora tutti i blocchi vengono concatenati nell'ordine corretto.
- **Test aggiornati**: aggiunti casi mirati in `backend/tests/api/test_agent.py` e `backend/tests/integrations/llm_interfaces/test_anthropic_interface.py` per coprire sia il controllo cross-tenant sia le risposte testuali multi-blocco.

---

## 0.7.0 — 2026-04-26

### Added

- **Dashboard aziendale** (`/dashboard`): area admin per la gestione di documenti, ticket, configurazione agente e statistiche. Accessibile senza login (usa `DEV_COMPANY_ID` come il resto del progetto MVP).
- **Backend `backend/api/dashboard.py`**: 5 nuovi endpoint REST registrati su `/dashboard`:
  - `GET /dashboard/tickets` — lista ticket della company (tutti, ordinati per data, con campo `is_escalation`).
  - `PATCH /dashboard/tickets/{ticket_id}` — aggiorna lo stato del ticket (`open` → `in_progress` → `closed`).
  - `GET /dashboard/agent-config` — legge la configurazione attuale dell'agente.
  - `PATCH /dashboard/agent-config` — aggiorna parzialmente: `agent_name`, `company_display_name`, `primary_color`, `tone`, `default_language`, `welcome_message`.
  - `GET /dashboard/stats` — ritorna conversazioni totali, ticket per stato e conteggio escalation aperti.
- **Test `backend/tests/api/test_dashboard.py`**: 11 test con Supabase completamente mockato (tutti gli endpoint, happy path + errori 404/422/wrong company).
- **Componenti UI** in `frontend/components/ui/`: `button`, `card`, `badge`, `table`, `input`, `label`, `select`, `textarea`, `dialog`, `toast` — implementati con Tailwind CSS v4 e `class-variance-authority`.
- **`ToastProvider`** + hook `useToast`: sistema di notifiche contestuali (success/error/info) con auto-dismiss dopo 4 secondi.
- **Funzioni API** aggiunte a `frontend/lib/api.ts`: `getDocuments`, `uploadDocument`, `deleteDocument`, `getTickets`, `updateTicketStatus`, `getAgentConfig`, `updateAgentConfig`, `getStats`.
- **Layout dashboard** `frontend/app/dashboard/layout.tsx`: sidebar di navigazione con link a Documenti, Ticket, Configurazione, Statistiche.
- **Pagina Documenti** `frontend/app/dashboard/documents/page.tsx`: upload tramite bottone, lista file con stato e conteggio chunk, eliminazione con confirm.
- **Pagina Ticket** `frontend/app/dashboard/tickets/page.tsx`: lista ticket con badge stato/escalation, pulsanti cambio stato, banner escalation alert.
- **Pagina Configurazione** `frontend/app/dashboard/config/page.tsx`: form completo per `agent_name`, `company_display_name`, `primary_color` (color picker + hex), `tone`, `default_language`, `welcome_message`.
- **Pagina Statistiche** `frontend/app/dashboard/stats/page.tsx`: 4 stat card (conversazioni, ticket, escalation aperti, ticket chiusi) + barre di progressione per stato ticket.
- **Redirect** `frontend/app/dashboard/page.tsx` → `/dashboard/documents`.

### Changed

- `backend/main.py`: registrato il nuovo `dashboard_router` con prefisso `/dashboard`.
- `frontend/lib/api.ts`: refactoring interno con helper `handleResponse<T>` per evitare duplicazione della gestione errori.

---

## 0.6.0 — 2026-04-24

### Added

- **Pagina Live Chat pubblica** (`/chat/[slug]`): i clienti finali di un'azienda possono aprire la chat direttamente nel browser senza login. Al caricamento vengono mostrati il branding aziendale e il messaggio di benvenuto; i messaggi successivi vengono gestiti con l'agente AI.
- **Endpoint `GET /chat/{company_slug}/config`**: ritorna nome agente, nome azienda, logo, colore principale e messaggio di benvenuto. Nessuna autenticazione richiesta ([backend/api/config.py](backend/api/config.py)).
- **`CORSMiddleware`** (FastAPI built-in): il backend ora accetta richieste cross-origin. In sviluppo tutte le origini sono permesse (`*`); in produzione si limita a `FRONTEND_URL` ([backend/main.py](backend/main.py)).
- **Variabile `FRONTEND_URL`** nelle `Settings` e in `.env.example` ([backend/utils/config.py](backend/utils/config.py)).
- **Test `tests/api/test_config.py`**: 4 test con Supabase mockato (happy path, 404 company, 404 agent_config, logo_url presente).
- **Progetto Next.js 15** in `frontend/` con App Router, TypeScript, Tailwind CSS v4.
- **`frontend/lib/api.ts`**: funzioni `getConfig(slug)` e `sendMessage(slug, payload)` verso il backend FastAPI.
- **Componenti React** ([frontend/components/chat/](frontend/components/chat/)):
  - `ChatWindow.tsx` — contenitore messaggi con scroll automatico.
  - `MessageBubble.tsx` — bolla messaggio con colore primario per il cliente e stile neutro per l'agente.
  - `MessageInput.tsx` — textarea con invio tramite Enter o pulsante; colore pulsante dinamico.
  - `TypingIndicator.tsx` — tre pallini animati mostrati durante l'attesa della risposta.
- **`frontend/.env.local.example`** con `NEXT_PUBLIC_API_URL`.

### Changed

- `backend/main.py`: registrato il nuovo router `/chat/{slug}/config` e aggiunto `CORSMiddleware`.

---

## 0.5.0 — 2026-04-24

### Added

- **Agente AI autonomo con tool calling** (`SupportAgent`): loop completo che chiama Claude, esegue i tool richiesti e salva i messaggi nel DB ([backend/agents/support_agent.py](backend/agents/support_agent.py)).
- **Tre tool invocabili dall'agente** ([backend/tools/](backend/tools/)):
  - `knowledge.py` — ricerca semantica sulla knowledge base aziendale (`search_knowledge`).
  - `ticket.py` — crea un ticket di supporto con `is_escalation=False` (`create_ticket`).
  - `escalation.py` — crea un ticket con `is_escalation=True` e aggiorna lo stato della conversazione a `ESCALATED` (`escalate`).
- **`AnthropicInterface`**: adapter concreto per Claude con supporto nativo al tool calling ([backend/integrations/llm_interfaces/anthropic_interface.py](backend/integrations/llm_interfaces/anthropic_interface.py)).
- **`BaseLLMInterface` aggiornata**: metodo `generate(prompt)` sostituito con `chat(messages, system, tools)` più adatto ai modelli moderni; aggiunti dataclass `ChatResponse` e `ToolUse` ([backend/integrations/llm_interfaces/base_llm_interface.py](backend/integrations/llm_interfaces/base_llm_interface.py)).
- **System prompt template** per l'agente di supporto: nome agente, azienda, tono, lingua, istruzioni sui tool ([backend/config/prompts/support_agent.py](backend/config/prompts/support_agent.py)).
- **Endpoint `POST /chat/{company_slug}/message`**: crea conversazione se necessario, esegue l'agente e ritorna la risposta ([backend/api/agent.py](backend/api/agent.py)).
- **Migration SQL 014** ([backend/database/migrations/014_tickets_add_is_escalation.sql](backend/database/migrations/014_tickets_add_is_escalation.sql)): colonna `is_escalation boolean NOT NULL DEFAULT false` nella tabella `tickets`.
- **Modelli Pydantic aggiornati**: `TicketCreate` e `Ticket` espongono ora il campo `is_escalation: bool = False`.
- **`config/llm_models/support_agent.yaml`**: file di configurazione del modello per l'agente di supporto (`model`, `max_tokens`). Modificare questo file per cambiare modello o limiti senza toccare il codice.
- **`config/llm_models/loader.py`**: funzione `load_model_config(name)` e dataclass immutabile `LLMModelConfig`. Il sistema è estensibile: ogni agente avrà il proprio YAML identificato dal nome.
- **Test completi con mock** (nessuna chiamata reale a servizi esterni):
  - `backend/tests/tools/test_knowledge.py`
  - `backend/tests/tools/test_ticket.py`
  - `backend/tests/tools/test_escalation.py`
  - `backend/tests/agents/test_support_agent.py`
  - `backend/tests/api/test_agent.py`
  - `backend/tests/integrations/llm_interfaces/test_base_llm_interface.py` (riscritto)
  - `backend/tests/config/test_llm_models_loader.py`
  - `backend/tests/integrations/llm_interfaces/test_anthropic_interface.py`

### Changed

- `BaseLLMInterface.generate` → `BaseLLMInterface.chat` (breaking change interno; nessun codice esterno ne dipendeva).
- `backend/main.py`: registrato il nuovo router `/chat`.
- `AnthropicInterface`: rimosso `DEFAULT_MODEL` hardcodato; model e max_tokens vengono ora caricati da `support_agent.yaml` all'avvio. Entrambi restano sovrascrivibili via argomento per test e usi one-off.
- `get_llm_client()`: accetta `config_name` invece di `model`.

---

## 0.4.0 — 2026-04-21

### Added

- Sistema RAG completo: upload documenti, estrazione testo (PDF/DOCX/TXT/Markdown), chunking con overlap, embedding su Voyage AI (`voyage-3`, 1024 dim), salvataggio in pgvector e ricerca semantica multi-tenant.
- Nuova tabella `document_chunks` con indice HNSW su `embedding` ([migration 010](backend/database/migrations/010_document_chunks.sql)).
- Funzione SQL `match_document_chunks` per la ricerca top-K filtrata per `company_id` ([migration 012](backend/database/migrations/012_search_function.sql)).
- Vista SQL `documents_with_counts` per esporre il numero di chunk per documento ([migration 013](backend/database/migrations/013_documents_with_counts_view.sql)), esposto via `GET /documents` come campo `chunk_count`.
- Bucket Storage `documents` gestito dall'endpoint di upload con chiave `<company_id>/<document_id>/<filename>` per evitare collisioni quando due upload condividono lo stesso filename.
- Batching automatico in `VoyageEmbedding`: richieste spezzate in blocchi da 128 input (limite API Voyage), trasparente per i chiamanti.
- Interfaccia astratta `BaseEmbeddingInterface` e implementazione `VoyageEmbedding` (chiamata REST via `httpx`, per compatibilità con Python 3.14).
- Moduli `backend/rag/`: `text_extraction`, `chunking`, `ingestion`, `search`.
- Endpoint API: `POST /documents/upload`, `GET /documents`, `DELETE /documents/{id}`, `POST /rag/search` ([backend/api/documents.py](backend/api/documents.py)).
- Nuovi modelli Pydantic `DocumentChunkCreate` / `DocumentChunk`.
- Variabile `VOYAGE_API_KEY` in [Settings](backend/utils/config.py) e `.env.example`.
- Dipendenze: `pypdf`, `python-docx`, `python-multipart`.
- Test con mock completo dei servizi esterni: chunking, estrazione, ingestion, search, client Voyage, endpoint documenti/ricerca.
- Nuova documentazione [docs/rag.md](docs/rag.md); aggiornate [architecture](docs/architecture.md), [database](docs/database.md), [api_endpoints](docs/api_endpoints.md), [repo_structure](docs/repo_structure.md).

### Changed

- Rimossa la colonna `documents.embedding` ([migration 011](backend/database/migrations/011_drop_documents_embedding.sql)): gli embedding vivono ora su `document_chunks`.
- Timeout HTTP di `VoyageEmbedding` alzato da 30s a 60s (default) per supportare batch di chunk più grossi.

### Notes

- Il pacchetto ufficiale `voyageai` non supporta Python 3.14: usiamo la REST API direttamente, zero SDK aggiuntivo.

---

## 0.3.0 — 2026-04-21

### Added

- Schema del database come migration SQL versionate in [backend/database/migrations/](backend/database/migrations/): `companies`, `users`, `agent_configs`, `documents` (con colonna `embedding` per il futuro RAG), `conversations`, `messages`, `tickets`.
- Abilitazione delle estensioni PostgreSQL `vector` (pgvector) e `pgcrypto`.
- Bucket Supabase Storage privato `documents` per la knowledge base.
- Row Level Security attivata su tutte le tabelle applicative (il backend usa la service role key e bypassa RLS).
- Factory cached del client Supabase ([backend/database/supabase_client.py](backend/database/supabase_client.py)).
- Modelli Pydantic per tutte le tabelle con enum tipizzati ([backend/database/models.py](backend/database/models.py)).
- Test dei modelli e del client Supabase ([backend/tests/database/](backend/tests/database/)).
- Nuova documentazione: [docs/architecture.md](docs/architecture.md) (schema e scelte architetturali) e [docs/database.md](docs/database.md) (guida operativa alle migration).

---

## 0.2.0 — 2026-04-20

### Added

- Struttura iniziale della repo (`backend/`, `docs/`, `dev_support/`).
- Scaffolding del backend Python con FastAPI e endpoint `/health`.
- Sistema di configurazione tramite `pydantic-settings` e file `.env` ([backend/utils/config.py](backend/utils/config.py)).
- Sistema di logging centralizzato con output a console e file con rotazione ([backend/utils/logging_config.py](backend/utils/logging_config.py)).
- Classi astratte `BaseAgent` ([backend/agents/base_agent.py](backend/agents/base_agent.py)) e `BaseLLMInterface` ([backend/integrations/llm_interfaces/base_llm_interface.py](backend/integrations/llm_interfaces/base_llm_interface.py)) come fondamenta per agenti e integrazioni LLM.
- Configurazione `pytest` ([backend/pytest.ini](backend/pytest.ini)) e suite di test iniziale (health endpoint, settings, logging).
- Dipendenze Python di partenza ([backend/requirements.txt](backend/requirements.txt)).
- Documentazione iniziale: struttura repo, configurazione, sistema di logging.

---

## 0.1.0 — 2026-04-17

- Setup progetto iniziale.
