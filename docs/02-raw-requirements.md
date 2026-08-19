# 02 — Raw Requirements

> **Related:** [03-requirement-clarification.md](03-requirement-clarification.md) · [05-srs.md](05-srs.md)

Initial requirements list without premature implementation decisions.

---

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | User can submit a URL for analysis |
| FR-02 | System validates and normalizes submitted URLs |
| FR-03 | System rejects dangerous/internal targets (SSRF protection) |
| FR-04 | System performs quick (URL + lightweight domain) analysis |
| FR-05 | System escalates to deep analysis when risk is uncertain or user opts in |
| FR-06 | System extracts URL lexical/structural features |
| FR-07 | System gathers domain intelligence (age, DNS, WHOIS where available) |
| FR-08 | System inspects TLS certificate properties |
| FR-09 | System follows redirects safely with limits |
| FR-10 | System fetches and analyzes static HTML (forms, title, content signals) |
| FR-11 | System queries external threat intelligence providers |
| FR-12 | System runs ML inference on available features |
| FR-13 | System aggregates evidence into risk score and classification |
| FR-14 | System computes confidence separately from risk |
| FR-15 | System generates human-readable explanation |
| FR-16 | System displays supporting evidence (simple + technical views) |
| FR-17 | System handles unavailable external sources gracefully |
| FR-18 | System reports analysis failures and partial results clearly |
| FR-19 | System logs analysis metadata for debugging (not full page content by default) |
| FR-20 | User can view analysis progress/status for long-running deep scans |

---

## Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | **Security:** Treat all submitted URLs as untrusted |
| NFR-02 | **Security:** Block private/internal IP ranges, localhost, link-local |
| NFR-03 | **Security:** Limit redirects, response size, timeouts |
| NFR-04 | **Privacy:** Minimize retention of URLs and fetched content |
| NFR-05 | **Reliability:** Single provider failure must not crash the system |
| NFR-06 | **Explainability:** Every classification cites contributing evidence |
| NFR-07 | **Performance:** Quick scan completes within TBD seconds (p95) |
| NFR-08 | **Performance:** Deep scan completes within TBD seconds (p95) |
| NFR-09 | **Usability:** Non-technical users understand verdict without jargon |
| NFR-10 | **Maintainability:** Evidence providers and feature extractors are pluggable |
| NFR-11 | **Extensibility:** New feature groups can be added without rewriting risk engine |
| NFR-12 | **Reproducibility:** Model versions, datasets, and splits are versioned |
| NFR-13 | **Rate limiting:** Respect external API quotas; internal rate limit on submissions |
| NFR-14 | **Availability:** TBD — student deployment target (single-instance acceptable) |
