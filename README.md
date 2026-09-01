# Creawler — AI Traffic Tracker

Track which AI crawlers and bots visit your website and see it all in a
modern dashboard. Self-hosted (FastAPI + SQLite + Vue 3): you clone it, deploy
it, drop one script tag into any page, and start seeing the AI-based referral
sources and crawler traffic hitting your site.

Built for small businesses and marketing teams that want to know how much of
their traffic comes from ChatGPT, Claude, Perplexity, Google, and the dozens
of other AI agents scraping the web today.

---

## How it works

1. You deploy this service (dashboard + API) anywhere you control.
2. You add a single `<script>` tag to any existing page.
3. Every time a bot (or the browser of a real person) loads that page, the
   tracker sends a visit to the API.
4. The API classifies each visit by `user_agent` and `referrer`:

   | Type      | Detected from                  | Example provider        |
   |-----------|--------------------------------|-------------------------|
   | `crawler` | known AI user-agent token      | OpenAI, Anthropic, Google, Perplexity, Meta |
   | `referral`| referrer domain                | ChatGPT, Claude, OpenRouter |
   | `unknown` | unrecognized user-agent        | human browsers, other bots |

5. The dashboard shows everything: headline stats, visits per AI provider,
   and a paginated history — with light/dark mode.

```
visitor's page (any origin)
   └── <script src="https://your-tracker/api/tracker.js">        (public)
        └── POST /api/track  + write-only tracker key
             └── SQLite  ──►  /api/stats · /api/visits           (admin)
```

---

## What's included

- **FastAPI backend** — tracking, classification, rate limiting, pagination.
- **SQLite storage** — zero-config, file-backed (`data/tracker.db`), WAL mode.
- **Vue 3 + Vuetify dashboard** — responsive, animated bar chart, stats cards,
  paginated history, system-aware dark/light theme.
- **Secure session login** — the admin key is never exposed to the browser; you
  log in and the server issues an `HttpOnly` `SameSite=Lax` session cookie.
- **Docker deployment** — one command, survives reboots (`restart: unless-stopped`).

---

## Requirements

- [Docker](https://docs.docker.com/engine/install/) + Docker Compose
  (recommended path), **or** Python 3.12+ and Node 18+ for local dev.

---

## Quick start with Docker (recommended)

```bash
git clone <your-repo-url> ia-crawler-tracker
cd ia-crawler-tracker

# 1. configure (see .env.example for guidance)
cp .env.example .env
nano .env

# 2. build and start in the background
docker compose up --build -d

# 3. verify
curl -sI http://localhost:5000/     # dashboard
```

- Dashboard → **http://localhost:5000/**  (log in with `API_KEY`)
- OpenAPI docs → **http://localhost:5000/docs**

Stop / restart / logs:

```bash
docker compose down            # stop (data persists in the docker volume)
docker compose up -d           # start again
docker compose logs -f         # stream logs
docker compose down -v         # wipe ALL data + restart clean
```

---

## Local development (no Docker)

```bash
cp .env.example .env && nano .env

# backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000

# dashboard (separate terminal)
cd dashboard
npm install
npm run dev          # http://localhost:5173, proxies /api to :5000
```

> For development only. The dashboard is served by the API in production.

---

## Add the tracker to any existing page

Paste this script tag into the `<body>` (or `<head>` with `defer`) of the page
you want to track. It is deliberately **public** and only embeds the write-only
`TRACKER_KEY`.

```html
<script defer src="https://your-tracker-server/api/tracker.js"></script>
```

That's the whole integration. No token sharing, no build step, works on static
sites, CMSs, landing pages, e-commerce — anything that can render a `<script>`.

If a page loads the script over HTTPS, the tracker origin must also be HTTPS
(modern browsers block mixed content). See **Production hardening** below.

---

## Configuration (`.env`)

| Variable         | Description                                                            |
|------------------|------------------------------------------------------------------------|
| `API_URL`        | Base URL browsers use to reach this deployment. Must be reachable from the visitor's browser. |
| `API_KEY`        | Admin key. Logs into the dashboard; also authorizes reads (`/api/stats`, `/api/visits`). **Keep secret.** |
| `TRACKER_KEY`    | Write-only key embedded in the public `tracker.js`. Can only record visits, never read or log in. Falls back to `API_KEY` if not set. |
| `COOKIE_SECURE`  | `true` only behind HTTPS (makes the session cookie `Secure`). |

Generate strong random values, e.g.:

```bash
python3 -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(24)).decode())"
```

---

## Security model

- **The admin `API_KEY` is never sent to the browser.** Login exchanges it for
  an `HttpOnly`, `SameSite=Lax`, 12-hour session cookie — immune to JavaScript
  (`XSS`) theft and to basic `CSRF`.
- **The public script only carries a write-only `TRACKER_KEY`.** Even if
  someone sniffs the served `tracker.js`, all they can do is record visits;
  they cannot read statistics or access the dashboard.
- **CORS is wide open intentionally.** The tracker runs on any customer page
  from any origin and posts without cookies, so open CORS is not a credential
  leak. Only restrict origins if you never inject the script elsewhere.
- **Rate limiting** (slowapi) on write and read endpoints, returning `429`.
- **Startup fails fast** if `API_KEY` is missing (never run unauthenticated).

### Production hardening (recommended for the internet)

- Terminate **TLS** in front of the service (e.g. nginx, Caddy, or a
  Cloudflare Tunnel) and set `COOKIE_SECURE=true`.
- Set `API_URL` to the public HTTPS origin and make sure the tracker page's
  scheme matches (HTTPS page → HTTPS tracker).
- Use a **different** `TRACKER_KEY` per deployment, distinct from `API_KEY`.
- Optional: run the tracker behind an internal DNS entry (e.g.
  `http://tracker.internal`) and only expose `5000` inside the LAN.

---

## API

All endpoints except `/api/tracker.js`, `/api/auth/status`, `/api/login` and
`/api/logout` require authentication.

| Method | Path                     | Auth        | Description                                            |
|--------|--------------------------|-------------|--------------------------------------------------------|
| `POST` | `/api/track`             | tracker key | Record a visit (called by the embedded script).        |
| `GET`  | `/api/stats`             | session/API | Aggregated metrics (totals, by type, by provider).     |
| `GET`  | `/api/visits`            | session/API | Paginated history (`?page=1&limit=10`, max 100/page).  |
| `GET`  | `/api/tracker.js`        | public      | JavaScript snippet to embed on pages (embeds `API_URL`, `TRACKER_KEY`). |
| `POST` | `/api/login`             | —           | Exchange `API_KEY` for an `HttpOnly` session cookie.   |
| `POST` | `/api/logout`            | —           | Destroy the session cookie.                            |
| `GET`  | `/api/auth/status`       | —           | Whether the current session is valid.                  |

Interactive docs: `http://localhost:5000/docs`.

---

## Project layout

```
app/                 FastAPI backend
  main.py            routes + auth
  services.py        classification, sessions, stats, pagination
  models.py          Pydantic payloads
  database.py        SQLite connection + schema
  ai_crawlers.json   known AI crawler user-agent tokens
  tracker.js         embedded snippet template
dashboard/           Vue 3 + Vuetify frontend (built by Dockerfile)
data/                SQLite database (local runs) — gitignored
docker-compose.yml   production service
Dockerfile           builds frontend + backend image
```

---

## Data & privacy notes

- Data is stored **on your own server** (SQLite). Nothing leaves your
  infrastructure.
- The tracker sends: user-agent, page URL (`window.location.href`), and the
  document referrer. It does **not** store IP addresses (the schema has an
  `ip_hash` column but it is currently unused).
- Review applicable privacy/cookie laws (e.g. EU-GDPR, ePrivacy) for your own
  site; storing referrer + URL may require a consent notice depending on your
  jurisdiction.

---

## Roadmap / ideas

- Add an `ip_hash`/geo enrichment per visit (currently stored empty).
- Webhooks or email alerts when a new provider appears.
- Per-site keys and site filtering in the dashboard.
- Optional analytics export (CSV / JSON download).

---

## License

Private/internal use. Not for public resale.