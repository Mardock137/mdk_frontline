<!-- markdownlint-disable -->
# 📋 Changelog

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
