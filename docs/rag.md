<!-- markdownlint-disable -->
# Sistema RAG

Guida operativa al sistema RAG (Retrieval-Augmented Generation) di MDK Frontline: come vengono processati i documenti caricati e come funziona la ricerca semantica.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [⚙️ Come funziona](#️-come-funziona)
- [🔧 Configurazione](#-configurazione)
- [🚀 Avvio rapido](#-avvio-rapido)
- [🧪 Testing](#-testing)
- [🔍 Troubleshooting](#-troubleshooting)
- [⚠️ Note MVP](#️-note-mvp)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

Il sistema RAG permette a ogni azienda cliente di:

1. **Caricare documenti** (PDF, DOCX, TXT, Markdown) tramite la dashboard.
2. Averli **indicizzati automaticamente**: estrazione del testo, divisione in pezzi ("chunk"), calcolo degli embedding, salvataggio.
3. Eseguire **ricerche semantiche** sulla knowledge base: data una domanda, il sistema ritorna i chunk più rilevanti.

La ricerca semantica è già integrata come **tool** dell'agente AI (`search_knowledge`): quando un cliente fa una domanda, l'agente la usa autonomamente per trovare le risposte nella knowledge base. L'endpoint `/rag/search` rimane disponibile per testare la ricerca direttamente senza passare dall'agente.

---

## ⚙️ Come funziona

### Flusso di ingestion

```txt
File caricato
   │
   ▼
[Supabase Storage] ──► salvataggio grezzo
   │
   ▼
[text_extraction] ──► estrazione del testo
   │
   ▼
[chunking] ──────────► suddivisione in chunk da ~500 token con overlap
   │
   ▼
[Voyage AI embed] ───► 1 embedding da 1024 dimensioni per chunk
   │
   ▼
[document_chunks]  ── pgvector su Supabase
```

### Flusso di search

```text
"Come resetto la password?"
   │
   ▼
[Voyage AI embed] (input_type=query)
   │
   ▼
[frontline.match_document_chunks RPC] ── filtro per company_id + ORDER BY distance
   │
   ▼
Top K chunk con similarity score
```

### Scelte tecniche

| Aspetto              | Scelta MVP                               | Perché                                                             |
|----------------------|------------------------------------------|--------------------------------------------------------------------|
| Provider embedding   | **Voyage AI** (`voyage-3`, 1024 dim)     | Multilingua (come richiesto dalla live chat), qualità top.         |
| SDK                  | REST via `httpx`                         | L'SDK ufficiale non supporta Python 3.14 → chiamata diretta.       |
| Dimensione chunk     | ~2000 caratteri (~500 token)             | Sweet spot per FAQ/manuali, standard di settore.                   |
| Overlap              | ~200 caratteri                           | Evita di spezzare a metà concetti chiave.                          |
| Batching embeddings  | 128 chunk per chiamata a Voyage          | Limite massimo consentito dall'API, spezzato automaticamente.      |
| Indice vettoriale    | HNSW + cosine distance                   | Default moderno di pgvector, ottimo rapporto qualità/velocità.     |
| Elaborazione         | **Sincrona** dentro l'endpoint di upload | Semplice. Code asincrone in una fase successiva.                   |
| Tabella              | `document_chunks` separata               | Più chunk per documento → non sta in una colonna su `documents`.   |
| Path Storage         | `<company_id>/<document_id>/<filename>`  | UUID nel path evita collisioni se due upload hanno lo stesso nome. |

---

## 🔧 Configurazione

### Variabili d'ambiente

| Variabile                   | Dove                  | Descrizione                                              |
|-----------------------------|-----------------------|----------------------------------------------------------|
| `VOYAGE_API_KEY`            | `backend/.env`        | Chiave API di Voyage AI (ottenibile su voyageai.com).    |
| `SUPABASE_URL`              | `backend/.env`        | URL progetto Supabase.                                   |
| `SUPABASE_SERVICE_ROLE_KEY` | `backend/.env`        | Service role key (bypassa RLS, solo backend).            |
| `SUPABASE_SCHEMA`           | `backend/.env`        | Schema del DB (default `frontline`); ospita `document_chunks` e `match_document_chunks`. |
| `DEV_COMPANY_ID`            | `backend/.env`        | UUID della company di sviluppo (tenant corrente).        |

### Migration

Le migration della fase 3 (`010`, `011`, `012`) vanno eseguite nel SQL Editor di Supabase **dopo** quelle della fase 2. Vedi [database.md](database.md#-avvio-rapido-applicare-le-migration).

---

## 🚀 Avvio rapido

1. **Imposta `VOYAGE_API_KEY`** in `backend/.env`.
2. **Applica le migration** `010`, `011`, `012`, `013` su Supabase.
3. **Avvia il backend**:

```bash
cd backend
uvicorn main:app --reload
```

4. **Carica un documento**:

```bash
curl -X POST http://localhost:8000/documents/upload \
     -F "file=@manuale.pdf"
```

5. **Prova una ricerca**:

```bash
curl -X POST http://localhost:8000/rag/search \
     -H "Content-Type: application/json" \
     -d '{"query": "Come contattare il supporto?", "top_k": 5}'
```

---

## 🧪 Testing

```bash
cd backend
pytest tests/rag tests/api/test_documents.py tests/integrations/embedding_interfaces -v
```

Tutti i test usano mock: nessuna chiamata reale a Voyage, Supabase o allo storage. Il chunker e l'estrattore sono testati end-to-end con input veri (testo inline, DOCX generato al volo).

---

## 🔍 Troubleshooting

### Problema: `RuntimeError: Voyage is not configured`

**Causa**: `VOYAGE_API_KEY` non è in `backend/.env`.
**Soluzione**: aggiungila e riavvia il backend.

### Problema: upload lento per PDF grossi

**Causa**: nell'MVP l'elaborazione è sincrona dentro l'endpoint. Un PDF da 100 pagine può richiedere qualche secondo (parsing + N chiamate embedding).
**Soluzione**: per l'MVP accettare l'attesa. Post-MVP si può spostare l'elaborazione su una coda asincrona.

### Problema: `UnsupportedDocumentError`

**Causa**: formato non tra PDF/DOCX/TXT/Markdown.
**Soluzione**: converti il file in uno dei formati supportati. Altri formati (CSV, XLSX, HTML) sono rimandati a post-MVP.

### Problema: `/rag/search` ritorna una lista vuota

**Cause possibili**:

- Nessun documento caricato per quella `company_id`.
- Documenti caricati con un altro `DEV_COMPANY_ID`.
- Lo `status` dei documenti è `error` (problema in fase di ingestion — controlla i log del backend).

### Problema: `extension "vector" is not available` o errore sull'indice HNSW

**Causa**: la migration `001_enable_extensions.sql` non è stata applicata, oppure la versione di pgvector sul progetto Supabase è troppo vecchia.
**Soluzione**: in Supabase → Database → Extensions, verifica che `vector` sia abilitato e aggiornato.

---

## ⚠️ Note MVP

- **Sincrono**: nessuna coda di background. Upload = attesa fino a fine ingestion.
- **Nessun re-indexing automatico**: se cambi parametri di chunking, i chunk vecchi restano come sono. Per rigenerarli cancella e ricarica il documento.
- **Chunking a caratteri**: approssimazione semplice. Un token splitter "vero" (es. `tiktoken`) è un miglioramento post-MVP.

---

## 📚 Riferimenti

- **Codice**:
  - [backend/rag/text_extraction.py](../backend/rag/text_extraction.py)
  - [backend/rag/chunking.py](../backend/rag/chunking.py)
  - [backend/rag/ingestion.py](../backend/rag/ingestion.py)
  - [backend/rag/search.py](../backend/rag/search.py)
  - [backend/integrations/embedding_interfaces/](../backend/integrations/embedding_interfaces/)
  - [backend/api/documents.py](../backend/api/documents.py)
- **Migration**: [010](../backend/database/migrations/010_document_chunks.sql), [011](../backend/database/migrations/011_drop_documents_embedding.sql), [012](../backend/database/migrations/012_search_function.sql), [013](../backend/database/migrations/013_documents_with_counts_view.sql)
- **Test**: [backend/tests/rag/](../backend/tests/rag/), [backend/tests/api/test_documents.py](../backend/tests/api/test_documents.py)
- **Doc correlati**: [architecture.md](architecture.md), [database.md](database.md), [api_endpoints.md](api_endpoints.md)
- **Risorse esterne**: [Voyage AI docs](https://docs.voyageai.com/), [pgvector](https://github.com/pgvector/pgvector)
