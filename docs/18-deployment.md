# 18 — Deployment and Technology Evaluation

> **Related:** [06-system-architecture.md](06-system-architecture.md) · [19-development-roadmap.md](19-development-roadmap.md)

Technology selection justified by requirements and deployment plan.

---

## Technology Evaluation

Selections are **recommendations** until validated during implementation.

| Need | Options | Recommendation | Pros | Cons | Reason |
|---|---|---|---|---|---|
| **Frontend** | React, Vue, Svelte | **React + TypeScript** | Large ecosystem, component libraries, TypeScript safety | Bundle size | Dashboard UI, wide hiring familiarity |
| **Backend** | FastAPI, Flask, Django | **FastAPI** | Async I/O, auto OpenAPI docs, Pydantic validation | Younger ecosystem | Parallel TI calls, API-first design |
| **ML** | sklearn, XGBoost, LightGBM | **sklearn + LightGBM** | Strong tabular performance, SHAP support | Tuning needed | Engineered features are tabular |
| **HTTP fetch** | httpx, requests, aiohttp | **httpx** | Async, timeout control, HTTP/2 | — | Safe fetch worker needs async + limits |
| **HTML parse** | BeautifulSoup, lxml, selectolax | **BeautifulSoup + lxml** | Simple API, adequate for static analysis | Slower than selectolax | Sufficient for v1 scale |
| **Job queue** | Celery, RQ, ARQ | **ARQ** | Lightweight, async-native, Redis-backed | Less mature than Celery | Student project simplicity |
| **Cache** | Redis, Memcached | **Redis** | TI/DNS caching, also backs ARQ | Requires separate service | Dual purpose |
| **Database** | SQLite, PostgreSQL | **PostgreSQL** (SQLite for early dev) | Analysis history, concurrent access | Setup overhead | SQLite fine until Phase 9 |
| **Container** | Docker Compose | **Docker Compose** | Isolated fetch worker, reproducible | Local resource use | Required for safe fetch isolation |
| **Deploy** | Render, Railway, VPS | **Railway or Render** | Free-tier friendly, Docker support | Cold starts | Student-accessible hosting |
| **Optional: Playwright** | Puppeteer, Playwright | **Playwright in Docker** | Screenshot capture | Heavy, risky | Deep scan only, disabled by default |

---

## Architecture Stack Diagram

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│    Redis    │
│  Frontend   │     │   Backend   │     │   (cache)   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │     ARQ     │
                    │   Worker    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Safe    │ │    ML    │ │    TI    │
        │  Fetch   │ │ Inference│ │ Adapters │
        │ (Docker) │ │ Service  │ │          │
        └──────────┘ └──────────┘ └──────────┘
                           │
                    ┌──────┴──────┐
                    │ PostgreSQL  │
                    │  (metadata) │
                    └─────────────┘
```

---

## Docker Compose Services

| Service | Image/Base | Purpose |
|---|---|---|
| `frontend` | Node 20 + React | Web UI |
| `api` | Python 3.11 + FastAPI | API orchestration |
| `worker` | Python 3.11 + ARQ | Async deep scan jobs |
| `fetch-worker` | Python 3.11 (isolated network) | Safe HTTP fetch |
| `redis` | Redis 7 | Cache + queue |
| `db` | PostgreSQL 15 | Analysis metadata |

### Fetch worker isolation

- Separate Docker network with no access to internal services
- Egress only to public internet
- No access to `db` or `redis` internal URLs

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `DATABASE_URL` | api, worker | PostgreSQL connection string |
| `REDIS_URL` | api, worker | Redis connection string |
| `PHISHTANK_API_KEY` | api, worker | PhishTank API key |
| `GOOGLE_SAFEBROWSING_KEY` | api, worker | Google Safe Browsing API key |
| `VIRUSTOTAL_API_KEY` | api, worker | VirusTotal API key |
| `MODEL_PATH` | api, worker | Path to trained ML model artifact |
| `FETCH_WORKER_URL` | api | Internal URL for isolated fetch worker |
| `RATE_LIMIT_PER_MINUTE` | api | User rate limit (default 10) |
| `LOG_LEVEL` | all | Logging verbosity |

Secrets must never be committed to the repository.

---

## Deployment Targets

### Development

```bash
docker compose up --build
```

Local development with hot reload for frontend and API.

### Demo/Production (Railway or Render)

- Docker Compose or individual service containers
- Managed PostgreSQL and Redis (provider add-ons)
- Environment variables configured in provider dashboard
- Custom domain optional

### Constraints

| Constraint | Mitigation |
|---|---|
| Free-tier CPU/memory | Limit concurrent deep scans to 3 |
| Free-tier API quotas | Cache aggressively; tiered TI usage |
| No static IP | Use provider's outbound IP (acceptable for fetch) |
| Cold starts | Health check endpoint; keep-alive ping for demo |

---

## ML Model Deployment

| Aspect | Approach |
|---|---|
| Model format | LightGBM `.txt` or `.pkl` via joblib |
| Versioning | `{model_name}_v{version}_exp{letter}` in `models/` |
| Loading | Load at API startup; reload on version change |
| Inference latency | Target < 100ms for feature vector scoring |
| SHAP | Pre-compute background dataset; compute on demand |

---

## Monitoring (Minimal for v1)

| Metric | Method |
|---|---|
| API request count | FastAPI middleware logging |
| Analysis latency | Log `completed_at - created_at` |
| Provider failure rate | Log TI adapter failures |
| Queue depth | Redis queue length check in `/health` |
| Error rate | Log 5xx responses |

Full observability (Prometheus, Grafana) is **future work**.

---

## Backup and Recovery

- Database: provider-managed backups (Railway/Render)
- Model artifacts: version-controlled in repo or object storage
- No user data backup needed (minimal retention policy)

---

## Open Technology Decisions

| ID | Question | Status |
|---|---|---|
| OQ-03 | PostgreSQL vs SQLite for production demo | PostgreSQL recommended; decide in Phase 9 |
| OQ-07 | Playwright for deep scan screenshots | Optional; defer until core pipeline works |
