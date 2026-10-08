# Configurazione

Documento di riferimento per il sistema di configurazione del backend: variabili d'ambiente, file `.env`, classe `Settings` e cartella `config/` per configurazioni statiche.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [⚙️ Come funziona](#️-come-funziona)
- [🔧 Variabili d'ambiente](#-variabili-dambiente)
- [🚀 Setup iniziale](#-setup-iniziale)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

La configurazione del backend è divisa in due categorie:

- **Segreta / per ambiente** (chiavi API, URL di servizi, identità di sviluppo): gestita tramite variabili d'ambiente caricate dal file `.env`, mai committata su git.
- **Statica / non sensibile** (configurazione dei modelli LLM, prompt di sistema, ecc.): gestita tramite file dentro la cartella `backend/config/`, versionata insieme al codice.

---

## ⚙️ Come funziona

### Variabili d'ambiente

Le variabili d'ambiente sono caricate dal file `backend/.env` tramite [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). La classe `Settings` definita in [backend/utils/config.py](../backend/utils/config.py) espone ogni variabile come attributo tipizzato.

Per accedere alla configurazione dal codice si usa la funzione `get_settings()`, che restituisce un'istanza singleton (cacheata con `lru_cache`):

```python
from utils.config import get_settings

settings = get_settings()
api_key = settings.ANTHROPIC_API_KEY
```

### Cartella `config/`

La cartella [backend/config/](../backend/config/) ospita configurazioni statiche non sensibili, organizzate in sottocartelle per area:

- `llm_models/` — parametri dei modelli LLM (nome modello, temperature, max tokens, ecc.)
- `prompts/` — prompt di sistema per l'agente AI e i suoi tool

Entrambe le sottocartelle sono già popolate.

#### Configurazione modelli LLM (`llm_models/`)

Ogni agente ha il proprio file YAML in `backend/config/llm_models/`. Il loader (`loader.py`) legge il file, valida i campi e restituisce una dataclass immutabile `LLMModelConfig`.

Campi supportati:

| Campo        | Tipo     | Obbligatorio | Default  | Descrizione                                                                                                                                                                                                                                                                    |
|--------------|----------|--------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `model`      | `str`    | Sì           | —        | Identificatore del modello Claude (es. `claude-sonnet-5`).                                                                                                                                                                                                                     |
| `max_tokens` | `int`    | Sì           | —        | Numero massimo di token che il modello può generare per risposta.                                                                                                                                                                                                              |
| `effort`     | `str`    | No           | `high`   | Quanti token Claude spende per la risposta (testo, tool call ed eventuale thinking; non richiede il thinking attivo). Valori validi: `low`, `medium`, `high`, `xhigh`, `max`. Valori più bassi riducono latenza e costo; `high` equivale al comportamento di default dell'API. |

Esempio (`support_agent.yaml`):

```yaml
model: claude-sonnet-5
max_tokens: 4096
effort: low
```

Per customer support ad alto volume, `effort: low` è la scelta consigliata: riduce latenza e costo senza impatto significativo sulla qualità delle risposte.

---

## 🔧 Variabili d'ambiente

L'elenco completo delle variabili è visibile nel file [backend/.env.example](../backend/.env.example), che va copiato in `.env` e compilato con i valori reali.

| Variabile                   | Descrizione                                                                                                                                | Obbligatoria             |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| `ANTHROPIC_API_KEY`         | Chiave API per il provider LLM (Anthropic Claude).                                                                                         | Sì                       |
| `VOYAGE_API_KEY`            | Chiave API per Voyage AI (embedding RAG).                                                                                                  | Sì                       |
| `SUPABASE_URL`              | URL del progetto Supabase.                                                                                                                 | Sì                       |
| `SUPABASE_ANON_KEY`         | Chiave pubblica di Supabase, usata dal client frontend.                                                                                    | Sì                       |
| `SUPABASE_SERVICE_ROLE_KEY` | Chiave privata di Supabase, usata dal backend per operazioni privilegiate.                                                                 | Sì                       |
| `SUPABASE_SCHEMA`           | Schema del database in cui vivono tabelle, funzioni e view di Frontline. Va anche aggiunto in Supabase → Settings → API → Exposed schemas. | No (default `frontline`) |
| `DEV_COMPANY_ID`            | Identità dell'azienda usata in sviluppo quando la richiesta non ha `Authorization: Bearer`.                                                | Solo in dev              |
| `SSO_SHARED_SECRET`         | Secret condiviso col sito MDK-137. Serve a verificare il JWT di ingresso (`sso_token`). Stesso valore sui due progetti.                    | Sì in staging/prod       |
| `FRONTLINE_SESSION_SECRET`  | Secret solo di Frontline (mai condiviso col sito). Firma il token di sessione interno, durata 24 ore.                                      | Sì in staging/prod       |
| `KV_REST_API_URL`           | URL REST del database Upstash di Frontline. Serve a registrare i `jti` dei token SSO già usati. Senza questo valore l'SSO viene rifiutato. | Sì in staging/prod       |
| `KV_REST_API_TOKEN`         | Token privato dello stesso database Upstash. Non committare il valore reale. Senza questo valore l'SSO viene rifiutato.                    | Sì in staging/prod       |
| `FRONTEND_URL`              | Origine CORS permessa. Usare `*` in sviluppo; in produzione inserire l'URL esatto del frontend. Default: `*`.                              | No                       |
| `CHAT_RATE_LIMIT`           | Tetto richieste per IP sull'endpoint chat, formato `<numero>/<periodo>` (es. `20/minute`, `200/hour`).                                     | No (default `20/minute`) |
| `TRUST_PROXY_HEADERS`       | Se `true`, l'IP usato per il rate limiting è letto da `X-Forwarded-For`. Attivare solo dietro un reverse proxy fidato.                     | No (default `false`)     |
| `LOG_LEVEL`                 | Livello minimo di log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).                                                                   | No (default `INFO`)      |

> **Attenzione**: il file `.env` contiene dati sensibili e non deve mai essere committato. È escluso dal controllo versione tramite `.gitignore`.

---

## 🚀 Setup iniziale

1. Dalla cartella `backend/`, copiare il template:

   ```bash
   cp .env.example .env
   ```

2. Aprire `.env` con un editor e sostituire i valori placeholder con le chiavi reali.

3. Verificare il caricamento avviando l'applicazione (i valori vengono validati all'avvio):

   ```bash
   uvicorn main:app --reload
   ```

Se una variabile obbligatoria è assente o malformata, l'avvio fallisce con un messaggio d'errore esplicito.

---

## 📚 Riferimenti

- **Codice**: [backend/utils/config.py](../backend/utils/config.py)
- **Test**: [backend/tests/utils/test_config.py](../backend/tests/utils/test_config.py)
- **Template `.env`**: [backend/.env.example](../backend/.env.example)
- **Doc correlati**: [Sistema di logging](observability.md), [Struttura della repo](repo_structure.md)
- **Risorse esterne**: [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
