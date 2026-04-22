# Struttura repo

📁 mdk_frontline/
 │
 ├── 📁 backend/                                             # Codice sorgente del backend (Python + FastAPI).
 │    ├── 📁 .venv/                                          # Ambiente virtuale con tutte le dipendenze installate.
 │    ├── 📁 agents/                                         # Agenti AI e relativa logica.
 │    │    └── 📄 base_agent.py                              # Base class comune per tutti gli agenti.
 │    ├── 📁 api/                                            # Endpoint HTTP esposti dal backend verso il frontend.
 │    │    └── 📄 documents.py                               # Endpoint /documents/* e /rag/search.
 │    ├── 📁 config/                                         # Configurazioni.
 │    │    ├── 📁 llm_models/                                # Configurazione dei modelli IA (model, temperature, max token, ecc.).
 │    │    └── 📁 prompts/                                   # Configurazione dei prompt.
 │    ├── 📁 core/                                           # Logica di business trasversale e orchestrazione degli agenti.
 │    ├── 📁 database/                                       # Modelli dati (Pydantic), client Supabase e migration SQL delle tabelle.
 │    │    ├── 📁 migrations/                                # Migration SQL da eseguire manualmente nel SQL Editor di Supabase (in ordine numerico).
 │    │    │    ├── 📄 001_enable_extensions.sql             # Abilita le estensioni PostgreSQL (pgvector, pgcrypto).
 │    │    │    ├── 📄 002_companies.sql                     # Tabella companies (tenant).
 │    │    │    ├── 📄 003_users.sql                         # Tabella users (utenti dashboard, predisposta per il futuro).
 │    │    │    ├── 📄 004_agent_configs.sql                 # Tabella agent_configs (configurazione agente per azienda).
 │    │    │    ├── 📄 005_documents.sql                     # Tabella documents (knowledge base) con colonna embedding per il RAG.
 │    │    │    ├── 📄 006_conversations.sql                 # Tabella conversations (live chat).
 │    │    │    ├── 📄 007_messages.sql                      # Tabella messages (messaggi dentro le conversazioni).
 │    │    │    ├── 📄 008_tickets.sql                       # Tabella tickets (casi non risolvibili / escalation).
 │    │    │    ├── 📄 009_storage.sql                       # Bucket Supabase Storage "documents" privato.
 │    │    │    ├── 📄 010_document_chunks.sql               # Tabella document_chunks con embedding vector(1024) per il RAG.
 │    │    │    ├── 📄 011_drop_documents_embedding.sql      # Rimuove la colonna embedding da documents (ora vive su document_chunks).
 │    │    │    ├── 📄 012_search_function.sql               # Funzione SQL match_document_chunks per la ricerca semantica multi-tenant.
 │    │    │    └── 📄 013_documents_with_counts_view.sql    # Vista documents_with_counts che espone il numero di chunk per documento.
 │    │    ├── 📄 models.py                                  # Modelli Pydantic che rappresentano le tabelle del database.
 │    │    └── 📄 supabase_client.py                         # Factory cached del client Supabase (service role).
 │    ├── 📁 integrations/                                   # Integrazione delle API esterne.
 │    │    ├── 📁 embedding_interfaces/                      # Interfaccia verso i provider di embedding.
 │    │    │    ├── 📄 base_embedding_interface.py           # Interfaccia astratta per i provider di embedding.
 │    │    │    └── 📄 voyage_embedding.py                   # Implementazione Voyage AI via REST (httpx).
 │    │    └── 📁 llm_interfaces/                            # Interfaccia verso i modelli LLM.
 │    │         └── 📄 base_llm_interface.py                 # Interfaccia astratta (classe base) per garantire che tutti i modelli LLM abbiano gli stessi metodi standard.
 │    ├── 📁 logs/                                           # File di log generati a runtime.
 │    ├── 📁 rag/                                            # Sistema RAG: processing dei documenti, embeddings e ricerca semantica.
 │    │    ├── 📄 text_extraction.py                         # Estrazione del testo da PDF, DOCX, TXT, Markdown.
 │    │    ├── 📄 chunking.py                                # Suddivisione del testo in chunk con overlap.
 │    │    ├── 📄 ingestion.py                               # Pipeline end-to-end: upload -> estrai -> chunka -> embedda -> salva.
 │    │    └── 📄 search.py                                  # Ricerca semantica sui chunk tramite match_document_chunks.
 │    ├── 📁 tests/                                          # Test automatici per tutte le funzioni e i moduli.
 │    │    ├── 📁 agents/                                    # Test degli agenti.
 │    │    │    └── 📄 test_base_agent.py
 │    │    ├── 📁 api/                                       # Test degli endpoint HTTP.
 │    │    ├── 📁 core/                                      # Test della logica di business e orchestrazione.
 │    │    ├── 📁 database/                                  # Test dei modelli dati e del client Supabase.
 │    │    │    ├── 📄 test_models.py                        # Test dei modelli Pydantic del database.
 │    │    │    └── 📄 test_supabase_client.py               # Test del client Supabase.
 │    │    ├── 📁 integrations/                              # Test delle integrazioni.
 │    │    │    └── 📁 llm_interfaces/
 │    │    │         └── 📄 test_base_llm_interface.py
 │    │    ├── 📁 rag/                                       # Test del sistema RAG.
 │    │    │    ├── 📄 test_chunking.py
 │    │    │    ├── 📄 test_text_extraction.py
 │    │    │    ├── 📄 test_ingestion.py
 │    │    │    └── 📄 test_search.py
 │    │    ├── 📁 tools/                                     # Test dei tool dell'agente.
 │    │    ├── 📁 utils/                                     # Test delle utility.
 │    │    │    ├── 📄 test_config.py
 │    │    │    └── 📄 test_logging_config.py
 │    │    └── 📄 test_main.py                               # Test del punto di ingresso dell'applicazione.
 │    ├── 📁 tools/                                          # Tool che l'agente AI puo invocare autonomamente (knowledge, ticket, escalation).
 │    ├── 📁 utils/                                          # Utility comuni e configurazione.
 │    │    ├── 📄 config.py                                  # Caricamento e gestione delle variabili d'ambiente dal file .env.
 │    │    └── 📄 logging_config.py                          # Configurazione centralizzata del logging (console e file, rotazione, formato).
 │    ├── 📄 .env                                            # Contiene le chiavi API e variabili d'ambiente riservate.
 │    ├── 📄 .env.example                                    # Contiene un esempio delle variabili d’ambiente in uso.
 │    ├── 📄 main.py                                         # Punto di ingresso del backend: inizializza FastAPI, registra endpoint e middleware.
 │    ├── 📄 pytest.ini                                      #
 │    └── 📄 requirements.txt                                # Elenco delle dipendenze Python e relative versioni.
 │
 ├── 📁 dev_support/                                         # Materiale di supporto.
 │    ├── 📄 notes.md
 │    ├── 📄 to_do_list.md
 │    └── 📄 whiteboard.md
 │
 ├── 📁 docs/                                                # Documentazione operativa e tecnica.
 │    ├── 📄 api_endpoints.md                                # Contiene l'elenco degli endpoint API utilizzati.
 │    ├── 📄 architecture.md                                 # Architettura sistema, stack e schema del database.
 │    ├── 📄 database.md                                     # Guida operativa alle migration Supabase e allo schema.
 │    ├── 📄 rag.md                                          # Guida al sistema RAG (upload, chunking, embedding, ricerca).
 │    ├── 📄 config.md                                       # Guida alla configurazione
 │    ├── 📄 decison_logic.md                                #
 │    ├── 📄 deploy.md                                       #
 │    ├── 📄 observability.md                                # Sistema di logging
 │    ├── 📄 repo_structure.md                               # Struttura e spiegazione della repo.
 │    └── 📄 TEMPLATE.md                                     # Template standard per la documentazione del progetto.
 │
 ├── 📁 frontend/                                            # Codice sorgente del frontend (Next.js + shadcn/ui): dashboard aziendale e pagina di live chat.
 │
 ├── 📄 .gitignore                                           # Elenco dei file e delle cartelle esclusi dal controllo di versione.
 ├── 📄 CHANGELOG.md                                         # Storico versioni e modifiche del progetto.
 └── 📄 README.md                                            # Panoramica, istruzioni e info rapide sul progetto.
