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

---

## 🧪 Testing

- `docker build` deve completare senza errori.
- Il container avviato con `docker run` deve rispondere `200 {"status": "ok"}` su `/health`.

---

## 📚 Riferimenti

- **Dockerfile**: [backend/Dockerfile](../backend/Dockerfile)
- **Dockerignore**: [backend/.dockerignore](../backend/.dockerignore)
- **Doc correlati**: [config.md](config.md), [repo_structure.md](repo_structure.md)
