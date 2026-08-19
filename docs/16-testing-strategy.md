# 16 — Testing Strategy

> **Related:** [07-threat-model.md](07-threat-model.md) · [10-ml-specification.md](10-ml-specification.md) · [14-api-contract.md](14-api-contract.md)

Software, ML, security, and real-world evaluation testing plan.

---

## Software Testing

### Unit tests

| Component | Test Cases |
|---|---|
| URL parser | Valid/invalid URLs, punycode, IP-based, port numbers, long URLs |
| URL feature extractor | Each feature with known inputs and expected outputs |
| SSRF guard | Blocked IPs, allowed public IPs, encoded URLs |
| Domain extractor | Subdomain parsing, registered domain extraction |
| HTML analyzer | Form detection, password fields, hidden inputs, iframes |
| Risk engine | Score calculation, weight redistribution, threshold mapping |
| Confidence engine | Completeness, agreement, conflict detection |
| Evidence templates | Template rendering with variable substitution |

### Integration tests

| Integration | Test Cases |
|---|---|
| TI provider adapters | Mock API responses; success, timeout, rate limit, unavailable |
| DNS/WHOIS lookup | Mock resolver; missing records, privacy-enabled domains |
| Safe fetch worker | Mock HTTP responses; redirects, timeouts, large responses |
| ML inference | Load test model; predict on fixture feature vectors |
| Cache layer | Hit/miss/expiry behaviour |

### API tests

| Endpoint | Test Cases |
|---|---|
| POST `/analyze` | Valid URL, invalid URL, blocked target, rate limit |
| GET `/analyze/{id}` | Processing, completed, partial, failed, not found |
| GET `/analyze/{id}/evidence` | Full payload structure validation |
| GET `/health` | Provider status reporting |

### End-to-end tests

- Submit known-safe URL → receive Safe verdict with evidence
- Submit URL triggering deep scan → poll until completed
- Submit invalid URL → receive 400 error
- Submit SSRF payload → receive 403 error
- Tool: Playwright or Cypress against running stack

---

## ML Testing

### Evaluation protocol

- **Primary test set:** Domain-holdout 20% split (never seen domains)
- **Temporal test set:** Recent phishing URLs (last 3–6 months, not in train/val)
- **Legitimacy stress test:** Random Tranco top-10k sample for false positive rate

### Metrics (report all)

| Metric | Purpose |
|---|---|
| Accuracy | Overall correctness (misleading with imbalance — report alongside others) |
| Precision (per class) | False positive control |
| Recall (per class) | Detection rate |
| F1 (macro and per class) | Balance of precision/recall |
| ROC-AUC | Ranking quality |
| PR-AUC | Important for imbalanced data |
| Confusion matrix | Error pattern analysis |
| Calibration (Brier score) | Probability reliability |

### Experiment-specific tests

| Experiment | Additional Test |
|---|---|
| A (URL-only) | Feature ablation — remove each feature, measure delta |
| B (+ domain) | Compare domain-holdout F1 vs Experiment A |
| C (+ TLS) | Subset with successful TLS handshake only |
| D (+ HTML) | Subset with successful fetch only |
| E (+ TI) | Compare with/without TI features on same test set |
| F (full pipeline) | End-to-end vs model-only on real-world evaluation set |

### Error analysis

- **False positives:** Manual review of top 20 Tranco sites flagged as phishing
- **False negatives:** Manual review of recent PhishTank misses
- Document patterns in final report

---

## Security Testing

### SSRF test payloads

| Payload | Expected Result |
|---|---|
| `http://127.0.0.1/admin` | Blocked (403) |
| `http://localhost/` | Blocked (403) |
| `http://169.254.169.254/` | Blocked (403) |
| `http://10.0.0.1/` | Blocked (403) |
| `http://192.168.1.1/` | Blocked (403) |
| `http://[::1]/` | Blocked (403) |
| `file:///etc/passwd` | Blocked (400 — invalid scheme) |
| `http://2130706433/` (decimal IP) | Blocked (403) |
| `http://0x7f000001/` (hex IP) | Blocked (403) |

### Redirect abuse

| Test | Expected Result |
|---|---|
| Redirect chain > 5 hops | Stop at 5; flag in evidence |
| Redirect to internal IP | Block at redirect hop |
| Redirect to different scheme (javascript:) | Block |

### Resource exhaustion

| Test | Expected Result |
|---|---|
| 10 MB response body | Truncate at 2 MB limit |
| Slow response (>10s) | Timeout; partial result |
| 20+ concurrent deep scans | Queue or reject with 503 |

### Content safety

| Test | Expected Result |
|---|---|
| Malformed HTML | Parse gracefully; extract what's possible |
| HTML with embedded scripts | Parse only; do not execute |
| Polyglot file served as text/html | Size limit prevents issues |
| Malformed punycode | Validation error or safe fallback |

### DNS rebinding

- Document manual test procedure (requires controlled DNS server)
- Verify IP pinning prevents rebinding attack

---

## Real-World Evaluation Set

Curated manual test set (not used for ML training metrics):

| Category | Count | Source |
|---|---|---|
| Known legitimate | 100 | Diverse Tranco sample (news, e-commerce, gov, edu) |
| Known phishing | 100 | Recent PhishTank verified |
| Borderline | 50 | URL shorteners, aged domains with login forms, new legitimate startups |

**Rules:**

- Manually document expected difficulty for borderline cases
- Do not auto-label borderline as ground truth for metric calculation
- Use for demo script and qualitative evaluation

---

## Test Infrastructure

| Tool | Purpose |
|---|---|
| pytest | Unit and integration tests |
| pytest-asyncio | Async API tests |
| httpx mock | HTTP client mocking |
| Playwright | E2E UI tests |
| Great Expectations (optional) | Data validation for datasets |

---

## Coverage Targets

| Area | Target |
|---|---|
| SSRF guard | 100% branch coverage |
| Risk engine | ≥ 90% line coverage |
| Feature extractors | ≥ 85% line coverage |
| API endpoints | All happy paths + primary error paths |
| ML pipeline | Reproducible notebook with fixed seed |

---

## Test Data Management

- Unit tests use fixtures in `tests/fixtures/`
- No live phishing URLs in unit tests — use mocked responses
- Integration tests may use known-safe public URLs (e.g., `https://example.com`)
- Security tests run in isolated CI environment
