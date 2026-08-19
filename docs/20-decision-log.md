# 20 — Decision Log

> **Related:** [04-project-constitution.md](04-project-constitution.md) · [19-development-roadmap.md](19-development-roadmap.md)

Record of major architectural and design decisions with alternatives, rationale, and consequences.

---

## Entry Format

```
## DEC-XXX: Title
- **Date:**
- **Context:**
- **Options considered:**
- **Decision:**
- **Rationale:**
- **Consequences:**
```

---

## DEC-001: Tiered Analysis Architecture

- **Date:** 2026-08-18
- **Context:** RC-01 — Should every submitted website be actively fetched? Active fetching introduces SSRF risk, latency, and exposure to malicious content.
- **Options considered:**
  - (A) Always perform deep fetch for every URL
  - (B) Never fetch; URL and passive analysis only
  - (C) Tiered: quick scan first; deep fetch only when uncertain or user opts in
- **Decision:** **(C) Tiered analysis**
- **Rationale:** Balances safety (minimal active fetching), speed (quick scan ≤8s), and academic depth (deep scan available). Avoids unnecessary exposure to malicious content for obviously safe or obviously suspicious URLs.
- **Consequences:** Requires decision gate logic in pipeline. ML models must work at multiple feature tiers. UI needs quick/deep scan modes.

---

## DEC-002: Three-Class Output (Safe / Suspicious / Phishing)

- **Date:** 2026-08-18
- **Context:** RC-06 — Binary classification forces borderline cases into false certainty.
- **Options considered:**
  - (A) Binary: Safe vs Phishing
  - (B) Three-class: Safe / Suspicious / Phishing
  - (C) Continuous risk score only (no discrete label)
- **Decision:** **(B) Three-class output** with continuous risk score 0–100
- **Rationale:** "Suspicious" honestly communicates uncertainty. Many real-world cases are borderline (new domain with login form, URL shortener, etc.). Binary output would inflate false confidence.
- **Consequences:** Training remains binary (legitimate vs phishing) but inference maps to three tiers via thresholds. UI needs three distinct visual states. Evaluation must report per-class metrics for Suspicious.

---

## DEC-003: Separate Risk Score and Confidence Score

- **Date:** 2026-08-18
- **Context:** RC-05 — Risk and confidence are often conflated in security tools, misleading users.
- **Options considered:**
  - (A) Single combined score
  - (B) Separate risk and confidence scores
  - (C) Risk score + confidence interval (statistical)
- **Decision:** **(B) Separate risk score (0–100) and confidence score (0–100)**
- **Rationale:** A site can be high-risk but low-confidence (suspicious signals but limited evidence) or low-risk but low-confidence (few signals available). Users and evaluators need both dimensions.
- **Consequences:** Risk engine must implement separate calculation paths. UI displays two meters. Explainability must explain confidence factors.

---

## DEC-004: Evidence Fusion Instead of API Score Averaging

- **Date:** 2026-08-18
- **Context:** RC-07 — Multiple TI APIs often disagree; naive averaging hides nuance and fails when APIs unavailable.
- **Options considered:**
  - (A) Fixed weighted average (e.g., 40% ML + 60% APIs)
  - (B) Majority vote across APIs
  - (C) Reliability-weighted evidence fusion with conflict flagging
- **Decision:** **(C) Evidence-based fusion** per [12-risk-engine.md](12-risk-engine.md)
- **Rationale:** Sources have different reliability, coverage, and correlation. Missing data breaks fixed weights. Fusion allows graceful degradation and surfaces conflicts to users.
- **Consequences:** More complex risk engine implementation. Each evidence item needs normalization to common scale. Explainability must show individual evidence contributions.

---

## DEC-005: Mixed-Audience UI (Simple + Technical Views)

- **Date:** 2026-08-18
- **Context:** Primary user selection — general public, technical users, and academic evaluators all need different depth.
- **Options considered:**
  - (A) Simple UI only (general public)
  - (B) Technical UI only (security professionals)
  - (C) Simple default + expandable technical panel
- **Decision:** **(C) Mixed-audience UI** with progressive disclosure
- **Rationale:** Academic demo needs technical depth for evaluators. General users need plain-language verdicts. Progressive disclosure serves both without overwhelming non-technical users.
- **Consequences:** Frontend has two view modes. API must return both summary and full evidence payload. Explainability engine produces both plain-language and structured output.

---

## DEC-006: Static HTML Analysis Only (No JS Execution)

- **Date:** 2026-08-18
- **Context:** RC-02 — JavaScript-heavy websites require headless browser; also increases security risk.
- **Options considered:**
  - (A) Full headless browser (Playwright) for all fetches
  - (B) Static HTTP fetch + HTML parse only
  - (C) Static by default; optional Playwright for deep scan
- **Decision:** **(B) Static fetch for core path**; Playwright optional for deep scan screenshots only (DEC-007)
- **Rationale:** Most phishing credential forms are in static HTML. JS rendering is expensive, risky, and hard to evaluate fairly. Static analysis is sufficient for core feature set (F24–F30).
- **Consequences:** JS-rendered login forms will be missed. Limitation must be documented in UI. Optional Playwright adds complexity if pursued.

---

## DEC-007: Playwright Optional for Deep Scan Screenshots

- **Date:** 2026-08-18
- **Context:** OQ-07 — Screenshots useful for demo but visual ML is out of scope.
- **Options considered:**
  - (A) Include Playwright in core pipeline
  - (B) No browser automation at all
  - (C) Optional Playwright for screenshot capture in deep scan only
- **Decision:** **(C) Optional** — defer until core pipeline complete
- **Rationale:** Screenshots aid demo and user trust but are not required for detection. Visual ML is future work. Optional status prevents scope creep.
- **Consequences:** May not be implemented if timeline is tight. Demo can use static HTML evidence instead.

---

## DEC-008: Domain-Level Train/Test Split

- **Date:** 2026-08-18
- **Context:** Dataset strategy — random URL splits cause same domain in train and test, inflating metrics.
- **Options considered:**
  - (A) Random URL split (80/20)
  - (B) Domain-level split (no domain overlap)
  - (C) Campaign-level split
- **Decision:** **(B) Domain-level split** (60/20/20 train/val/test) plus separate temporal hold-out
- **Rationale:** Model must generalize to unseen domains, not just unseen URLs on known domains. Domain split gives realistic performance estimate. Temporal hold-out additionally tests concept drift.
- **Consequences:** Smaller effective training set (one domain = one or few URLs for negatives). Must document domain counts alongside URL counts.

---

## DEC-009: LightGBM as Primary ML Model

- **Date:** 2026-08-18
- **Context:** ML model selection for tabular engineered features.
- **Options considered:**
  - (A) Logistic Regression only
  - (B) Random Forest
  - (C) LightGBM
  - (D) Neural network on raw URL characters
- **Decision:** **Logistic Regression for Experiment A baseline; LightGBM as primary model**
- **Rationale:** LightGBM consistently strong on tabular data with mixed feature types. SHAP integration available. Logistic Regression provides interpretable baseline for comparison.
- **Consequences:** Two models to maintain. Hyperparameter tuning needed for LightGBM. SHAP computation adds inference latency (acceptable for deep scan).

---

## DEC-010: Three TI Providers (PhishTank, Safe Browsing, VirusTotal)

- **Date:** 2026-08-18
- **Context:** OQ-04 — External intelligence provider selection and quota management.
- **Options considered:**
  - (A) Single provider (VirusTotal only)
  - (B) Three providers: PhishTank + Safe Browsing + VirusTotal
  - (C) Five+ providers including urlscan.io
- **Decision:** **(B) Three providers** — urlscan.io deferred to optional
- **Rationale:** Three providers give phishing-specific (PhishTank), broad safety (Safe Browsing), and multi-engine (VirusTotal) coverage without exhausting free-tier quotas. More providers add complexity with diminishing returns.
- **Consequences:** Must implement caching and quota-aware usage. VirusTotal limited to 4 req/min on free tier — use for deep scan only.

---

## DEC-011: SSOT Documentation Structure

- **Date:** 2026-08-18
- **Context:** Need single authoritative source for all project decisions before implementation begins.
- **Options considered:**
  - (A) Single monolithic document
  - (B) 20-document SSOT structure with cross-links
  - (C) Wiki-style documentation
- **Decision:** **(B) 20-document SSOT structure** in `docs/` directory
- **Rationale:** Separates concerns (requirements, architecture, ML, security, etc.). Enables targeted updates without rewriting entire plan. Decision log provides audit trail.
- **Consequences:** Must maintain cross-links when documents change. Change control process required (see docs/README.md).

---

## Pending Decisions

| ID | Topic | Blocker | Target Phase |
|---|---|---|---|
| DEC-012 | Uncertain band thresholds (35–65 initial) | Experiment A baseline | Phase 5 |
| DEC-013 | Final feature set after ablation | Experiment A ablation | Phase 5 |
| DEC-014 | PostgreSQL vs SQLite for demo | Deployment testing | Phase 9 |
| DEC-015 | URL retention policy | Privacy review | Phase 9 |
| DEC-016 | Playwright inclusion | Timeline assessment | Phase 4+ |

---

## Decision Review Schedule

- Review all pending decisions at phase boundaries
- Update this log before starting each new phase
- Link experiment results to decisions they validate (e.g., DEC-012 validated by Experiment A metrics)
