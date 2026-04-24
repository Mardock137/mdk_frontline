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

Il frontend è un'applicazione **Next.js 16** con TypeScript e Tailwind CSS. Nella Fase 5 (MVP) espone una sola pagina pubblica:

- **`/chat/[slug]`** — Live chat dedicata per ogni azienda cliente. Il cliente finale di un'azienda apre questa pagina e chatta con l'agente AI. Non richiede login.

La **dashboard aziendale** (gestione documenti, ticket, configurazione) è prevista nella Fase 6.

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

### Componenti

| File                                  | Ruolo                                                                           |
|---------------------------------------|---------------------------------------------------------------------------------|
| `app/chat/[slug]/page.tsx`            | Pagina principale: carica config, gestisce stato messaggi e conversazione       |
| `components/chat/ChatWindow.tsx`      | Contenitore messaggi con auto-scroll                                            |
| `components/chat/MessageBubble.tsx`   | Singola bolla (cliente a destra, agente a sinistra)                             |
| `components/chat/MessageInput.tsx`    | Input testo + pulsante invia (Enter per inviare, Shift+Enter per andare a capo) |
| `components/chat/TypingIndicator.tsx` | Tre pallini animati mentre l'agente elabora                                     |
| `lib/api.ts`                          | Chiamate al backend: `getConfig()` e `sendMessage()`                            |

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

| Tecnologia            | Versione | Ruolo                           |
|-----------------------|----------|---------------------------------|
| Next.js               | 16.x     | Framework React (App Router)    |
| React                 | 19.x     | UI                              |
| TypeScript            | 5.x      | Tipizzazione                    |
| Tailwind CSS          | 4.x      | Styling                         |
| lucide-react          | 1.x      | Icone                           |
| clsx + tailwind-merge | —        | Utility composizione classi CSS |

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

> Il backend deve essere avviato in parallelo dalla cartella `backend/` con `uvicorn main:app --reload`. Senza backend il frontend non può caricare la configurazione né inviare messaggi.

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

- **Nessun login**: la pagina `/chat/[slug]` è pubblica e accessibile a chiunque abbia il link.
- **Conversazione in memoria**: il `conversation_id` vive nello stato React. Ricaricare la pagina azzera la conversazione.
- **Nessun test automatico**: il frontend non ha test nella Fase 5. I test UI sono rimandati a post-MVP.
- **Home page (`/`) vuota**: la root del sito mostra solo un placeholder. Verrà gestita nella Fase 6 o nella dashboard.

---

## 📚 Riferimenti

- **Codice**:
  - [frontend/app/chat/[slug]/page.tsx](../frontend/app/chat/%5Bslug%5D/page.tsx)
  - [frontend/components/chat/](../frontend/components/chat/)
  - [frontend/lib/api.ts](../frontend/lib/api.ts)
- **Backend correlato**:
  - [backend/api/config.py](../backend/api/config.py) — endpoint `GET /chat/{slug}/config`
  - [backend/api/agent.py](../backend/api/agent.py) — endpoint `POST /chat/{slug}/message`
- **Doc correlati**: [architecture.md](architecture.md), [api_endpoints.md](api_endpoints.md)
