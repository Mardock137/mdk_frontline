# Endpoint API

Elenco degli endpoint HTTP esposti dal backend FastAPI.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [⭐ Endpoint](#-endpoint)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

Il backend espone una REST API. Nell'MVP il tenant corrente (azienda cliente) è identificato dalla variabile d'ambiente `DEV_COMPANY_ID` (l'auth reale arriverà dopo). Tutte le risposte sono JSON.

---

## ⭐ Endpoint

### `GET /health`

Health check. Ritorna `{"status": "ok"}`.

### `POST /documents/upload`

Upload di un file e ingestion sincrona nella knowledge base (estrazione testo → chunking → embedding → salvataggio).

- **Body**: `multipart/form-data`, campo `file`
- **Formati supportati**: PDF, DOCX, TXT, Markdown
- **Risposta `201`**:

```json
{
    "document_id": "uuid",
    "chunk_count": 12,
    "status": "ready"
}
```

- **Errori**: `400` file vuoto/senza nome, `415` formato non supportato.

### `GET /documents`

Lista documenti della company corrente (più recenti prima).

- **Risposta `200`**: array di `{ id, filename, content_type, status, created_at }`.

### `DELETE /documents/{document_id}`

Cancella il documento, i chunk associati e il file da Supabase Storage.

- **Risposta `204`** su successo, `404` se il documento non appartiene alla company.

### `POST /rag/search`

Ricerca semantica sui chunk della knowledge base della company corrente.

- **Body**:

```json
{
    "query": "How do I reset my password?",
    "top_k": 5
}
```

- **Risposta `200`**:

```json
{
    "hits": [
        {
            "chunk_id": "uuid",
            "document_id": "uuid",
            "chunk_index": 2,
            "content": "...",
            "similarity": 0.87
        }
    ]
}
```

- `similarity` è in `[0, 1]` (cosine similarity, più alto = più rilevante).

---

## 📚 Riferimenti

- **Router**: [backend/api/documents.py](../backend/api/documents.py)
- **Registrazione**: [backend/main.py](../backend/main.py)
- **Doc correlati**: [rag.md](rag.md), [database.md](database.md)
