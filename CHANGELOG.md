<!-- markdownlint-disable -->
# 📋 Changelog

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
- Timeout HTTP di `VoyageEmbedding` alzato da 30s a 60s (default) per supportare batch di chunk piu' grossi.

### Notes

- Il pacchetto ufficiale `voyageai` non supporta Python 3.14: usiamo la REST API direttamente, zero SDK aggiuntivo.

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

## 0.1.0 — 2026-04-17

- Setup progetto iniziale.
