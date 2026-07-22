# Database Supabase

Guida operativa al database Supabase di MDK Frontline: come applicare le migration, struttura delle tabelle e regole di accesso.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [🚀 Avvio rapido: applicare le migration](#-avvio-rapido-applicare-le-migration)
- [⚙️ Come funziona](#️-come-funziona)
- [🔒 Sicurezza](#-sicurezza)
- [🧪 Testing](#-testing)
- [🔍 Troubleshooting](#-troubleshooting)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

Il database è su **Supabase** (PostgreSQL gestito). Lo schema è definito come file SQL versionati in [backend/database/migrations/](../backend/database/migrations/). Nell'MVP le migration si applicano **manualmente** dal SQL Editor di Supabase.

Tutti gli oggetti di Frontline (tabelle, funzioni, view) vivono in uno **schema dedicato `frontline`**, così lo schema `public` resta libero per un futuro secondo prodotto. Il backend punta a questo schema tramite la variabile `SUPABASE_SCHEMA` (default `frontline`). L'estensione `vector` (pgvector) vive in un secondo schema dedicato, **`extensions`**: `public` è quindi completamente vuoto. Lo Storage dei file non è coinvolto: usa lo schema `storage`, separato.

Il backend si connette con la **service role key** (chiave privata), che bypassa la Row Level Security. L'isolamento tra aziende clienti è garantito filtrando sempre per `company_id` a livello applicativo.

---

## 🚀 Avvio rapido: applicare le migration

La **prima volta** (o quando si aggiunge una nuova migration):

1. Apri il progetto Supabase nel browser.
2. Vai su **SQL Editor** → **New query**.
3. Apri i file in [backend/database/migrations/](../backend/database/migrations/) **in ordine numerico** (001, 002, 003, ...).
4. Per ogni file: copia tutto il contenuto, incollalo nel SQL Editor, clicca **Run**.
5. Verifica che non ci siano errori prima di passare al file successivo.

> ⚠️ L'ordine è importante: `002_companies.sql` deve esistere prima di `004_agent_configs.sql` (che ha una foreign key verso `companies`), e così via.

Dopo l'esecuzione puoi controllare il risultato dalla sezione **Table Editor** (seleziona lo schema `frontline` dal menù a tendina in alto).

> ⚠️ **Exposed schemas**: dopo aver creato lo schema `frontline`, vai su **Settings → API → Exposed schemas** e aggiungi `frontline` alla lista (accanto a `public`, `graphql_public`). Salva: PostgREST ricarica lo schema. Senza questo passo il backend non riesce a leggere/scrivere le tabelle.

---

## ⚙️ Come funziona

### Schema

Tutti gli oggetti di Frontline vivono nello schema **`frontline`**: le 8 tabelle, la funzione `match_document_chunks`, la funzione trigger `set_updated_at` e la view `documents_with_counts`. L'estensione `vector` vive nello schema **`extensions`**. Lo schema `public` resta completamente vuoto e pronto per un futuro secondo prodotto. Il backend sa a quale schema puntare grazie alla variabile `SUPABASE_SCHEMA` (vedi [config.md](config.md#-variabili-dambiente)); `extensions` non va aggiunto agli "Exposed schemas" perché il backend non lo interroga mai direttamente (l'operatore vettoriale è usato solo dentro `match_document_chunks`, che vive in `frontline`).

### Tabelle

| Tabella           | Descrizione                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `companies`       | Aziende clienti (tenant). `slug` unico per l'URL della chat pubblica.       |
| `agent_configs`   | Configurazione agente per azienda (nome, logo, colore, tono, lingua).       |
| `documents`       | Metadata dei documenti + riferimento allo Storage.                          |
| `document_chunks` | Chunk di testo con embedding `vector(1024)` per la ricerca semantica (RAG). |
| `conversations`   | Conversazioni della live chat.                                              |
| `messages`        | Messaggi delle conversazioni (`customer` / `agent` / `system`).             |
| `tickets`         | Ticket aperti dall'agente per casi non risolvibili o escalation.            |

### Estensioni

- `vector` (pgvector) — installato nello schema `extensions`, usato dalla tabella `document_chunks` per la ricerca semantica (indice HNSW, cosine distance).
- `pgcrypto` — per `gen_random_uuid()` usato nelle primary key.

### Funzioni SQL

- `match_document_chunks(query_embedding, match_company_id, match_count)` — restituisce i top-K chunk più simili alla query per la company specificata (cosine similarity). Definita in [012_search_function.sql](../backend/database/migrations/012_search_function.sql).

### Storage

Bucket **privato** `documents` creato da [009_storage.sql](../backend/database/migrations/009_storage.sql). I file vengono salvati in `<company_id>/<document_id>/<filename>` per separare i tenant e prevenire collisioni tra file con lo stesso nome.

### Diagramma

Vedi il diagramma ER in [architecture.md](architecture.md#️-schema-del-database).

---

## 🔒 Sicurezza

- **Row Level Security** attivata su tutte le tabelle applicative.
- **Nessuna policy per `anon` / `authenticated`** nell'MVP → il frontend **non** parla direttamente col DB: tutto passa dal backend.
- **Service role key**: usata solo dal backend (`backend/.env`). Non va mai esposta al frontend, commitata su Git o condivisa via chat.
- **Isolamento applicativo**: ogni query backend filtra per `company_id` (nell'MVP arriva dalla variabile `DEV_COMPANY_ID`).

---

## 🧪 Testing

Test dei modelli Pydantic e del client Supabase:

```bash
cd backend
pytest tests/database -v
```

I test **non** toccano il database reale: i modelli sono validati in locale e il client è testato con `monkeypatch` sulle settings.

---

## 🔍 Troubleshooting

### Problema: `extension "vector" is not available`

**Causa**: l'estensione pgvector non è abilitata sul progetto Supabase.
**Soluzione**: in Supabase, vai su **Database → Extensions** e abilita `vector`, oppure esegui `001_enable_extensions.sql` dal SQL Editor (il comando `create extension if not exists` dovrebbe bastare sui progetti moderni).

### Problema: `RuntimeError: Supabase is not configured`

**Causa**: `SUPABASE_URL` o `SUPABASE_SERVICE_ROLE_KEY` non sono valorizzate in `backend/.env`.
**Soluzione**: copia i valori dal dashboard Supabase (**Project Settings → API**) e incollali in `backend/.env`. Riavvia il processo.

### Problema: il backend non trova le tabelle (`relation ... does not exist` o `404` da PostgREST)

**Causa**: lo schema `frontline` non è tra gli "Exposed schemas" di Supabase, oppure `SUPABASE_SCHEMA` in `backend/.env` non è impostata su `frontline`.
**Soluzione**: aggiungi `frontline` in **Settings → API → Exposed schemas** e verifica che `SUPABASE_SCHEMA=frontline` sia presente in `backend/.env`. Riavvia il backend.

### Problema: `foreign key violation` durante una migration

**Causa**: le migration sono state eseguite fuori ordine.
**Soluzione**: rieseguile in ordine numerico. I `create table if not exists` sono idempotenti, quindi ri-eseguire i file già applicati non crea problemi.

---

## 📚 Riferimenti

- **Migration SQL**: [backend/database/migrations/](../backend/database/migrations/)
- **Client Supabase**: [backend/database/supabase_client.py](../backend/database/supabase_client.py)
- **Modelli Pydantic**: [backend/database/models.py](../backend/database/models.py)
- **Test**: [backend/tests/database/](../backend/tests/database/)
- **Doc correlati**: [architecture.md](architecture.md), [config.md](config.md)
- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)
