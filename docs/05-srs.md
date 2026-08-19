# 05 — Software Requirements Specification (SRS)

> **Related:** [02-raw-requirements.md](02-raw-requirements.md) · [03-requirement-clarification.md](03-requirement-clarification.md) · [14-api-contract.md](14-api-contract.md)

Consolidated functional and non-functional requirements with acceptance-oriented wording.

---

## Functional Requirements

| ID | Requirement | Acceptance Criteria |
|---|---|---|
| FR-01 | System accepts HTTP/HTTPS URLs for analysis | URLs up to 2048 characters accepted; other schemes rejected |
| FR-02 | System validates and normalizes submitted URLs | Invalid URLs return structured validation errors without analysis |
| FR-03 | System rejects dangerous/internal targets | Internal IPs, localhost, non-http schemes return security rejection (403) |
| FR-04 | System performs quick scan | Returns classification, risk, confidence, and top evidence within NFR-07 |
| FR-05 | System escalates to deep analysis | Triggered when risk ∈ uncertain band (35–65) OR user selects Deep Scan |
| FR-06 | System extracts URL lexical/structural features | All Tier 0 features computed per [09-feature-specification.md](09-feature-specification.md) |
| FR-07 | System gathers domain intelligence | DNS, WHOIS/RDAP, Tranco lookup where available |
| FR-08 | System inspects TLS certificate properties | Validity, issuer, domain match evaluated on deep scan |
| FR-09 | System follows redirects safely | Max 5 redirects; each hop validated against SSRF guard |
| FR-10 | System analyzes static HTML | Forms, titles, keywords, external resources parsed without JS execution |
| FR-11 | System queries external TI providers | At least PhishTank + Safe Browsing in recommended configuration |
| FR-12 | System runs ML inference | Model version logged; probability available as evidence item |
| FR-13 | System produces risk score and classification | Score 0–100; label ∈ {Safe, Suspicious, Phishing} |
| FR-14 | System computes confidence separately | Confidence 0–100 with breakdown of contributing factors |
| FR-15 | System generates human-readable explanation | ≥3 evidence items when available; fewer if data sparse |
| FR-16 | System displays evidence in dual views | Simple View (default) + Technical Evidence View |
| FR-17 | System handles unavailable providers | Provider marked `unavailable`; weight redistributed |
| FR-18 | System reports partial results | `partial_analysis: true` with explicit reason codes on timeout/unreachable |
| FR-19 | System logs analysis metadata | Analysis ID, timestamps, verdict, scores; no full HTML by default |
| FR-20 | User can poll deep scan status | Async job with processing/completed/partial/failed states |

---

## Non-Functional Requirements

| ID | Requirement | Target | Status |
|---|---|---|---|
| NFR-01 | Security: untrusted URL input | All inputs validated before any network action | Design decision |
| NFR-02 | Security: block internal targets | RFC1918, localhost, link-local, metadata IPs blocked | Design decision |
| NFR-03 | Security: resource limits | Max redirects: 5; timeout: 10s/hop; max response: 2 MB | Design decision |
| NFR-04 | Privacy: minimal retention | No default HTML persistence; URL hash preferred | Design decision |
| NFR-05 | Reliability: graceful degradation | Single provider failure does not crash analysis | Design decision |
| NFR-06 | Explainability | Every classification cites contributing evidence | Design decision |
| NFR-07 | Performance: quick scan | p95 ≤ 8s | TBD — validate in Phase 9 |
| NFR-08 | Performance: deep scan | p95 ≤ 45s | TBD — validate in Phase 9 |
| NFR-09 | Usability | Non-technical users understand verdict without jargon | Validate in UI testing |
| NFR-10 | Maintainability | Pluggable extractors and TI providers | Architecture requirement |
| NFR-11 | Extensibility | New feature groups without risk engine rewrite | Architecture requirement |
| NFR-12 | Reproducibility | Versioned datasets, models, splits | Document in SSOT |
| NFR-13 | Rate limiting | 10 scans/min/IP (TBD); respect external API quotas | TBD |
| NFR-14 | Availability | 95% uptime on demo deployment | Student-realistic |

---

## Traceability Matrix (Summary)

| Use Case | Requirements |
|---|---|
| UC-01 Quick check | FR-01, FR-04, FR-06, FR-12, FR-13, FR-15, NFR-07 |
| UC-02 Deep investigation | FR-05, FR-08–FR-11, FR-20, NFR-08 |
| UC-03 Technical review | FR-16, FR-15 |
| UC-04 Partial failure | FR-17, NFR-05 |
| UC-05 Unreachable site | FR-18, NFR-06 |
