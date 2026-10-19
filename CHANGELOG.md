<!-- markdownlint-disable -->
# 📋 Changelog

## 0.14.0 — 2026-10-15

### Changed

- **Fallback su `DEV_COMPANY_ID` disattivato di default** (`backend/utils/config.py`, `backend/utils/auth.py`, `backend/.env.example`): senza `Authorization: Bearer` le API rispondono `401`. In locale serve `ALLOW_DEV_COMPANY_FALLBACK=true` nel `.env`. In staging e produzione non vanno impostati né il flag né `DEV_COMPANY_ID`.
- **Controllo di origine sul proxy** (`frontend/app/api/[...path]/route.ts`): `POST`, `PATCH` e `DELETE` rispondono `403` se l'origine non coincide con l'host della richiesta (`Origin`, oppure `Sec-Fetch-Site: same-origin` quando `Origin` manca). `GET` non cambia.
- `docs/config.md`, `docs/deploy.md`, `docs/api_endpoints.md`, `docs/architecture.md`, `docs/frontend.md`, `docs/database.md`, `docs/rag.md`, `docs/repo_structure.md` e `README.md` (versione `0.14.0`).

---

## 0.13.1 — 2026-10-09

### Changed

- **Cookie di sessione non più leggibile da JavaScript** (`frontend/app/sso/callback/route.ts`, `frontend/lib/session.ts`): `frontline_session` è `httpOnly`. Il browser non può più leggere il token e non allega `Authorization: Bearer`.
- **Proxy Next.js** (`frontend/app/api/[...path]/route.ts`, `frontend/lib/api.ts`): documenti e dashboard chiamano `/api/...` sullo stesso sito. Il proxy legge il cookie e aggiunge il Bearer verso il backend. Path diversi da `documents` e `dashboard` (chat, auth, rag, health) rispondono `404`. La chat pubblica resta sul backend, senza cookie.
- **Upload su Vercel**: il file passa dal proxy. Sopra 4,5 MB Vercel risponde `413`.
- `docs/architecture.md`, `docs/frontend.md`, `docs/repo_structure.md`, `docs/api_endpoints.md`, `docs/deploy.md` e `README.md`.
- `README.md`: versione bumped a `0.13.1`.

---

## 0.13.0 — 2026-10-08

### Added

- **Token SSO monouso** (`backend/utils/replay_guard.py`, `backend/api/auth.py`): dopo la verifica della firma, Frontline richiede `jti` e `product` uguale a `mdk-frontline`. Il `jti` viene registrato su Upstash Redis (`SET` con `NX`, scadenza 90 secondi). Un secondo uso dello stesso token risponde `401`. Se Redis non risponde, va in timeout o mancano `KV_REST_API_URL` / `KV_REST_API_TOKEN`, la risposta è `503` e non viene emesso alcun token di sessione.

### Changed

- `verify_site_token` restituisce l'id azienda insieme al `jti`. I token senza `jti` o senza `product` corretto ora vengono rifiutati.
- `docs/config.md`, `docs/api_endpoints.md`, `docs/architecture.md`, `docs/deploy.md`, `docs/repo_structure.md`, `docs/observability.md` e `README.md`.
- `README.md`: versione bumped a `0.13.0`.

---

## 0.12.1 — 2026-09-19

### Fixed

- **Alert di sicurezza GitHub sul frontend** (`frontend/package.json`, `frontend/package-lock.json`): tre dipendenze npm risultavano nelle versioni segnalate da Dependabot. Nessuna modifica al codice applicativo (chat, dashboard, SSO, `next.config.ts`). `npm run lint` e `npm run build` passano sulla nuova stack. Backend e workflow CI invariati; Dependabot version-update resta disattivato (come da 0.8.2).
  - **`next` e `eslint-config-next` da `16.2.12` a `16.3.4`**: chiude CVE-2026-75604 / GHSA-p293-qw3h-jr36 (RCE su server Next ospitati su Windows) e GHSA-2xp9-vwfh-vxw4 (RCE nell'ottimizzazione immagini AVIF via `sharp`/libheif). L'advisory indica `16.3.3` come prima patch; si usa `16.3.4` perché riabilita l'ottimizzazione AVIF dopo il fix upstream e corregge un errore di build con TypeScript 6 (già in uso nel progetto, `6.0.3`). Le novità 16.3 (Cache Components, Instant Navigations, Partial Prefetching) restano disattivate: sono opt-in. Staging è su Vercel (Linux), quindi il CVE Windows non era sfruttabile in deploy; il salto chiude comunque l'alert e copre lo sviluppo locale su Windows.
  - **Override `sharp` da `^0.35.0` (`0.35.3` risolto) a `0.35.4`**: GHSA-rgj7-g3m4-5g8c, RCE in libheif su Linux se si processano AVIF/HEIF. `sharp` non è importato dal codice: lo usa Next per `/_next/image` (logo in `frontend/app/chat/[slug]/page.tsx`). Il range `^0.35.0` aveva lasciato il lock sulla `0.35.3` ancora vulnerabile; pin esatto per non ripetere il problema.
  - **Override `js-yaml` da `4.3.1` a `4.3.2`**: CVE-2026-84375, consumo CPU sul parse di YAML untrusted. Dipendenza transitiva solo di ESLint (`@eslint/eslintrc`), non presente a runtime. Il config di lint è `frontend/eslint.config.mjs` (JavaScript), non YAML.

---

## 0.12.0 — 2026-08-22

### Added

- **SSO da un sito esterno** (`backend/utils/auth.py`, `backend/api/auth.py`): il sito invia un JWT firmato (`sso_token` in query). Il backend verifica firma, scadenza (leeway 10s), issuer `mdk-137-website` e audience `mdk-frontline`, poi emette un token di sessione interno (24h) firmato con un secret diverso, mai condiviso col sito. Endpoint `POST /auth/sso` → `{ session_token }`. Token mancante/scaduto/non valido → `401`.
- **Identità azienda reale sulle API dashboard/documenti**: `get_current_company_id` legge `Authorization: Bearer`. Se l'header manca, resta il fallback su `DEV_COMPANY_ID` (sviluppo locale e test esistenti).
- **Callback frontend** (`frontend/app/sso/callback/route.ts`): scambia il token del sito, salva la sessione in un cookie leggibile dal browser (`frontline_session`), redirect a `/dashboard`. Pagina di errore `frontend/app/sso/error/page.tsx` con link di ritorno al sito.
- **Chiamate dashboard/documenti autenticati** (`frontend/lib/api.ts`): allegano `Authorization: Bearer` se il cookie è presente. La live chat pubblica non cambia.
- **Variabili** `SSO_SHARED_SECRET` e `FRONTLINE_SESSION_SECRET` in Settings / `.env.example`; dipendenza `PyJWT`. Frontend: `NEXT_PUBLIC_WEBSITE_URL` per il link di ritorno.
- **Azienda di test in staging** nello schema `frontline`, con una riga `agent_configs`, usata per il test end-to-end dell'SSO.

### Fixed

- **Test end-to-end reale dell'SSO in staging**: risolti due problemi di configurazione emersi durante la prima prova con un click vero dal sito esterno (nessuna modifica al codice). L'URL di callback configurato sul sito esterno puntava alla root del dominio invece che a `/sso/callback`, quindi il token non veniva mai letto da Frontline. Sul backend, i secret `SSO_SHARED_SECRET` e `FRONTLINE_SESSION_SECRET` erano stati creati in Secret Manager ma senza il ruolo `Secret Manager Secret Accessor` concesso al service account del servizio, causando `Permission denied` al deploy.

### Changed

- `_current_company_id()` duplicata in `dashboard.py` e `documents.py` sostituita dalla dipendenza condivisa.

---

## 0.11.3 — 2026-07-26

### Added

- **Dockerfile per il backend** (`backend/Dockerfile`, `backend/.dockerignore`): immagine basata su `python:3.14-slim`, pensata per il deploy su Google Cloud Run. La porta viene letta dalla variabile d'ambiente `PORT` (default `8080`), coerente con il comportamento di Cloud Run. Build e run testati in locale: il container risponde correttamente su `/health`.
- **Documentazione aggiornata**: `docs/repo_structure.md` (righe per `Dockerfile` e `.dockerignore`), `docs/deploy.md` (prima guida al deploy in staging, sezione build/run locale dell'immagine).
- **Nessun impatto sul comportamento dell'app**: nessuna modifica al codice Python, solo aggiunta dell'infrastruttura di containerizzazione.

---

## 0.11.2 — 2026-07-24

### Fixed

- **Segreti esposti nel log a `LOG_LEVEL=DEBUG`** (`backend/utils/logging_config.py`): a livello `DEBUG`, le librerie `httpx`, `httpcore` e `hpack` stampano le intestazioni HTTP grezze di ogni richiesta, comprese `Authorization` e `apikey` — cioè la `SUPABASE_SERVICE_ROLE_KEY` in chiaro nel file `backend/logs/backend.log`. `setup_logging()` ora forza questi tre logger a `WARNING` indipendentemente dal `LOG_LEVEL` applicativo, così il debug della logica di business non rischia più di scrivere segreti su disco. Il codice applicativo (tutte le chiamate `logger.*` nei moduli del progetto) non ha mai loggato segreti: il problema riguardava solo le dipendenze HTTP di terze parti.
- **Test aggiunto** (`backend/tests/utils/test_logging_config.py`): verifica che `httpx`/`httpcore`/`hpack` restino a `WARNING` anche quando il logger applicativo è impostato su `DEBUG`.
- **Documentazione aggiornata**: `docs/observability.md` (nuova sezione "Librerie di terze parti silenziate").

---

## 0.11.1 — 2026-07-24

### Fixed

- **`403 Forbidden` / `permission denied for schema frontline` (Postgres `42501`) su ogni chiamata REST verso lo schema `frontline`** (`backend/database/migrations/020_grant_frontline_privileges.sql`): a differenza di `public`, uno schema custom non riceve permessi di default da Postgres, quindi `service_role` (usato dal backend) non poteva accedere a tabelle, view, funzioni e sequenze anche se bypassa la Row Level Security. La nuova migration concede esplicitamente `usage` sullo schema e i permessi su tutti gli oggetti esistenti a `service_role`, più `alter default privileges` per applicare automaticamente gli stessi permessi agli oggetti creati dalle migration future.
- **Documentazione aggiornata**: `docs/database.md` (sezione "Come funziona" e nuova voce di Troubleshooting), `docs/repo_structure.md` (riga per `020_grant_frontline_privileges.sql`).

---

## 0.11.0 — 2026-07-24

### Changed

- **Modello LLM aggiornato a Claude Sonnet 5** (`backend/config/llm_models/support_agent.yaml`): `model` passa da `claude-sonnet-4-6` a `claude-sonnet-5`, drop-in replacement secondo la documentazione Anthropic (stessi tool, stesso formato di richieste/risposte). Il codice non usa `temperature`/`top_p`/`top_k` né thinking manuale (`budget_tokens`), quindi nessuna delle breaking change dell'API introdotte da Sonnet 5 impatta il progetto.
- **`max_tokens` alzato da `2048` a `4096`** (stesso file): su Sonnet 5 l'adaptive thinking è attivo di default e consuma parte dello stesso budget di `max_tokens` condiviso con la risposta finale; inoltre il nuovo tokenizer del modello produce ~30% di token in più a parità di testo. Il margine più ampio previene risposte troncate (`stop_reason: "max_tokens"`). `effort: low` resta invariato, già la scelta corretta per customer support ad alto volume.
- **Nessuna modifica al codice Python**: `loader.py` e `anthropic_interface.py` leggono `model`/`max_tokens` dinamicamente dal YAML senza validare il nome del modello.
- **Documentazione aggiornata**: `README.md`, `docs/architecture.md`, `docs/config.md` (riferimenti a `claude-sonnet-4-6` sostituiti).
- **Nessun impatto su ambienti reali**: il progetto non è ancora stato deployato né in staging né in produzione.

---

## 0.10.2 — 2026-07-22

### Removed

- **Tabella `users` rimossa** (`backend/database/migrations/019_drop_users_table.sql`): non era referenziata da nessun endpoint, tool o agente, solo dai modelli Pydantic (`UserCreate`/`User` in `backend/database/models.py`) e dai loro test. Era stata creata nella migration `003` in previsione di un futuro supporto multi-utente per azienda, mai collegata al resto del codice. Come già fatto per `011_drop_documents_embedding.sql`, la rimozione avviene con una nuova migration numerata invece di modificare retroattivamente la `003`, che resta come documento storico. Nessun impatto sul comportamento dell'app.

---

## 0.10.1 — 2026-07-22

### Changed

- **Estensione `vector` spostata dallo schema `public` a uno schema dedicato `extensions`** (migration `001`, `005`, `010`, `012`, `016`): chiude l'ultimo warning del Security Advisor (`extension vector installed in public`), lasciando `public` completamente vuoto. La migration `001_enable_extensions.sql` crea lo schema `extensions` e installa `vector` al suo interno (`with schema extensions`); il tipo è ora qualificato esplicitamente come `extensions.vector` nella colonna legacy `documents.embedding` (migration `005`), nella colonna `document_chunks.embedding` e nel relativo indice HNSW (migration `010`, `extensions.vector_cosine_ops`), e nel parametro `query_embedding` di `match_document_chunks` (migration `012`). Il `search_path` della funzione (migration `016`) passa da `frontline, public, pg_temp` a `frontline, extensions, pg_temp` per continuare a risolvere l'operatore `<=>`.
- **Nessuna modifica al codice Python né a `SUPABASE_SCHEMA`**: nessun modulo backend referenzia il tipo `vector` o il suo schema; l'ingestion passa gli embedding come liste e la ricerca passa dalla funzione RPC `match_document_chunks`. Lo schema `extensions` non va aggiunto agli "Exposed schemas" di Supabase: non è mai interrogato direttamente dal backend.

---

## 0.10.0 — 2026-07-21

### Changed

- **Tutti gli oggetti del database spostati nello schema dedicato `frontline`** (migration `001`-`016`): tabelle, indici, trigger, la funzione trigger `set_updated_at`, la funzione `match_document_chunks` e la view `documents_with_counts` vivono ora nello schema `frontline` invece che in `public`, così `public` resta libero per un futuro secondo prodotto. L'estensione `vector` (pgvector) resta in `public` per ora (spostamento rimandato alla Fase 2). La migration `001_enable_extensions.sql` crea lo schema; le migration `002`-`008`, `010`, `011`, `012`, `013`, `014`, `015`, `016` sono state aggiornate per creare/alterare gli oggetti in `frontline`. Il `search_path` di `match_document_chunks` è `frontline, public, pg_temp` per continuare a risolvere l'operatore vettoriale `<=>` (ancora in `public`). Le migration `009` (storage) e `017`/`018` (funzione `rls_auto_enable` gestita da Supabase in `public`) restano invariate.
- **Nuova variabile `SUPABASE_SCHEMA`** (`backend/utils/config.py`, `backend/.env.example`): default `frontline`. Il client Supabase (`backend/database/supabase_client.py`) la passa tramite `ClientOptions(schema=...)`, così tutte le chiamate `.table(...)` e `.rpc(...)` esistenti puntano automaticamente allo schema corretto senza altre modifiche al codice.

---

## 0.9.6 — 2026-07-17

### Fixed

- **Warning Security Advisor su `rls_auto_enable()`** (`backend/database/migrations/017_revoke_rls_auto_enable_execute.sql`, `backend/database/migrations/018_revoke_rls_auto_enable_execute_public.sql`): la funzione (creata da Supabase per l'auto-enable di RLS sulle nuove tabelle, non dal codice del progetto) è `SECURITY DEFINER` e viveva in `public`, quindi era auto-esposta come RPC pubblico (`/rest/v1/rpc/rls_auto_enable`) chiamabile da `anon` e `authenticated`. La prima revoca (017) toglieva il permesso direttamente a `anon`/`authenticated`, ma senza effetto: quei ruoli lo ereditavano dal permesso concesso di default al ruolo `PUBLIC` (comportamento standard di Postgres alla creazione di una funzione). La seconda migration (018) revoca il permesso direttamente da `PUBLIC`, eliminandolo alla radice per tutti i ruoli che lo ereditano. La funzione e il suo event trigger restano invariati e continuano a funzionare automaticamente sulle nuove `CREATE TABLE`.

---

## 0.9.5 — 2026-07-17

### Fixed

- **Warning Security Advisor `role mutable search_path`** (`backend/database/migrations/016_fix_functions_search_path.sql`): le funzioni `set_updated_at()` e `match_document_chunks()` non avevano un `search_path` fissato, lasciando che venisse risolto usando quello di chi le chiamava (rischio di "search_path hijacking"). Impostato `search_path = public, pg_temp` su entrambe, senza modificarne la logica.

---

## 0.9.4 — 2026-07-15

### Fixed

- **Errore Security Advisor su `documents_with_counts`** (`backend/database/migrations/015_documents_with_counts_security_invoker.sql`): la view era definita senza `security_invoker`, facendola girare implicitamente con i permessi del creatore (equivalente a `SECURITY DEFINER`) invece che di chi la interroga, bypassando così la RLS delle tabelle sottostanti. Impostato `security_invoker = true` sulla view.

---

## 0.9.3 — 2026-06-17

### Fixed

- **Test instabile sull'endpoint `PATCH /dashboard/agent-config`** (`backend/api/dashboard.py`): il controllo del corpo vuoto (`422 No fields to update`) veniva eseguito *dopo* la creazione del client Supabase. In CI, dove le chiavi Supabase non sono configurate, `get_supabase_client()` sollevava `RuntimeError` prima del controllo, facendo fallire `test_update_agent_config_empty_body` (atteso `422`, ottenuto `500`). In locale il test passava perché il `.env` con le chiavi reali mascherava il problema. Il controllo del corpo vuoto è stato spostato prima della creazione del client: con un corpo vuoto l'endpoint risponde subito `422` senza contattare il database.

### Changed

- **CI anche sui push diretti** (`.github/workflows/backend-ci.yml`, `.github/workflows/frontend-ci.yml`): aggiunto il trigger `push` accanto a `pull_request` (stesso filtro `paths`). In precedenza i test giravano solo all'apertura di una Pull Request, quindi i push diretti non venivano mai verificati. Ora la suite parte sia sui push sia sulle PR, su tutti i branch.

---

## 0.9.2 — 2026-06-17

### Fixed

- **Errore lint `react-hooks/set-state-in-effect`** (`frontend/app/dashboard/documents/page.tsx`): la pagina Documenti caricava i dati iniziali chiamando una funzione `async` (`void fetchDocuments()`) dentro `useEffect`, facendo scattare la nuova regola di React Hooks. L'`useEffect` ora usa lo stile a catena di promise (`getDocuments().then().catch().finally()`), coerente con le altre pagine della dashboard (tickets, config, stats). La funzione `fetchDocuments` resta invariata per il refresh dopo upload. Nessun cambiamento di comportamento.

---

## 0.9.1 — 2026-06-17

### Fixed

- **Linting frontend rotto** (`frontend/eslint.config.mjs`, `frontend/package.json`): in Next.js 16 il comando `next lint` è stato rimosso, causando il fallimento dello script `npm run lint` (e del passo CI corrispondente). Migrazione allo standard ESLint CLI: creato `eslint.config.mjs` con flat config nativa (`eslint-config-next/core-web-vitals` + `eslint-config-next/typescript`, già inclusi nelle dipendenze) e aggiornato lo script a `"lint": "eslint ."`. Nessuna nuova dipendenza, nessuna modifica al workflow CI.

---

## 0.9.0 — 2026-06-17

### Added

- **Persistenza cronologia chat** (`frontend/app/chat/[slug]/page.tsx`, `frontend/lib/api.ts`): il browser memorizza il `conversation_id` in localStorage (`mdk:conversation:<slug>`) dopo il primo messaggio inviato. Alla riapertura della pagina, la cronologia reale viene ricaricata dal database tramite il nuovo endpoint e mostrata nella chat (preceduta dal welcome message di configurazione). Se l'ID salvato risulta stale (conversazione non trovata), la chiave localStorage viene pulita e la chat riparte da zero senza errori visibili.
- **Endpoint `GET /chat/{company_slug}/conversation/{conversation_id}/messages`** (`backend/api/agent.py`): nuovo endpoint pubblico di sola lettura che restituisce i messaggi di una conversazione in ordine cronologico (ruolo `system` escluso). Include controllo cross-tenant identico al POST: chi non conosce sia lo slug sia il `conversation_id` non può accedere alla conversazione.
- **Tipo `ChatMessage` e funzione `getConversationMessages`** (`frontend/lib/api.ts`): nuovo tipo `{ id, role, content }` e funzione fetch con supporto `AbortSignal`.
- **Test** (`backend/tests/api/test_agent.py`): 5 test per il nuovo endpoint — happy path con messaggi, lista vuota, 404 company non trovata, 404 conversazione non trovata, 404 cross-tenant.

---

## 0.8.5 — 2026-06-17

### Added

- **Rate limiting sull'endpoint chat** (`backend/api/agent.py`, `backend/main.py`, `backend/utils/rate_limit.py`): aggiunto un tetto alle richieste verso `POST /chat/{company_slug}/message` tramite la libreria `slowapi`. Il conteggio è per indirizzo IP, in memoria (adatto all'MVP single-istanza). Chi supera il limite riceve `429 Too Many Requests` senza che la chiamata a Claude venga eseguita. Il limite è configurabile da `.env` con la variabile `CHAT_RATE_LIMIT` (default `20/minute`).
- **`backend/utils/rate_limit.py`**: modulo unico che espone l'istanza `Limiter` condivisa tra `main.py` e `api/agent.py`, evitando import circolari.
- **`CHAT_RATE_LIMIT`** nelle `Settings` (`backend/utils/config.py`) e documentata in `backend/.env.example`.
- **`slowapi==0.1.10`** aggiunta a `backend/requirements.txt`.
- **Test `429`** in `backend/tests/api/test_agent.py`: verifica che superato il limite l'endpoint risponda `429` e che `SupportAgent.run` non venga chiamato.
- **Fixture `disable_rate_limiter`** in `backend/tests/conftest.py` (`autouse=True`): disabilita il limiter per tutti i test esistenti, che restano invariati e verdi.
- **Supporto proxy nel rate limiting** (`backend/utils/rate_limit.py`, `backend/utils/config.py`): nuova variabile `TRUST_PROXY_HEADERS` (default `false`). Quando attiva, l'IP usato come chiave del rate limiter viene letto dalla prima voce dell'header `X-Forwarded-For` invece che dal socket. Risolve il caso in cui, dietro un reverse proxy o load balancer, tutte le richieste arriverebbero con l'IP del proxy facendo condividere a tutti i visitatori un unico contatore. L'header viene considerato solo con trust esplicito: fidarsene senza un proxy davanti permetterebbe a chiunque di falsificare l'IP e aggirare il limite.
- **`TRUST_PROXY_HEADERS`** documentata in `backend/.env.example`, `docs/config.md`, `docs/api_endpoints.md` e nella tabella variabili del `README.md`.
- **Test bucketing per IP** in `backend/tests/api/test_agent.py`: con `TRUST_PROXY_HEADERS=true`, IP diversi in `X-Forwarded-For` hanno contatori separati (un IP viene bloccato con `429` mentre un altro passa).

---

## 0.8.4 — 2026-06-16

### Fixed

- **Query Supabase non bloccanti nel percorso chat** (`backend/api/agent.py`, `backend/agents/support_agent.py`, `backend/rag/search.py`): tutte le chiamate Supabase sincrone nel percorso della live chat sono ora avvolte in `asyncio.to_thread`, replicando il pattern già usato in `tools/ticket.py` e `tools/escalation.py`. In precedenza ogni query DB bloccava l'intero event loop, impedendo a tutti gli utenti connessi di ricevere risposte durante l'attesa. Nessuna migrazione al client `AsyncClient` (fuori scope MVP).

---

## 0.8.3 — 2026-06-16

### Accessibility

- **Live region messaggi** (`frontend/components/chat/ChatWindow.tsx`): il contenitore dei messaggi è ora una live region (`role="log"`, `aria-live="polite"`, `aria-relevant="additions"`, `aria-label="Conversazione"`). Gli screen reader annunciano ogni nuovo messaggio senza interrompere l'utente.
- **Mittente nelle bolle** (`frontend/components/chat/MessageBubble.tsx`): ogni bolla antepone un'etichetta `sr-only` con il nome del mittente ("Assistant:" / "You:"), invisibile visivamente ma letta dagli screen reader.
- **Indicatore "sta scrivendo" percepibile** (`frontend/components/chat/TypingIndicator.tsx`): aggiunto un testo `sr-only` "Assistant is typing" (annunciato dalla live region che lo contiene) e i tre pallini animati marcati `aria-hidden="true"` (decorativi).
- **Campo di input** (`frontend/components/chat/MessageInput.tsx`): aggiunto `aria-label="Type a message"` alla textarea; il `placeholder` da solo non è un'etichetta affidabile per gli screen reader.
- **Pagina attiva nella sidebar** (`frontend/app/dashboard/layout.tsx`): aggiunto `aria-label="Main navigation"` sul `nav` e `aria-current="page"` sul link attivo; la sezione corrente è ora comunicata agli screen reader oltre che tramite colore.
- **Lingua coerente per gli screen reader**: tutte le etichette ARIA / `sr-only` sono in inglese, allineate al testo visibile dell'interfaccia.

---

## 0.8.2 — 2026-06-16

### Removed

- **Dependabot** (`.github/dependabot.yml`): rimossa la configurazione degli aggiornamenti automatici delle dipendenze (backend `pip` e frontend `npm`). Gli aggiornamenti di versione si gestiscono a mano. Gli alert di sicurezza di GitHub (indipendenti da questo file) restano invariati.

---

## 0.8.1 — 2026-06-16

### Fixed

- **Costante HTTP 422 deprecata** (`backend/api/dashboard.py`): sostituito `status.HTTP_422_UNPROCESSABLE_ENTITY` con `status.HTTP_422_UNPROCESSABLE_CONTENT` (rinominata in Starlette). Stesso codice di stato `422`, nessun cambiamento di comportamento; rimuove il `DeprecationWarning` dalla suite di test.

---

## 0.8.0 — 2026-06-16

### Added

- **Parametro `effort` su `LLMModelConfig`** (`backend/config/llm_models/loader.py`): nuovo campo opzionale con default `"high"` e validazione sui valori ammessi (`low`, `medium`, `high`, `xhigh`, `max`). I YAML che non lo definiscono continuano a funzionare invariati.
- **`effort: low` in `support_agent.yaml`** (`backend/config/llm_models/support_agent.yaml`): il livello di effort è ora impostato esplicitamente a `low`, coerente con l'uso ad alto volume del customer support (riduce latenza e costo).
- **Override `effort` in `AnthropicInterface`** (`backend/integrations/llm_interfaces/anthropic_interface.py`): il costruttore accetta il parametro opzionale `effort`; il metodo `chat()` passa sempre `output_config={"effort": ...}` alla SDK Anthropic.
- **Test aggiornati**: aggiunti casi in `backend/tests/config/test_llm_models_loader.py` (lettura da YAML, default `high`, errore su valore non valido) e in `backend/tests/integrations/llm_interfaces/test_anthropic_interface.py` (verifica `_effort`, override, presenza di `output_config` nella chiamata SDK).

---

## 0.7.8 — 2026-04-27

### Added

- **Dependabot frontend** (`.github/dependabot.yml`): aggiunto il monitoraggio automatico settimanale delle dipendenze npm nella cartella `frontend/`, con PR di aggiornamento create direttamente su GitHub.
- **GitHub Actions CI frontend** (`.github/workflows/frontend-ci.yml`): nuovo workflow che si attiva su ogni PR che tocca il frontend, installa le dipendenze con `npm ci`, esegue `npm run lint` e poi `npm run build`.

---

## 0.7.7 — 2026-04-27

### Added

- **Dependabot** (`.github/dependabot.yml`): controlla automaticamente ogni settimana le dipendenze Python del backend (`/backend`) e apre PR di aggiornamento sul repo GitHub.
- **GitHub Actions CI** (`.github/workflows/backend-ci.yml`): workflow che si attiva su ogni PR che tocca file in `backend/`. Installa le dipendenze ed esegue `pytest` in autonomia. Nessun secret necessario (i test sono completamente mockati).

---

## 0.7.6 — 2026-04-27

### Fixed

- **Fixture test condivise** (`backend/tests/conftest.py`, `backend/tests/api/test_agent.py`, `backend/tests/api/test_config.py`, `backend/tests/agents/test_support_agent.py`): centralizzate le fixture `company_id` e `conversation_id` in `conftest.py`, rimuovendo le duplicazioni locali nei moduli di test.
- **Copertura `BaseAgent` completata** (`backend/tests/agents/test_base_agent.py`): aggiunti test sul contratto della classe astratta, inclusi i casi di istanziazione vietata, sottoclasse concreta valida e verifica del metodo `run()` asincrono.
- **Errori infrastrutturali coperti** (`backend/tests/api/test_agent.py`, `backend/tests/api/test_config.py`, `backend/tests/api/test_dashboard.py`): aggiunti test `500` per i casi in cui l'agente o Supabase sollevano errori non gestiti.
- **Test agente meno fragile** (`backend/tests/agents/test_support_agent.py`): riscritto il test del tool sconosciuto per verificare il risultato finale dell'agente invece di dipendere dalla struttura interna di `call_args_list`.
- **Suite verificata**: i test aggiornati passano correttamente.

## 0.7.5 — 2026-04-27

### Fixed

- **Classi custom dei bottoni** (`frontend/components/ui/button.tsx`): corretto il merge di `className` nei componenti `Button`, così le classi passate dal chiamante non vengono più ignorate o scartate in modo silenzioso.
- **Toast piu' sicuri** (`frontend/components/ui/toast.tsx`): i timeout di auto-dismiss vengono ora tracciati e cancellati quando `ToastProvider` viene smontato, evitando aggiornamenti di stato dopo l'unmount. In più gli ID dei toast usano `crypto.randomUUID()` al posto di `Math.random()`.
- **Chat pubblica senza race condition** (`frontend/app/chat/[slug]/page.tsx`, `frontend/lib/api.ts`): il caricamento iniziale della configurazione usa `AbortController` e cleanup nel `useEffect`, così una navigazione rapida non provoca più `setState` su un componente già smontato.

## 0.7.4 — 2026-04-27

### Fixed

- **Tool agente non bloccanti** (`backend/tools/ticket.py`, `backend/tools/escalation.py`, `backend/agents/support_agent.py`): `create_ticket` ed `escalate` sono stati convertiti in funzioni asincrone e ora eseguono le chiamate Supabase con `asyncio.to_thread`, evitando di bloccare l'event loop durante le richieste FastAPI.
- **Client Voyage riusabile** (`backend/integrations/embedding_interfaces/voyage_embedding.py`): il client HTTP verso Voyage AI viene ora creato una sola volta nell'istanza `VoyageEmbedding` e riutilizzato per tutte le richieste di embedding, evitando la creazione di una nuova connessione a ogni chiamata.
- **Stats dashboard ottimizzate** (`backend/api/dashboard.py`): il conteggio ticket non scarica più tutte le righe in memoria. Ora usa query di count direttamente sul database per `open`, `in_progress`, `closed` ed escalation aperte.
- **Test aggiornati** (`backend/tests/tools/test_ticket.py`, `backend/tests/tools/test_escalation.py`, `backend/tests/agents/test_support_agent.py`, `backend/tests/api/test_dashboard.py`): allineati ai tool asincroni e alla nuova strategia di count lato DB. Suite verificata con test tutti passati.

## 0.7.3 — 2026-04-26

### Fixed

- **Pipeline di ingestione documenti** (`backend/rag/ingestion.py`): spostati upload su storage e aggiornamento di `storage_path` dentro il blocco `try/except`, così un errore in queste fasi marca correttamente il documento come `ERROR` invece di lasciarlo bloccato in `PROCESSING`.
- **Sanitizzazione filename upload** (`backend/rag/ingestion.py`): il path storage ora usa `Path(filename).name`, così vengono rimossi eventuali componenti di directory dal nome file inviato dall'utente.
- **Escalation piu' robusta** (`backend/tools/escalation.py`): inserimento ticket e update della conversazione sono gestiti separatamente. Se l'insert fallisce viene restituito un errore controllato; se fallisce solo l'update della conversazione, il problema viene loggato ma il ticket creato non va perso.
- **Test aggiornati**: aggiunti casi mirati in `backend/tests/rag/test_ingestion.py` e `backend/tests/tools/test_escalation.py` per coprire storage failure, sanitizzazione filename, ticket insert failure e conversation update failure.

## 0.7.2 — 2026-04-26

### Fixed

- **CORS backend** (`backend/main.py`): corretta la configurazione di `allow_credentials` quando `FRONTEND_URL` vale `*`. Prima il backend inviava una combinazione CORS non valida (`*` + credentials abilitate), che poteva far rifiutare le risposte dal browser.
- **Loghi esterni nella chat** (`frontend/next.config.ts`): aggiunti `remotePatterns` per permettere il caricamento di immagini remote via `next/image`, necessario per supportare loghi aziendali ospitati su domini esterni.
- **Crash nei tool dell'agente** (`backend/agents/support_agent.py`): i parametri dei tool ora vengono letti in modo sicuro con `.get()` invece di causare un crash se Claude omette un campo richiesto. Nei casi incompleti viene restituito un messaggio d'errore controllato invece di un `500`.
- **Test aggiornati** (`backend/tests/agents/test_support_agent.py`): aggiunti 3 test per verificare che `search_knowledge`, `create_ticket` ed `escalate` non vadano in crash quando ricevono input incompleto.

## 0.7.1 — 2026-04-26

### Fixed

- **Sicurezza endpoint chat** (`backend/api/agent.py`): aggiunta verifica cross-tenant su `conversation_id` per impedire il riuso di conversazioni appartenenti a un'altra company. Se la conversazione non appartiene al tenant corrente, l'endpoint ritorna `404`.
- **`AnthropicInterface`** (`backend/integrations/llm_interfaces/anthropic_interface.py`): corretta la gestione delle risposte con più blocchi `text`, che prima sovrascrivevano i segmenti precedenti. Ora tutti i blocchi vengono concatenati nell'ordine corretto.
- **Test aggiornati**: aggiunti casi mirati in `backend/tests/api/test_agent.py` e `backend/tests/integrations/llm_interfaces/test_anthropic_interface.py` per coprire sia il controllo cross-tenant sia le risposte testuali multi-blocco.

---

## 0.7.0 — 2026-04-26

### Added

- **Dashboard aziendale** (`/dashboard`): area admin per la gestione di documenti, ticket, configurazione agente e statistiche. Accessibile senza login (usa `DEV_COMPANY_ID` come il resto del progetto MVP).
- **Backend `backend/api/dashboard.py`**: 5 nuovi endpoint REST registrati su `/dashboard`:
  - `GET /dashboard/tickets` — lista ticket della company (tutti, ordinati per data, con campo `is_escalation`).
  - `PATCH /dashboard/tickets/{ticket_id}` — aggiorna lo stato del ticket (`open` → `in_progress` → `closed`).
  - `GET /dashboard/agent-config` — legge la configurazione attuale dell'agente.
  - `PATCH /dashboard/agent-config` — aggiorna parzialmente: `agent_name`, `company_display_name`, `primary_color`, `tone`, `default_language`, `welcome_message`.
  - `GET /dashboard/stats` — ritorna conversazioni totali, ticket per stato e conteggio escalation aperti.
- **Test `backend/tests/api/test_dashboard.py`**: 11 test con Supabase completamente mockato (tutti gli endpoint, happy path + errori 404/422/wrong company).
- **Componenti UI** in `frontend/components/ui/`: `button`, `card`, `badge`, `table`, `input`, `label`, `select`, `textarea`, `dialog`, `toast` — implementati con Tailwind CSS v4 e `class-variance-authority`.
- **`ToastProvider`** + hook `useToast`: sistema di notifiche contestuali (success/error/info) con auto-dismiss dopo 4 secondi.
- **Funzioni API** aggiunte a `frontend/lib/api.ts`: `getDocuments`, `uploadDocument`, `deleteDocument`, `getTickets`, `updateTicketStatus`, `getAgentConfig`, `updateAgentConfig`, `getStats`.
- **Layout dashboard** `frontend/app/dashboard/layout.tsx`: sidebar di navigazione con link a Documenti, Ticket, Configurazione, Statistiche.
- **Pagina Documenti** `frontend/app/dashboard/documents/page.tsx`: upload tramite bottone, lista file con stato e conteggio chunk, eliminazione con confirm.
- **Pagina Ticket** `frontend/app/dashboard/tickets/page.tsx`: lista ticket con badge stato/escalation, pulsanti cambio stato, banner escalation alert.
- **Pagina Configurazione** `frontend/app/dashboard/config/page.tsx`: form completo per `agent_name`, `company_display_name`, `primary_color` (color picker + hex), `tone`, `default_language`, `welcome_message`.
- **Pagina Statistiche** `frontend/app/dashboard/stats/page.tsx`: 4 stat card (conversazioni, ticket, escalation aperti, ticket chiusi) + barre di progressione per stato ticket.
- **Redirect** `frontend/app/dashboard/page.tsx` → `/dashboard/documents`.

### Changed

- `backend/main.py`: registrato il nuovo `dashboard_router` con prefisso `/dashboard`.
- `frontend/lib/api.ts`: refactoring interno con helper `handleResponse<T>` per evitare duplicazione della gestione errori.

---

## 0.6.0 — 2026-04-24

### Added

- **Pagina Live Chat pubblica** (`/chat/[slug]`): i clienti finali di un'azienda possono aprire la chat direttamente nel browser senza login. Al caricamento vengono mostrati il branding aziendale e il messaggio di benvenuto; i messaggi successivi vengono gestiti con l'agente AI.
- **Endpoint `GET /chat/{company_slug}/config`**: ritorna nome agente, nome azienda, logo, colore principale e messaggio di benvenuto. Nessuna autenticazione richiesta ([backend/api/config.py](backend/api/config.py)).
- **`CORSMiddleware`** (FastAPI built-in): il backend ora accetta richieste cross-origin. In sviluppo tutte le origini sono permesse (`*`); in produzione si limita a `FRONTEND_URL` ([backend/main.py](backend/main.py)).
- **Variabile `FRONTEND_URL`** nelle `Settings` e in `.env.example` ([backend/utils/config.py](backend/utils/config.py)).
- **Test `tests/api/test_config.py`**: 4 test con Supabase mockato (happy path, 404 company, 404 agent_config, logo_url presente).
- **Progetto Next.js 15** in `frontend/` con App Router, TypeScript, Tailwind CSS v4.
- **`frontend/lib/api.ts`**: funzioni `getConfig(slug)` e `sendMessage(slug, payload)` verso il backend FastAPI.
- **Componenti React** ([frontend/components/chat/](frontend/components/chat/)):
  - `ChatWindow.tsx` — contenitore messaggi con scroll automatico.
  - `MessageBubble.tsx` — bolla messaggio con colore primario per il cliente e stile neutro per l'agente.
  - `MessageInput.tsx` — textarea con invio tramite Enter o pulsante; colore pulsante dinamico.
  - `TypingIndicator.tsx` — tre pallini animati mostrati durante l'attesa della risposta.
- **`frontend/.env.local.example`** con `NEXT_PUBLIC_API_URL`.

### Changed

- `backend/main.py`: registrato il nuovo router `/chat/{slug}/config` e aggiunto `CORSMiddleware`.

---

## 0.5.0 — 2026-04-24

### Added

- **Agente AI autonomo con tool calling** (`SupportAgent`): loop completo che chiama Claude, esegue i tool richiesti e salva i messaggi nel DB ([backend/agents/support_agent.py](backend/agents/support_agent.py)).
- **Tre tool invocabili dall'agente** ([backend/tools/](backend/tools/)):
  - `knowledge.py` — ricerca semantica sulla knowledge base aziendale (`search_knowledge`).
  - `ticket.py` — crea un ticket di supporto con `is_escalation=False` (`create_ticket`).
  - `escalation.py` — crea un ticket con `is_escalation=True` e aggiorna lo stato della conversazione a `ESCALATED` (`escalate`).
- **`AnthropicInterface`**: adapter concreto per Claude con supporto nativo al tool calling ([backend/integrations/llm_interfaces/anthropic_interface.py](backend/integrations/llm_interfaces/anthropic_interface.py)).
- **`BaseLLMInterface` aggiornata**: metodo `generate(prompt)` sostituito con `chat(messages, system, tools)` più adatto ai modelli moderni; aggiunti dataclass `ChatResponse` e `ToolUse` ([backend/integrations/llm_interfaces/base_llm_interface.py](backend/integrations/llm_interfaces/base_llm_interface.py)).
- **System prompt template** per l'agente di supporto: nome agente, azienda, tono, lingua, istruzioni sui tool ([backend/config/prompts/support_agent.py](backend/config/prompts/support_agent.py)).
- **Endpoint `POST /chat/{company_slug}/message`**: crea conversazione se necessario, esegue l'agente e ritorna la risposta ([backend/api/agent.py](backend/api/agent.py)).
- **Migration SQL 014** ([backend/database/migrations/014_tickets_add_is_escalation.sql](backend/database/migrations/014_tickets_add_is_escalation.sql)): colonna `is_escalation boolean NOT NULL DEFAULT false` nella tabella `tickets`.
- **Modelli Pydantic aggiornati**: `TicketCreate` e `Ticket` espongono ora il campo `is_escalation: bool = False`.
- **`config/llm_models/support_agent.yaml`**: file di configurazione del modello per l'agente di supporto (`model`, `max_tokens`). Modificare questo file per cambiare modello o limiti senza toccare il codice.
- **`config/llm_models/loader.py`**: funzione `load_model_config(name)` e dataclass immutabile `LLMModelConfig`. Il sistema è estensibile: ogni agente avrà il proprio YAML identificato dal nome.
- **Test completi con mock** (nessuna chiamata reale a servizi esterni):
  - `backend/tests/tools/test_knowledge.py`
  - `backend/tests/tools/test_ticket.py`
  - `backend/tests/tools/test_escalation.py`
  - `backend/tests/agents/test_support_agent.py`
  - `backend/tests/api/test_agent.py`
  - `backend/tests/integrations/llm_interfaces/test_base_llm_interface.py` (riscritto)
  - `backend/tests/config/test_llm_models_loader.py`
  - `backend/tests/integrations/llm_interfaces/test_anthropic_interface.py`

### Changed

- `BaseLLMInterface.generate` → `BaseLLMInterface.chat` (breaking change interno; nessun codice esterno ne dipendeva).
- `backend/main.py`: registrato il nuovo router `/chat`.
- `AnthropicInterface`: rimosso `DEFAULT_MODEL` hardcodato; model e max_tokens vengono ora caricati da `support_agent.yaml` all'avvio. Entrambi restano sovrascrivibili via argomento per test e usi one-off.
- `get_llm_client()`: accetta `config_name` invece di `model`.

---

## 0.4.0 — 2026-04-21

### Added

- Sistema RAG completo: upload documenti, estrazione testo (PDF/DOCX/TXT/Markdown), chunking con overlap, embedding su Voyage AI (`voyage-3`, 1024 dim), salvataggio in pgvector e ricerca semantica multi-tenant.
- Nuova tabella `document_chunks` con indice HNSW su `embedding` ([migration 010](backend/database/migrations/010_document_chunks.sql)).
- Funzione SQL `match_document_chunks` per la ricerca top-K filtrata per `company_id` ([migration 012](backend/database/migrations/012_search_function.sql)).
- Vista SQL `documents_with_counts` per esporre il numero di chunk per documento ([migration 013](backend/database/migrations/013_documents_with_counts_view.sql)), esposto via `GET /documents` come campo `chunk_count`.
- Bucket Storage `documents` gestito dall'endpoint di upload con chiave `<company_id>/<document_id>/<filename>` per evitare collisioni quando due upload condividono lo stesso filename.
- Batching automatico in `VoyageEmbedding`: richieste spezzate in blocchi da 128 input (limite API Voyage), trasparente per i chiamanti.
- Interfaccia astratta `BaseEmbeddingInterface` e implementazione `VoyageEmbedding` (chiamata REST via `httpx`, per compatibilità con Python 3.14).
- Moduli `backend/rag/`: `text_extraction`, `chunking`, `ingestion`, `search`.
- Endpoint API: `POST /documents/upload`, `GET /documents`, `DELETE /documents/{id}`, `POST /rag/search` ([backend/api/documents.py](backend/api/documents.py)).
- Nuovi modelli Pydantic `DocumentChunkCreate` / `DocumentChunk`.
- Variabile `VOYAGE_API_KEY` in [Settings](backend/utils/config.py) e `.env.example`.
- Dipendenze: `pypdf`, `python-docx`, `python-multipart`.
- Test con mock completo dei servizi esterni: chunking, estrazione, ingestion, search, client Voyage, endpoint documenti/ricerca.
- Nuova documentazione [docs/rag.md](docs/rag.md); aggiornate [architecture](docs/architecture.md), [database](docs/database.md), [api_endpoints](docs/api_endpoints.md), [repo_structure](docs/repo_structure.md).

### Changed

- Rimossa la colonna `documents.embedding` ([migration 011](backend/database/migrations/011_drop_documents_embedding.sql)): gli embedding vivono ora su `document_chunks`.
- Timeout HTTP di `VoyageEmbedding` alzato da 30s a 60s (default) per supportare batch di chunk più grossi.

---

## 0.3.0 — 2026-04-21

### Added

- Schema del database come migration SQL versionate in [backend/database/migrations/](backend/database/migrations/): `companies`, `users`, `agent_configs`, `documents` (con colonna `embedding` per il futuro RAG), `conversations`, `messages`, `tickets`.
- Abilitazione delle estensioni PostgreSQL `vector` (pgvector) e `pgcrypto`.
- Bucket Supabase Storage privato `documents` per la knowledge base.
- Row Level Security attivata su tutte le tabelle applicative (il backend usa la service role key e bypassa RLS).
- Factory cached del client Supabase ([backend/database/supabase_client.py](backend/database/supabase_client.py)).
- Modelli Pydantic per tutte le tabelle con enum tipizzati ([backend/database/models.py](backend/database/models.py)).
- Test dei modelli e del client Supabase ([backend/tests/database/](backend/tests/database/)).
- Nuova documentazione: [docs/architecture.md](docs/architecture.md) (schema e scelte architetturali) e [docs/database.md](docs/database.md) (guida operativa alle migration).

---

## 0.2.0 — 2026-04-20

### Added

- Struttura iniziale della repo (`backend/`, `docs/`, `dev_support/`).
- Scaffolding del backend Python con FastAPI e endpoint `/health`.
- Sistema di configurazione tramite `pydantic-settings` e file `.env` ([backend/utils/config.py](backend/utils/config.py)).
- Sistema di logging centralizzato con output a console e file con rotazione ([backend/utils/logging_config.py](backend/utils/logging_config.py)).
- Classi astratte `BaseAgent` ([backend/agents/base_agent.py](backend/agents/base_agent.py)) e `BaseLLMInterface` ([backend/integrations/llm_interfaces/base_llm_interface.py](backend/integrations/llm_interfaces/base_llm_interface.py)) come fondamenta per agenti e integrazioni LLM.
- Configurazione `pytest` ([backend/pytest.ini](backend/pytest.ini)) e suite di test iniziale (health endpoint, settings, logging).
- Dipendenze Python di partenza ([backend/requirements.txt](backend/requirements.txt)).
- Documentazione iniziale: struttura repo, configurazione, sistema di logging.

---

## 0.1.0 — 2026-04-17

- Setup progetto iniziale.
