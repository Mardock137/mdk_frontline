# Deploy

Guida operativa al deploy di MDK Frontline in staging: containerizzazione del backend, hosting su Google Cloud Run e Vercel.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [⚙️ Come funziona](#️-come-funziona)
- [🧪 Testing](#-testing)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

Per adesso il progetto viene deployato **solo in staging**, non in produzione. I due pezzi da ospitare sono:

- **Backend** (FastAPI) → containerizzato con Docker, ospitato su **Google Cloud Run**.
- **Frontend** (Next.js) → ospitato su **Vercel**.

Il database (Supabase) è già un servizio gestito esternamente: non richiede deploy da parte nostra. In questa fase si riusa il progetto Supabase già esistente, usato anche in sviluppo locale.

Non è ancora configurato un dominio custom: sia il backend che il frontend usano gli URL automatici forniti rispettivamente da Cloud Run (`*.run.app`) e Vercel (`*.vercel.app`).

**Stato attuale**: backend e frontend sono entrambi online in staging e collegati tra loro. Dashboard e live chat sono state testate end-to-end.

- **URL backend staging**: `https://<backend-staging>.run.app`
- **URL frontend staging**: `https://<frontend-staging>.vercel.app`

---

## ⚙️ Come funziona

### Containerizzazione del backend

Il backend viene impacchettato in un'immagine Docker tramite [backend/Dockerfile](../backend/Dockerfile):

- Immagine base: `python:3.14-slim`.
- Le dipendenze (`requirements.txt`) vengono installate in un layer separato dal codice applicativo, per riusare la cache Docker quando cambia solo il codice.
- Il server (`uvicorn`) si avvia sulla porta indicata dalla variabile d'ambiente `PORT` (default `8080`), lo standard richiesto da Cloud Run per instradare il traffico verso il container.
- [backend/.dockerignore](../backend/.dockerignore) esclude dal contesto di build file non necessari nell'immagine (ambiente virtuale, test, log, segreti, cache).

### Build e run locali

Dalla cartella `backend/`:

```bash
docker build -t mdk-frontline-backend:test .
```

Per far girare il container in locale con le variabili del proprio `.env`:

```bash
docker run --rm -p 8080:8080 --env-file .env -e PORT=8080 mdk-frontline-backend:test
```

Verifica che il backend risponda aprendo [http://localhost:8080/health](http://localhost:8080/health): deve restituire `{"status": "ok"}`.

### Deploy del backend su Google Cloud Run

Il servizio Cloud Run **`frontline-backend-staging`** (regione `europe-west1`) è configurato per il **deploy continuo da GitHub tramite Cloud Build**:

- **Repository**: `Mardock137/mdk_frontline`
- **Branch**: `staging` (espressione `^staging$`)
- **Dockerfile**: `/backend/Dockerfile` (la cartella `backend/` viene usata anche come contesto della build Docker)
- **Accesso**: pubblico non autenticato (il backend deve rispondere direttamente al browser dei clienti finali)
- **Scalabilità**: automatica, minimo `0` istanze (nessun costo quando non c'è traffico)
- **Fatturazione**: basata sulle richieste

Ad ogni push sul branch `staging`, Cloud Build ricostruisce l'immagine e Cloud Run pubblica automaticamente una nuova revisione.

### Segreti e configurazione su Cloud Run

Le credenziali sensibili non vivono in un file `.env` sul server, ma su **Google Secret Manager**, seguendo il criterio: *le credenziali sono secret, la configurazione è una variabile d'ambiente normale*.

**Secret** (letti da Secret Manager, ruolo `Secret Manager Secret Accessor` concesso al service account del servizio):

- `ANTHROPIC_API_KEY`
- `VOYAGE_API_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_ANON_KEY`
- `SSO_SHARED_SECRET`
- `FRONTLINE_SESSION_SECRET`
- `KV_REST_API_TOKEN`

**Variabili d'ambiente semplici** (nessun dato sensibile: URL pubblici o parametri di comportamento):

| Variabile             | Valore in staging                                             |
|-----------------------|---------------------------------------------------------------|
| `SUPABASE_URL`        | URL del progetto Supabase (riusato da dev/locale)             |
| `SUPABASE_SCHEMA`     | `frontline`                                                   |
| `FRONTEND_URL`        | `https://<frontend-staging>.vercel.app`                       |
| `CHAT_RATE_LIMIT`     | `20/minute`                                                   |
| `TRUST_PROXY_HEADERS` | `true`                                                        |
| `LOG_LEVEL`           | `INFO`                                                        |
| `KV_REST_API_URL`     | URL REST del database Upstash di Frontline                    |

In staging e produzione non vanno impostati né `DEV_COMPANY_ID` né `ALLOW_DEV_COMPANY_FALLBACK`. Senza sessione le API rispondono `401`.

> **Nota su `TRUST_PROXY_HEADERS`**: in locale resta `false` (valore di default), ma su Cloud Run è impostato a `true` in sicurezza, perché l'header `X-Forwarded-For` viene scritto dall'infrastruttura di Google davanti al container e non è falsificabile da un client esterno.
> **Attenzione — permesso IAM per ogni singolo secret**: creare un secret in Secret Manager non basta per renderlo leggibile dal servizio. Ogni secret richiede il ruolo `Secret Manager Secret Accessor` concesso esplicitamente (Secret Manager → apri il secret → scheda **Autorizzazioni** → Concedi accesso) al service account del servizio (es. `<project-number>-compute@developer.gserviceaccount.com`). Dimenticarlo per un secret nuovo fa fallire il deploy con un errore `Permission denied on secret: ...` — è capitato con `SSO_SHARED_SECRET` e `FRONTLINE_SESSION_SECRET` alla loro prima introduzione.

### Deploy del frontend su Vercel

Il progetto Vercel **`mdk-frontline`** è collegato allo stesso repository GitHub, con **Root Directory** impostata su `frontend` (Vercel rileva automaticamente Next.js da lì).

- **Repository**: `Mardock137/mdk_frontline`
- **Branch usato in staging**: `staging`, pubblicato come **Preview Deployment** (non come "Production" di Vercel, che resta associato a `main` e libero per una futura vera produzione).
- **Variabile d'ambiente** `NEXT_PUBLIC_API_URL`: puntata all'URL del backend su Cloud Run, impostata sia per l'ambiente Production che Preview di Vercel (Development resta escluso, usa `frontend/.env.local` in locale). La usano la chat pubblica, il callback SSO e il proxy `/api` (documenti e dashboard). Il browser della dashboard non chiama più Cloud Run direttamente.
- **Variabile d'ambiente** `NEXT_PUBLIC_WEBSITE_URL`: URL del sito esterno (link di ritorno dalla pagina `/sso/error`).
- **Upload documenti**: il file passa da Vercel (`/api/documents/upload`). Sopra 4,5 MB Vercel risponde `413` e il backend non riceve il file.

Ad ogni push sul branch `staging`, Vercel ricostruisce e ripubblica automaticamente un nuovo Preview Deployment sullo stesso URL.

> **Nota terminologica**: "Production"/"Preview" sono nomi interni di Vercel per i tipi di deployment, non corrispondono agli ambienti di business (staging/produzione del progetto). In questa fase usiamo un Preview Deployment di Vercel come nostro ambiente di staging.

### Collegamento con il sito esterno (SSO)

Il sito esterno deve reindirizzare a un indirizzo che finisce con `/sso/callback`.

> **Attenzione — l'URL deve finire con `/sso/callback`**, non con la sola root del dominio. Se punta solo a `https://<dominio>` il token SSO arriva sulla home page di Frontline (che non lo legge) e il login automatico non parte mai, senza nessun errore visibile lato Frontline.

Vedi anche [architecture.md](architecture.md#-autenticazione-sso-da-un-sito-esterno) per il flusso completo del token.

---

## 🧪 Testing

- `docker build` deve completare senza errori.
- Il container avviato con `docker run` deve rispondere `200 {"status": "ok"}` su `/health`.
- In staging, il servizio Cloud Run deve rispondere `200 {"status": "ok"}` su `/health` dopo ogni nuova revisione (vedi URL nella sezione Panoramica).
- In staging, verificare end-to-end aprendo `/dashboard` (documenti, ticket, config, stats) e `/chat/<slug>` sul frontend, con dati reali provenienti dal backend su Cloud Run.

---

## 📚 Riferimenti

- **Dockerfile**: [backend/Dockerfile](../backend/Dockerfile)
- **Dockerignore**: [backend/.dockerignore](../backend/.dockerignore)
- **Doc correlati**: [config.md](config.md), [repo_structure.md](repo_structure.md), [architecture.md](architecture.md)
- **Risorse esterne**: [Cloud Run](https://cloud.google.com/run), [Secret Manager](https://cloud.google.com/secret-manager), [Vercel](https://vercel.com/docs)
