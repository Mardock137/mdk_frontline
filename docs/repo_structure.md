# Struttura repo

📁 mdk_frontline/
 │
 ├── 📁 backend/                                             # Codice sorgente del backend (Python + FastAPI).
 │    ├── 📁 .venv/                                          # Ambiente virtuale con tutte le dipendenze installate.
 │    ├── 📁 agents/                                         # Agenti AI e relativa logica.
 │    │    ├── 📄 base_agent.py                              # Base class comune per tutti gli agenti.
 │    │    └── 📄 support_agent.py                           # Agente AI di supporto: loop autonomo con tool calling, salva messaggi nel DB.
 │    ├── 📁 api/                                            # Endpoint HTTP esposti dal backend verso il frontend.
 │    │    ├── 📄 agent.py                                   # Endpoint POST /chat/{company_slug}/message.
 │    │    ├── 📄 config.py                                  # Endpoint pubblico GET /chat/{company_slug}/config (branding + welcome).
 │    │    ├── 📄 dashboard.py                               # Endpoint /dashboard/*: ticket, agent-config, stats.
 │    │    └── 📄 documents.py                               # Endpoint /documents/* e /rag/search.
 │    ├── 📁 config/                                         # Configurazioni.
 │    │    ├── 📁 llm_models/                                # Configurazione dei modelli IA per ogni agente.
 │    │    │    ├── 📄 loader.py                             # Loader YAML: legge e valida LLMModelConfig (model, max_tokens).
 │    │    │    └── 📄 support_agent.yaml                    # Parametri del modello per l'agente di supporto (model, max_tokens).
 │    │    └── 📁 prompts/
 │    │         └── 📄 support_agent.py                      # Template del system prompt: identità agente, tono, istruzioni tool.
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
 │    │    │    ├── 📄 013_documents_with_counts_view.sql    # Vista documents_with_counts che espone il numero di chunk per documento.
 │    │    │    └── 📄 014_tickets_add_is_escalation.sql     # Aggiunge colonna is_escalation (boolean) alla tabella tickets.
 │    │    ├── 📄 models.py                                  # Modelli Pydantic che rappresentano le tabelle del database.
 │    │    └── 📄 supabase_client.py                         # Factory cached del client Supabase (service role).
 │    ├── 📁 integrations/                                   # Integrazione delle API esterne.
 │    │    ├── 📁 embedding_interfaces/                      # Interfaccia verso i provider di embedding.
 │    │    │    ├── 📄 base_embedding_interface.py           # Interfaccia astratta per i provider di embedding.
 │    │    │    └── 📄 voyage_embedding.py                   # Implementazione Voyage AI via REST (httpx).
 │    │    └── 📁 llm_interfaces/                            # Interfaccia verso i modelli LLM.
 │    │         ├── 📄 base_llm_interface.py                 # Interfaccia astratta con metodo chat(messages, system, tools); dataclass ChatResponse e ToolUse.
 │    │         └── 📄 anthropic_interface.py                # Adapter concreto per Anthropic Claude con tool calling (usa AsyncAnthropic SDK).
 │    ├── 📁 logs/                                           # File di log generati a runtime.
 │    ├── 📁 rag/                                            # Sistema RAG: processing dei documenti, embeddings e ricerca semantica.
 │    │    ├── 📄 chunking.py                                # Suddivisione del testo in chunk con overlap.
 │    │    ├── 📄 ingestion.py                               # Pipeline end-to-end: upload -> estrai -> chunka -> embedda -> salva.
 │    │    ├── 📄 search.py                                  # Ricerca semantica sui chunk tramite match_document_chunks.
 │    │    └── 📄 text_extraction.py                         # Estrazione del testo da PDF, DOCX, TXT, Markdown.
 │    ├── 📁 tests/                                          # Test automatici per tutte le funzioni e i moduli.
 │    │    ├── 📄 conftest.py                                # Fixture condivise tra tutti i test (company_id, conversation_id).
 │    │    ├── 📁 agents/                                    # Test degli agenti.
 │    │    │    ├── 📄 test_base_agent.py
 │    │    │    └── 📄 test_support_agent.py                 # Test del loop dell'agente (LLM e tool mockati).
 │    │    ├── 📁 api/                                       # Test degli endpoint HTTP.
 │    │    │    ├── 📄 test_agent.py                         # Test endpoint /chat/{slug}/message (Supabase e agente mockati).
 │    │    │    ├── 📄 test_config.py                        # Test endpoint /chat/{slug}/config (Supabase mockato).
 │    │    │    ├── 📄 test_dashboard.py                     # Test endpoint /dashboard/* (13 test, Supabase mockato).
 │    │    │    └── 📄 test_documents.py
 │    │    ├── 📁 config/                                    # Test della configurazione.
 │    │    │    └── 📄 test_llm_models_loader.py             # Test del loader YAML (happy path, errori, validazione).
 │    │    ├── 📁 core/                                      # Test della logica di business e orchestrazione.
 │    │    ├── 📁 database/                                  # Test dei modelli dati e del client Supabase.
 │    │    │    ├── 📄 test_models.py                        # Test dei modelli Pydantic del database.
 │    │    │    └── 📄 test_supabase_client.py               # Test del client Supabase.
 │    │    ├── 📁 integrations/                              # Test delle integrazioni.
 │    │    │    ├── 📁 embedding_interfaces/
 │    │    │    │    └── 📄 test_voyage_embedding.py
 │    │    │    └── 📁 llm_interfaces/
 │    │    │         ├── 📄 test_base_llm_interface.py       # Test interfaccia base, ChatResponse e ToolUse.
 │    │    │         └── 📄 test_anthropic_interface.py      # Test AnthropicInterface con YAML e SDK mockati.
 │    │    ├── 📁 rag/                                       # Test del sistema RAG.
 │    │    │    ├── 📄 test_chunking.py
 │    │    │    ├── 📄 test_ingestion.py
 │    │    │    ├── 📄 test_search.py
 │    │    │    └── 📄 test_text_extraction.py
 │    │    ├── 📁 tools/                                     # Test dei tool dell'agente.
 │    │    │    ├── 📄 test_escalation.py                    # Test escalate (Supabase mockato).
 │    │    │    ├── 📄 test_knowledge.py                     # Test search_knowledge (search_chunks mockato).
 │    │    │    └── 📄 test_ticket.py                        # Test create_ticket (Supabase mockato).
 │    │    ├── 📁 utils/                                     # Test delle utility.
 │    │    │    ├── 📄 test_config.py
 │    │    │    └── 📄 test_logging_config.py
 │    │    └── 📄 test_main.py                               # Test del punto di ingresso dell'applicazione.
 │    ├── 📁 tools/                                          # Tool che l'agente AI può invocare autonomamente.
 │    │    ├── 📄 knowledge.py                               # Tool search_knowledge: ricerca semantica sulla KB.
 │    │    ├── 📄 ticket.py                                  # Tool create_ticket: crea ticket di supporto nel DB.
 │    │    └── 📄 escalation.py                              # Tool escalate: crea ticket di escalation e aggiorna stato conversazione.
 │    ├── 📁 utils/                                          # Utility comuni e configurazione.
 │    │    ├── 📄 config.py                                  # Caricamento e gestione delle variabili d'ambiente dal file .env.
 │    │    └── 📄 logging_config.py                          # Configurazione centralizzata del logging (console e file, rotazione, formato).
 │    ├── 📄 .env                                            # Contiene le chiavi API e variabili d'ambiente riservate.
 │    ├── 📄 .env.example                                    # Contiene un esempio delle variabili d’ambiente in uso.
 │    ├── 📄 main.py                                         # Punto di ingresso del backend: inizializza FastAPI, registra endpoint e middleware.
 │    ├── 📄 pytest.ini                                      #
 │    └── 📄 requirements.txt                                # Elenco delle dipendenze Python e relative versioni.
 │
 ├── 📁 dev_support/                                         # Materiale di supporto (Non è documentazione).
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
 │    ├── 📄 frontend.md                                     #
 │    ├── 📄 observability.md                                # Sistema di logging
 │    ├── 📄 repo_structure.md                               # Struttura e spiegazione della repo.
 │    └── 📄 TEMPLATE.md                                     # Template standard per la documentazione del progetto.
 │
 ├── 📁 frontend/                                            # Codice sorgente del frontend (Next.js 16 + Tailwind CSS v4).
 │    ├── 📁 app/                                            # App Router di Next.js.
 │    │    ├── 📁 chat/
 │    │    │    └── 📁 [slug]/
 │    │    │         └── 📄 page.tsx                         # Pagina pubblica di live chat: carica config, mostra welcome, gestisce conversazione.
 │    │    ├── 📁 dashboard/                                 # Dashboard aziendale (admin area, usa DEV_COMPANY_ID).
 │    │    │    ├── 📁 config/
 │    │    │    │    └── 📄 page.tsx                         # Form modifica agent_name, colore, tono, lingua, welcome message.
 │    │    │    ├── 📁 documents/
 │    │    │    │    └── 📄 page.tsx                         # Upload, lista e cancellazione documenti.
 │    │    │    ├── 📁 stats/
 │    │    │    │    └── 📄 page.tsx                         # Stat card: conversazioni, ticket per stato, escalation aperti.
 │    │    │    ├── 📁 tickets/
 │    │    │    │    └── 📄 page.tsx                         # Lista ticket con badge stato/escalation e cambio stato.
 │    │    │    ├── 📄 layout.tsx                            # Layout con sidebar di navigazione (Documenti/Ticket/Config/Stats).
 │    │    │    └── 📄 page.tsx                              # Redirect automatico a /dashboard/documents.
 │    │    ├── 📄 globals.css                                # Stili globali (Tailwind v4).
 │    │    ├── 📄 layout.tsx                                 # Root layout dell'app.
 │    │    └── 📄 page.tsx                                   # Home page placeholder.
 │    ├── 📁 components/
 │    │    ├── 📁 chat/
 │    │    │    ├── 📄 ChatWindow.tsx                        # Contenitore messaggi con scroll automatico.
 │    │    │    ├── 📄 MessageBubble.tsx                     # Bolla singolo messaggio (agente / cliente).
 │    │    │    ├── 📄 MessageInput.tsx                      # Textarea + pulsante invia.
 │    │    │    └── 📄 TypingIndicator.tsx                   # Animazione "sta scrivendo...".
 │    │    └── 📁 ui/                                        # Componenti UI riutilizzabili (stile shadcn/ui, Tailwind v4).
 │    │         ├── 📄 badge.tsx                             # Badge colorato per stati (success/warning/error/info).
 │    │         ├── 📄 button.tsx                            # Button con varianti (default/outline/ghost/destructive/link).
 │    │         ├── 📄 card.tsx                              # Card con Header, Title, Description, Content, Footer.
 │    │         ├── 📄 dialog.tsx                            # Modal dialog con overlay e chiusura via ESC.
 │    │         ├── 📄 input.tsx                             # Input testuale stilizzato.
 │    │         ├── 📄 label.tsx                             # Label per form.
 │    │         ├── 📄 select.tsx                            # Select dropdown con icona chevron.
 │    │         ├── 📄 table.tsx                             # Table semantica con stile Tailwind.
 │    │         ├── 📄 textarea.tsx                          # Textarea stilizzata.
 │    │         └── 📄 toast.tsx                             # Toast notification: ToastProvider + hook useToast().
 │    ├── 📁 lib/
 │    │    ├── 📄 api.ts                                     # Tutte le chiamate al backend (chat, documenti, dashboard).
 │    │    └── 📄 utils.ts                                   # Utility cn() per classi Tailwind condizionali.
 │    ├── 📄 .env.local                                      # Variabili d'ambiente locali (NEXT_PUBLIC_API_URL).
 │    ├── 📄 .env.local.example                              # Esempio di variabili d'ambiente frontend.
 │    ├── 📄 next.config.ts                                  # Configurazione Next.js.
 │    ├── 📄 package.json                                    # Dipendenze e script npm.
 │    ├── 📄 postcss.config.mjs                              # Configurazione PostCSS per Tailwind v4.
 │    └── 📄 tsconfig.json                                   # Configurazione TypeScript.
 │
 ├── 📄 .gitignore                                           # Elenco dei file e delle cartelle esclusi dal controllo di versione.
 ├── 📄 CHANGELOG.md                                         # Storico versioni e modifiche del progetto.
 └── 📄 README.md                                            # Panoramica, istruzioni e info rapide sul progetto.
