# Sistema di logging

Documento di riferimento per il sistema di logging centralizzato del backend: output, rotazione dei file, livelli e configurazione.

---

## 📋 Indice

- [📄 Panoramica](#-panoramica)
- [⚙️ Come funziona](#️-come-funziona)
- [🔧 Configurazione](#-configurazione)
- [🧪 Testing](#-testing)
- [📚 Riferimenti](#-riferimenti)

---

## 📄 Panoramica

Il backend utilizza il modulo `logging` della libreria standard Python con una configurazione centralizzata definita in [backend/utils/logging_config.py](../backend/utils/logging_config.py). La configurazione è applicata all'avvio dell'applicazione tramite l'evento `lifespan` di FastAPI in [backend/main.py](../backend/main.py).

Caratteristiche principali:

- Output simultaneo a **console** e a **file**.
- **Rotazione automatica** dei file di log per evitare che crescano indefinitamente.
- **Idempotenza**: chiamate ripetute a `setup_logging()` non duplicano gli handler.
- Livello di log configurabile tramite variabile d'ambiente `LOG_LEVEL`.

---

## ⚙️ Come funziona

All'avvio del backend, la funzione `setup_logging()` configura il root logger con due handler:

1. **`StreamHandler`** — scrive i messaggi sulla console (stdout).
2. **`RotatingFileHandler`** — scrive i messaggi su file, ruotandoli al raggiungimento della dimensione massima.

### File di log

- **Percorso**: `backend/logs/backend.log`
- **Dimensione massima per file**: 5 MB
- **Numero di backup mantenuti**: 5 (i file ruotati vengono rinominati in `backend.log.1`, `backend.log.2`, ecc.)

La cartella [backend/logs/](../backend/logs/) viene creata automaticamente se non esiste.

### Formato dei messaggi

```text
2026-04-17 10:23:45 | INFO     | nome.del.modulo | Messaggio di log
```

I campi sono: timestamp, livello, nome del logger (di solito il modulo Python), messaggio.

### Uso nel codice

Ogni modulo recupera il proprio logger con il nome standard `__name__`:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Operazione completata")
logger.warning("Attenzione: valore inatteso")
logger.error("Errore durante l'elaborazione")
```

Non serve configurare nulla nei singoli moduli: ereditano la configurazione dal root logger.

### Librerie di terze parti silenziate

Le librerie HTTP di basso livello usate sotto il cofano (`httpx`, `httpcore`, `hpack`) a livello `DEBUG` stampano le intestazioni HTTP grezze delle richieste — comprese `Authorization` e `apikey`, cioè la `SUPABASE_SERVICE_ROLE_KEY`. Per evitare che finiscano nel file di log, `setup_logging()` forza questi tre logger a `WARNING` **indipendentemente** dal `LOG_LEVEL` scelto per il resto dell'app: puoi quindi usare `LOG_LEVEL=DEBUG` per debuggare la tua logica applicativa senza rischiare di scrivere segreti su disco.

---

## 🔧 Configurazione

Il livello di log è controllato dalla variabile d'ambiente `LOG_LEVEL` definita in [backend/.env](../backend/.env) (o [backend/.env.example](../backend/.env.example) come riferimento).

Valori accettati (dal più verboso al meno verboso):

- `DEBUG` — ogni dettaglio, utile durante lo sviluppo.
- `INFO` — eventi rilevanti del flusso normale (default).
- `WARNING` — situazioni sospette ma non bloccanti.
- `ERROR` — errori gestiti.
- `CRITICAL` — errori gravi che possono compromettere il funzionamento.

Esempio in `.env`:

```env
LOG_LEVEL=DEBUG
```

Per override temporanei (utile nei test), `setup_logging()` accetta parametri opzionali:

```python
from pathlib import Path
from utils.logging_config import setup_logging

setup_logging(log_level="DEBUG", log_file=Path("/tmp/custom.log"))
```

---

## 🧪 Testing

I test del sistema di logging si trovano in [backend/tests/utils/test_logging_config.py](../backend/tests/utils/test_logging_config.py) e verificano:

- Creazione corretta dei file di log e degli handler.
- Scrittura effettiva dei messaggi.
- Idempotenza della funzione di setup.

Per eseguirli, dalla cartella `backend/`:

```bash
pytest tests/utils/test_logging_config.py -v
```

---

## 📚 Riferimenti

- **Codice**: [backend/utils/logging_config.py](../backend/utils/logging_config.py)
- **Test**: [backend/tests/utils/test_logging_config.py](../backend/tests/utils/test_logging_config.py)
- **Doc correlati**: [Configurazione](config.md), [Struttura della repo](repo_structure.md)
- **Risorse esterne**: [Python logging HOWTO](https://docs.python.org/3/howto/logging.html), [RotatingFileHandler](https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler)
