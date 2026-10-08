# Endpoint API

Elenco degli endpoint HTTP esposti dal backend FastAPI.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [⭐ Endpoint](#-endpoint)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

Il backend espone una REST API. Dashboard e documenti identificano l'azienda dal token di sessione (`Authorization: Bearer`). Se l'header manca, si usa `DEV_COMPANY_ID` (sviluppo locale). La live chat resta pubblica, identificata dallo slug nell'URL. Tutte le risposte sono JSON.

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

- **Auth**: header `Authorization: Bearer <session_token>` (fallback `DEV_COMPANY_ID` se assente).
- **Errori**: `400` file vuoto/senza nome, `415` formato non supportato, `401` sessione non valida.

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

### `POST /auth/sso`

Scambia il JWT del sito MDK-137 con un token di sessione interno di Frontline (24h). Il token del sito è monouso.

- **Body**: `{ "sso_token": "..." }`
- Il JWT deve includere `jti` e `product` uguale a `mdk-frontline`, oltre a firma, issuer, audience e scadenza.
- **Risposta `200`**: `{ "session_token": "..." }`
- **Errori**: `401` se il token è scaduto, non valido, senza i claim richiesti o già usato; `503` se Redis non risponde o mancano `KV_REST_API_URL` / `KV_REST_API_TOKEN` (nessun token di sessione); `422` body vuoto.

### `GET /chat/{company_slug}/config`

Ritorna i dati di branding e il messaggio di benvenuto per la pagina di live chat. Endpoint pubblico: nessuna autenticazione richiesta.

- **Path param**: `company_slug` — lo slug dell'azienda (es. `acme`).
- **Risposta `200`**:

```json
{
    "agent_name": "Sofia",
    "company_display_name": "Acme Srl",
    "logo_url": null,
    "primary_color": "#FF5733",
    "welcome_message": "Ciao! Come posso aiutarti?"
}
```

- **Errori**: `404` company o agent_config non trovata.

### `GET /chat/{company_slug}/conversation/{conversation_id}/messages`

Restituisce i messaggi di una conversazione esistente, in ordine cronologico. Endpoint pubblico di sola lettura (nessuna autenticazione, nessun rate limit) usato dalla live chat per ripristinare la cronologia dopo un refresh.

- **Path params**: `company_slug` — slug dell'azienda; `conversation_id` — UUID della conversazione.
- **Risposta `200`**: array di `{ id, role, content }` (ruolo `system` escluso, lista vuota se non ci sono messaggi).

```json
[
    { "id": "uuid", "role": "customer", "content": "Come resetto la password?" },
    { "id": "uuid", "role": "agent",    "content": "Segui questi passi..." }
]
```

- **Errori**: `404` company non trovata, `404` conversazione non trovata o appartenente a un'altra company (`"Conversation not found"`).

### `POST /chat/{company_slug}/message`

Invia un messaggio al chatbot AI dell'azienda identificata da `company_slug`. Se `conversation_id` è null viene creata una nuova conversazione. L'agente usa la knowledge base, può aprire ticket e scalare a operatori umani autonomamente.

- **Path param**: `company_slug` — lo slug dell'azienda (es. `acme`).
- **Body**:

```json
{
    "conversation_id": "uuid-opzionale-o-null",
    "content": "Come resetto la password?"
}
```

- **Risposta `200`**:

```json
{
    "conversation_id": "uuid",
    "reply": "Per resettare la password segui questi passi..."
}
```

- **Errori**: `404` company o agent_config non trovata, `404` `conversation_id` fornito ma inesistente o appartenente a un'altra company (`"Conversation not found"`), `422` contenuto vuoto, `429` limite richieste per IP superato (configurabile via `CHAT_RATE_LIMIT`, default `20/minute`; dietro un reverse proxy fidato impostare `TRUST_PROXY_HEADERS=true` perché il limite conti il vero IP del client), `500` API key Anthropic non configurata.

---

## 🖥️ Dashboard endpoints (`/dashboard`)

Tutti gli endpoint `/dashboard` (e `/documents`, `/rag/search`) usano `get_current_company_id`: token di sessione se presente, altrimenti `DEV_COMPANY_ID`.

### `GET /dashboard/tickets`

Lista tutti i ticket della company corrente, ordinati dal più recente.

- **Risposta `200`**: array di `{ id, conversation_id, subject, description, status, is_escalation, created_at, updated_at }`.
- `status`: `"open"` | `"in_progress"` | `"closed"`.
- `is_escalation`: `true` se l'agente ha aperto il ticket come escalation.

### `PATCH /dashboard/tickets/{ticket_id}`

Aggiorna lo stato di un ticket.

- **Body**: `{ "status": "open" | "in_progress" | "closed" }`
- **Risposta `200`**: oggetto ticket aggiornato.
- **Errori**: `404` se il ticket non esiste o non appartiene alla company.

### `GET /dashboard/agent-config`

Legge la configurazione dell'agente per la company corrente.

- **Risposta `200`**:

```json
{
    "agent_name": "Sofia",
    "company_display_name": "Acme Srl",
    "primary_color": "#FF5733",
    "tone": "formal",
    "default_language": "it",
    "welcome_message": "Ciao! Come posso aiutarti?"
}
```

- **Errori**: `404` se la configurazione non esiste.

### `PATCH /dashboard/agent-config`

Aggiorna parzialmente la configurazione dell'agente. Solo i campi presenti nel body vengono modificati.

- **Campi aggiornabili**: `agent_name`, `company_display_name`, `primary_color` (hex `#RRGGBB`), `tone` (`formal`|`informal`), `default_language`, `welcome_message`.
- **Risposta `200`**: configurazione aggiornata.
- **Errori**: `422` se il body è vuoto, `404` se la configurazione non esiste.

### `GET /dashboard/stats`

Ritorna statistiche aggregate per la company corrente.

- **Risposta `200`**:

```json
{
    "total_conversations": 142,
    "tickets_by_status": {
        "open": 5,
        "in_progress": 2,
        "closed": 18
    },
    "escalation_open_count": 3
}
```

---

## 📚 Riferimenti

- **Router documenti**: [backend/api/documents.py](../backend/api/documents.py)
- **Router agente**: [backend/api/agent.py](../backend/api/agent.py)
- **Router auth**: [backend/api/auth.py](../backend/api/auth.py)
- **Router config**: [backend/api/config.py](../backend/api/config.py)
- **Router dashboard**: [backend/api/dashboard.py](../backend/api/dashboard.py)
- **Sessione / SSO**: [backend/utils/auth.py](../backend/utils/auth.py)
- **Registrazione**: [backend/main.py](../backend/main.py)
- **Doc correlati**: [rag.md](rag.md), [database.md](database.md), [architecture.md](architecture.md), [frontend.md](frontend.md)
