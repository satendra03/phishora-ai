# 11 — External Intelligence Strategy

> **Related:** [06-system-architecture.md](06-system-architecture.md) · [12-risk-engine.md](12-risk-engine.md)

Evaluation, abstraction, and usage rules for external threat intelligence providers.

---

## Provider Evaluation

| Provider | Provides | Overlap | Free Tier | Recommendation |
|---|---|---|---|---|
| **Google Safe Browsing** | Known unsafe URLs | High with VT | Limited API | **Recommended** |
| **PhishTank** | Community phishing verification | Phishing-specific | Free API | **Recommended** |
| **VirusTotal** | Multi-engine URL verdict | Broad | 4 req/min free | **Recommended** (use sparingly) |
| **urlscan.io** | Scan reports, DOM, screenshot | Partial | Limited | **Optional** (deep scan) |
| **WHOIS/RDAP** | Registration data | Unique | Varies | **Recommended** (domain age) |

**Recommendation:** Limit to 3 TI providers (Safe Browsing, PhishTank, VirusTotal) for quota management. urlscan.io optional for deep scan demos.

---

## Provider Abstraction

Each provider implements a common interface:

```
ThreatIntelProvider:
  name: str
  purpose: str
  input_schema: dict
  output_schema: dict
  reliability_weight: float
  timeout_seconds: int
  cache_ttl_seconds: int

  query(url: str) -> ProviderResult
  on_failure() -> UnavailableResult
```

### ProviderResult schema

```json
{
  "provider": "phishtank",
  "status": "success",
  "verdict": "phishing",
  "raw_response": {},
  "queried_at": "2026-08-18T12:00:00Z",
  "cache_hit": false
}
```

### UnavailableResult schema

```json
{
  "provider": "virustotal",
  "status": "unavailable",
  "reason": "rate_limit_exceeded",
  "queried_at": "2026-08-18T12:00:00Z"
}
```

---

## Per-Provider Specification

### Google Safe Browsing

| Field | Value |
|---|---|
| Purpose | Check URL against Google's unsafe URL lists |
| Input | Normalized URL |
| Output | `{ "threat_types": ["SOCIAL_ENGINEERING"], "platforms": ["ANY_PLATFORM"] }` |
| Reliability weight | 0.85 |
| Timeout | 5s |
| Cache TTL | 24h (negative), 1h (positive) |
| Free-tier constraint | API key required; daily quota limits |
| Failure behaviour | Mark unavailable; redistribute weight |
| Contribution | Strong positive signal when match; neutral when no match |

### PhishTank

| Field | Value |
|---|---|
| Purpose | Community-verified phishing database |
| Input | Normalized URL |
| Output | `{ "in_database": true, "verified": true, "verified_at": "..." }` |
| Reliability weight | 0.90 (verified), 0.70 (unverified) |
| Timeout | 5s |
| Cache TTL | 1h |
| Free-tier constraint | Free API with rate limits |
| Failure behaviour | Mark unavailable |
| Contribution | High-weight evidence when verified phishing |

### VirusTotal

| Field | Value |
|---|---|
| Purpose | Multi-engine URL scan aggregation |
| Input | Normalized URL |
| Output | `{ "malicious": 3, "suspicious": 1, "harmless": 60, "undetected": 5 }` |
| Reliability weight | 0.80 |
| Timeout | 10s |
| Cache TTL | 24h |
| Free-tier constraint | 4 requests/minute (public API) |
| Failure behaviour | Mark unavailable; do not block analysis |
| Contribution | Corroborating signal; use malicious count threshold |

### WHOIS/RDAP (Domain Intelligence)

| Field | Value |
|---|---|
| Purpose | Domain registration age and metadata |
| Input | Registered domain (extracted from URL) |
| Output | `{ "creation_date": "...", "registrar": "...", "privacy_enabled": true }` |
| Reliability weight | 0.75 |
| Timeout | 8s |
| Cache TTL | 7 days |
| Failure behaviour | Features marked missing; confidence reduced |
| Contribution | Domain age feeds feature set and evidence layer |

---

## Usage Rules

1. TI results are **evidence items**, not the final verdict.
2. Cache results to respect quotas (TTL: 24h negatives, 1h positives — TBD after quota testing).
3. Query providers in parallel with individual timeouts; do not wait for slowest provider beyond global timeout.
4. Display provider name, timestamp, and raw verdict in technical panel.
5. Never call all providers for quick scan — reserve VirusTotal for deep scan or uncertain cases.
6. Log provider failures for monitoring; alert if failure rate exceeds threshold.

---

## Graceful Degradation

| Scenario | Behaviour |
|---|---|
| Single provider down | Continue; mark unavailable; reduce confidence slightly |
| All TI providers down | URL/domain/HTML/ML evidence still produces verdict; confidence significantly reduced |
| Rate limit hit | Return cached result if available; else mark unavailable |
| Timeout | Mark unavailable after timeout; do not retry synchronously |

---

## Caching Strategy

| Cache Key | TTL | Storage |
|---|---|---|
| `ti:{provider}:{url_hash}` | Provider-specific | Redis |
| `whois:{domain}` | 7 days | Redis |
| `dns:{domain}` | 1 hour | Redis |

Cache invalidation: manual flush for testing; automatic expiry otherwise.
