# Struttura repo

📁 mdk_frontline/
 │
 ├── 📁 backend/                                             # Codice sorgente del backend (Python + FastAPI).
 │    ├── 📁 .venv/                                          # Ambiente virtuale con tutte le dipendenze installate.
 │    ├── 📁 agents/                                         # Agenti AI e relativa logica.
 │    │    └── 📄 base_agent.py                              # Base class comune per tutti gli agenti.
 │    ├── 📁 api/                                            # Endpoint HTTP esposti dal backend verso il frontend.
 │    ├── 📁 config/                                         # Configurazioni.
 │    │    ├── 📁 llm_models/                                # Configurazione dei modelli IA (model, temperature, max token, ecc.).
 │    │    └── 📁 prompts/                                   # Configurazione dei prompt.
 │    ├── 📁 core/                                           # Logica di business trasversale e orchestrazione degli agenti.
 │    ├── 📁 database/                                       # Modelli dati (Pydantic), client Supabase e migration SQL delle tabelle.
 │    ├── 📁 integrations/                                   # Integrazione delle API esterne.
 │    │    └── 📁 llm_interfaces/                            # Interfaccia verso i modelli LLM.
 │    │         └── 📄 base_llm_interface.py                 # Interfaccia astratta (classe base) per garantire che tutti i modelli LLM abbiano gli stessi metodi standard.
 │    ├── 📁 logs/                                           # File di log generati a runtime.
 │    ├── 📁 rag/                                            # Sistema RAG: processing dei documenti, embeddings e ricerca semantica.
 │    ├── 📁 tests/                                          # Test automatici per tutte le funzioni e i moduli.
 │    │    ├── 📁 agents/                                    # Test degli agenti.
 │    │    │    └── 📄 test_base_agent.py
 │    │    ├── 📁 api/                                       # Test degli endpoint HTTP.
 │    │    ├── 📁 core/                                      # Test della logica di business e orchestrazione.
 │    │    ├── 📁 database/                                  # Test dei modelli dati e del client Supabase.
 │    │    ├── 📁 integrations/                              # Test delle integrazioni.
 │    │    │    └── 📁 llm_interfaces/
 │    │    │         └── 📄 test_base_llm_interface.py
 │    │    ├── 📁 rag/                                       # Test del sistema RAG.
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
 │    ├── 📄 architecture.md                                 # Architettura sistema e tech stack.
 │    ├── 📄 config.md                                       # Guida alla configurazione
 │    ├── 📄 decison_logic.md                                #
 │    ├── 📄 deploy.md                                       #
 │    ├── 📄 hierarchy_and_roles.md                          #
 │    ├── 📄 observability.md                                # Sistema di logging
 │    ├── 📄 repo_structure.md                               # Struttura e spiegazione della repo.
 │    └── 📄 TEMPLATE.md                                     # Template standard per la documentazione del progetto.
 │
 ├── 📁 frontend/                                            # Codice sorgente del frontend (Next.js + shadcn/ui): dashboard aziendale e pagina di live chat.
 │
 ├── 📄 .gitignore                                           # Elenco dei file e delle cartelle esclusi dal controllo di versione.
 ├── 📄 CHANGELOG.md                                         # Storico versioni e modifiche del progetto.
 └── 📄 README.md                                            # Panoramica, istruzioni e info rapide sul progetto.
