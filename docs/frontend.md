<!-- markdownlint-disable -->
# Frontend

Guida operativa al frontend di MDK Frontline: pagina di live chat pubblica e setup del progetto Next.js.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [⚙️ Come funziona](#️-come-funziona)
- [🔧 Configurazione](#-configurazione)
- [🚀 Avvio rapido](#-avvio-rapido)
- [🔍 Troubleshooting](#-troubleshooting)
- [⚠️ Note MVP](#️-note-mvp)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

Il frontend è un'applicazione **Next.js 16** con TypeScript e Tailwind CSS. Espone due aree principali:

- **`/chat/[slug]`** — Live chat pubblica dedicata per ogni azienda cliente. Non richiede login.
- **`/dashboard`** — Dashboard aziendale per la gestione di documenti, ticket, configurazione agente e statistiche. Usa `DEV_COMPANY_ID` dal backend (nessun login nell'MVP).

---

## ⚙️ Come funziona

### Flusso della pagina di chat

```txt
Cliente apre /chat/[slug]
   │
   ▼
GET /chat/{slug}/config  ──► carica branding (nome agente, colore, logo, welcome message)
   │
   ▼
Mostra header con branding + welcome message come primo messaggio agente
   │
   ▼
Cliente scrive messaggio
   │
   ▼
POST /chat/{slug}/message ──► invia al backend con conversation_id (null al primo messaggio)
   │
   ▼
Backend esegue agente AI ──► risposta testuale
   │
   ▼
Mostra risposta agente, salva conversation_id per i messaggi successivi
```

### Componenti — Chat

| File                                  | Ruolo                                                                           |
|---------------------------------------|---------------------------------------------------------------------------------|
| `app/chat/[slug]/page.tsx`            | Pagina principale: carica config, gestisce stato messaggi e conversazione       |
| `components/chat/ChatWindow.tsx`      | Contenitore messaggi con auto-scroll                                            |
| `components/chat/MessageBubble.tsx`   | Singola bolla (cliente a destra, agente a sinistra)                             |
| `components/chat/MessageInput.tsx`    | Input testo + pulsante invia (Enter per inviare, Shift+Enter per andare a capo) |
| `components/chat/TypingIndicator.tsx` | Tre pallini animati mentre l'agente elabora                                     |
| `lib/api.ts`                          | Tutte le chiamate al backend (chat, documenti, dashboard)                       |

### Componenti — Dashboard

| File                                    | Ruolo                                                          |
|-----------------------------------------|----------------------------------------------------------------|
| `app/dashboard/layout.tsx`              | Layout con sidebar di navigazione (Documenti/Ticket/Config/Stats) |
| `app/dashboard/page.tsx`                | Redirect automatico a `/dashboard/documents`                   |
| `app/dashboard/documents/page.tsx`      | Upload, lista e cancellazione documenti                        |
| `app/dashboard/tickets/page.tsx`        | Lista ticket con badge stato/escalation e cambio stato         |
| `app/dashboard/config/page.tsx`         | Form configurazione agente (nome, colore, tono, lingua, welcome) |
| `app/dashboard/stats/page.tsx`          | Stat card + barre stato ticket                                 |
| `components/ui/button.tsx`              | Componente Button con varianti (default/outline/ghost/etc.)    |
| `components/ui/card.tsx`                | Card con Header, Title, Description, Content, Footer           |
| `components/ui/badge.tsx`               | Badge colorato per stati (success/warning/error/info)          |
| `components/ui/table.tsx`               | Table semantica con stile Tailwind                             |
| `components/ui/input.tsx`               | Input testuale stilizzato                                      |
| `components/ui/label.tsx`               | Label per form                                                 |
| `components/ui/select.tsx`              | Select dropdown stilizzato con icona chevron                   |
| `components/ui/textarea.tsx`            | Textarea stilizzata                                            |
| `components/ui/dialog.tsx`              | Modal dialog con overlay, chiusura via ESC e click esterno     |
| `components/ui/toast.tsx`               | Toast notification con `ToastProvider` e hook `useToast()`     |

### Branding dinamico

Ogni azienda ha il suo `primary_color` in `agent_configs`. La pagina applica questo colore su:

- Header (sfondo)
- Bolle messaggi del cliente (sfondo)
- Pulsante invia (sfondo)
- Ring di focus sull'input (bordo)

Se l'azienda ha un `logo_url`, viene mostrato nell'header. Altrimenti appare la prima lettera del nome azienda.

### Gestione conversazione

Il `conversation_id` vive nello stato React (`useRef`). Al primo messaggio viene passato `null` al backend, che crea una nuova conversazione e ritorna l'id. Tutti i messaggi successivi riutilizzano lo stesso id. Se il cliente ricarica la pagina, la conversazione riparte da zero.

---

## 🔧 Configurazione

### Variabili d'ambiente

Il frontend usa un file `.env.local` nella cartella `frontend/` (non va nel git):

| Variabile             | Descrizione                  | Valore sviluppo         |
|-----------------------|------------------------------|-------------------------|
| `NEXT_PUBLIC_API_URL` | URL base del backend FastAPI | `http://localhost:8000` |

Copiare `frontend/.env.local.example` in `frontend/.env.local` e inserire i valori.

> Le variabili con prefisso `NEXT_PUBLIC_` sono visibili nel browser. Quelle senza prefisso rimangono lato server. Per questo progetto MVP tutte le variabili del frontend sono pubbliche.

### Stack

| Tecnologia              | Versione | Ruolo                              |
|-------------------------|----------|------------------------------------|
| Next.js                 | 16.x     | Framework React (App Router)       |
| React                   | 19.x     | UI                                 |
| TypeScript              | 5.x      | Tipizzazione                       |
| Tailwind CSS            | 4.x      | Styling                            |
| class-variance-authority| 0.7.x    | Varianti CSS per componenti UI     |
| lucide-react            | 1.x      | Icone                              |
| clsx + tailwind-merge   | —        | Utility composizione classi CSS    |

---

## 🚀 Avvio rapido

Tutti i comandi vanno eseguiti dalla cartella `frontend/`.

1. **Installa le dipendenze** (una volta sola):

```bash
npm install
```

2. **Crea il file `.env.local`**:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Avvia il server di sviluppo**:

```bash
npm run dev
```

4. **Apri la chat** nel browser: `http://localhost:3000/chat/[slug]`
5. **Apri la dashboard** nel browser: `http://localhost:3000/dashboard`

> Il backend deve essere avviato in parallelo dalla cartella `backend/` con `uvicorn main:app --reload`. Senza backend il frontend non può caricare la configurazione né inviare messaggi. La dashboard richiede `DEV_COMPANY_ID` configurato nel file `backend/.env`.

---

## 🔍 Troubleshooting

### Problema: "Chat not found" all'apertura della pagina

**Causa**: lo slug nell'URL non esiste nella tabella `companies` del database, oppure manca la riga in `agent_configs` per quella company.
**Soluzione**: verificare in Supabase che esista una riga in `companies` con lo slug usato nell'URL e una riga corrispondente in `agent_configs`.

### Problema: la pagina carica ma i messaggi non partono

**Causa**: il backend non è avviato o `NEXT_PUBLIC_API_URL` non è configurato correttamente.
**Soluzione**: verificare che il backend risponda su `http://localhost:8000/health` e che il file `.env.local` contenga l'URL corretto.

### Problema: errore CORS nel browser

**Causa**: il backend non ha il `FRONTEND_URL` configurato o il middleware CORS non copre l'origine del frontend.
**Soluzione**: verificare che `backend/.env` contenga `FRONTEND_URL=*` (sviluppo) o l'URL esatto del frontend (produzione), e riavviare il backend.

---

## ⚠️ Note MVP

- **Nessun login**: la pagina `/chat/[slug]` è pubblica; la dashboard usa `DEV_COMPANY_ID` dal backend.
- **Conversazione in memoria**: il `conversation_id` vive nello stato React. Ricaricare la pagina azzera la conversazione.
- **Nessun test automatico**: il frontend non ha test automatici nell'MVP. I test UI sono rimandati a post-MVP.
- **Home page (`/`) vuota**: la root del sito mostra un placeholder. Non è ancora una landing page.

---

## 📚 Riferimenti

- **Chat**:
  - [frontend/app/chat/[slug]/page.tsx](../frontend/app/chat/%5Bslug%5D/page.tsx)
  - [frontend/components/chat/](../frontend/components/chat/)
- **Dashboard**:
  - [frontend/app/dashboard/](../frontend/app/dashboard/)
  - [frontend/components/ui/](../frontend/components/ui/)
- **API client**:
  - [frontend/lib/api.ts](../frontend/lib/api.ts)
- **Backend correlato**:
  - [backend/api/config.py](../backend/api/config.py) — `GET /chat/{slug}/config`
  - [backend/api/agent.py](../backend/api/agent.py) — `POST /chat/{slug}/message`
  - [backend/api/documents.py](../backend/api/documents.py) — documenti e RAG
  - [backend/api/dashboard.py](../backend/api/dashboard.py) — ticket, config agente, stats
- **Doc correlati**: [architecture.md](architecture.md), [api_endpoints.md](api_endpoints.md)
