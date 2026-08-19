# 14 — API Contract Plan

> **Related:** [05-srs.md](05-srs.md) · [06-system-architecture.md](06-system-architecture.md) · [15-ui-ux.md](15-ui-ux.md)

Conceptual backend API specification (pre-implementation).

---

## Conventions

- Base path: `/api/v1`
- Content-Type: `application/json`
- Error schema (all endpoints):

```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "Human-readable message",
    "details": {}
  }
}
```

---

## POST `/api/v1/analyze`

Submit a URL for analysis.

### Request

```json
{
  "url": "https://example.com/login",
  "deep_scan": false
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `url` | string | Yes | Valid HTTP/HTTPS URL; max 2048 chars |
| `deep_scan` | boolean | No | Default `false`; forces deep investigation |

### Response — Quick Scan (sync)

HTTP 200 — completed inline:

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "verdict": "Suspicious",
  "risk_score": 58,
  "confidence": 62,
  "summary": "...",
  "top_risk_factors": [],
  "scan_tier": "quick",
  "partial_analysis": false,
  "created_at": "2026-08-18T12:00:00Z",
  "completed_at": "2026-08-18T12:00:05Z"
}
```

### Response — Deep Scan (async)

HTTP 202 — processing:

```json
{
  "analysis_id": "uuid",
  "status": "processing",
  "message": "Deep scan in progress. Poll GET /analyze/{id} for results.",
  "created_at": "2026-08-18T12:00:00Z"
}
```

### Errors

| HTTP | Code | When |
|---|---|---|
| 400 | `INVALID_URL` | Malformed URL, wrong scheme, exceeds length |
| 403 | `BLOCKED_TARGET` | SSRF guard rejected target |
| 429 | `RATE_LIMIT_EXCEEDED` | User exceeded scan rate limit |
| 503 | `SYSTEM_OVERLOAD` | Queue full or system unavailable |

### Processing stages (logged internally)

1. `validating`
2. `quick_scan`
3. `decision_gate`
4. `deep_scan` (if applicable)
5. `aggregating`
6. `scoring`
7. `explaining`
8. `completed` / `partial` / `failed`

### Timeout behaviour

- Quick scan: abort and return partial result after 15s
- Deep scan: return partial result after 60s with `partial_analysis: true`

---

## GET `/api/v1/analyze/{analysis_id}`

Poll analysis status and retrieve result.

### Response — Processing

```json
{
  "analysis_id": "uuid",
  "status": "processing",
  "progress": {
    "current_stage": "deep_scan",
    "stages_completed": ["validating", "quick_scan", "decision_gate"]
  }
}
```

### Response — Completed

Full result payload (same as quick scan response + deep scan fields):

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "verdict": "Phishing",
  "risk_score": 82,
  "confidence": 78,
  "scan_tier": "deep",
  "partial_analysis": false,
  "completed_at": "2026-08-18T12:00:38Z"
}
```

### Response — Partial

```json
{
  "analysis_id": "uuid",
  "status": "partial",
  "verdict": "Suspicious",
  "partial_analysis": true,
  "limitations": ["Website unreachable; HTML analysis skipped"],
  "reason_code": "FETCH_TIMEOUT"
}
```

### Response — Failed

```json
{
  "analysis_id": "uuid",
  "status": "failed",
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Analysis could not be completed",
    "details": { "reason": "All evidence sources unavailable" }
  }
}
```

### Errors

| HTTP | Code | When |
|---|---|---|
| 404 | `NOT_FOUND` | Analysis ID does not exist |

---

## GET `/api/v1/analyze/{analysis_id}/evidence`

Full technical evidence payload for technical view.

### Response

```json
{
  "analysis_id": "uuid",
  "evidence_by_layer": {
    "url": [],
    "domain": [],
    "tls": [],
    "html": [],
    "threat_intel": [],
    "model": []
  },
  "redirect_chain": [],
  "features": {},
  "shap_values": [],
  "conflicts": [],
  "limitations": []
}
```

---

## GET `/api/v1/health`

Liveness and provider status.

### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "providers": {
    "phishtank": "available",
    "safe_browsing": "available",
    "virustotal": "degraded",
    "whois": "available"
  },
  "queue_depth": 2
}
```

---

## Rate Limiting

| Limit | Value | Header |
|---|---|---|
| Scans per IP per minute | 10 (TBD) | `X-RateLimit-Remaining` |
| Deep scans per IP per hour | 5 (TBD) | `X-RateLimit-Remaining` |

HTTP 429 returned when exceeded with `Retry-After` header.

---

## Authentication

v1 demo: **public read-only API with IP rate limiting** (see OQ-06).

Admin endpoints (if any): API key in `Authorization: Bearer {key}` header.
