# Struttura repo

📁 mdk_frontline/
 │
 ├── 📁 .venv/                                               # Ambiente virtuale con tutte le dipendenze installate.
 │
 ├── 📁 config/                                              # Configurazioni.
 │    ├── 📁 llm_models/                                     # Configurazione dei modelli IA (model, temperature, max token, ecc.).
 │    └── 📁 prompts/                                        # Configurazione dei prompt.
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
 │    ├── 📄 observability.md                                # Sistema di logging
 │    ├── 📄 repo_structure.md                               # Struttura e spiegazione della repo.
 │    └── 📄 TEMPLATE.md                                     # Template standard per la documentazione del progetto.
 │
 ├── 📁 logs/
 │
 ├── 📁 src/                                                 # Cartella contenente il codice sorgente del progetto.
 │    ├── 📁 agents/                                         # Agenti.
 │    │    └── 📄 base_agent.py                              # Base class comune per tutti gli agenti.
 │    ├── 📁 core/                                           #
 │    ├── 📁 integrations/                                   # Integrazione delle API esterne
 │    │    └── 📁 llm_interfaces/                            # Interfaccia verso i modelli LLM.
 │    │         └── 📄 base_llm_interface.py                 # Interfaccia astratta (classe base) per garantire che tutti i modelli LLM abbiano gli stessi metodi standard.
 │    ├── 📁 utils/                                          # Utility comuni e configurazione.
 │    │    ├── 📄 config.py                                  # Caricamento e gestione delle variabili d'ambiente dal file .env.
 │    │    └── 📄 logging_config.py                          # Configurazione centralizzata del logging (console e file, rotazione, formato).
 │    └── 📄 test_logging_config.py
 │
 ├── 📁 tests/                                               # Test automatici per tutte le funzioni e i moduli.
 │    ├── 📁 agents/                                         # Test degli agenti.
 │    │    └── 📄 test_base_agent.py
 │    ├── 📁 core/                                           #
 │    ├── 📁 api/                                            # Test delle integrazioni.
 │    │    └── 📁 llm_interfaces/
 │    │         └── 📄 test_base_llm_interface.py
 │    └── 📁 utils/                                          # Test delle utility.
 │         ├── 📄 test_config.py
 │         └── 📄 test_logging_config.py
 │
 ├── 📄 .env                                                 # Contiene le chiavi API e variabili d'ambiente riservate.
 ├── 📄 .env.example                                         # Contiene un esempio delle variabili d’ambiente in uso.
 ├── 📄 .gitignore                                           # Elenco dei file e delle cartelle esclusi dal controllo di versione.
 ├── 📄 CHANGELOG.md                                         # Storico versioni e modifiche del progetto.
 ├── 📄 README.md                                            # Panoramica, istruzioni e info rapide sul progetto.
 └── 📄 requirements.txt                                     # Elenco delle dipendenze Python e relative versioni.
