# 19 — Development Roadmap

> **Related:** [01-project-overview.md](01-project-overview.md) · [20-decision-log.md](20-decision-log.md) · [18-deployment.md](18-deployment.md)

Phased development plan, risks, definition of done, and open questions.

---

## Development Phases

Dependency-ordered phases (adjust durations to academic calendar):

| Phase | Name | Deliverable | Dependencies |
|---|---|---|---|
| **0** | Planning | SSOT approved, decision log initialized | — |
| **1** | Data | Dataset v1 curated, domain splits, data spec | Phase 0 |
| **2** | URL engine | URL features + Experiment A baseline | Phase 1 |
| **3** | Domain/TLS | DNS, WHOIS, TLS features + Experiments B/C | Phase 2 |
| **4** | Safe fetch | Isolated fetch worker + HTML features + Experiment D | Phase 3 |
| **5** | ML | LightGBM training, calibration, SHAP | Phases 2–4 |
| **6** | Threat intel | Provider adapters + Experiment E | Phase 5 |
| **7** | Risk engine | Fusion, confidence, conflict rules | Phase 6 |
| **8** | Explainability | Evidence templates + ML explanations | Phase 7 |
| **9** | Backend API | Orchestration, async deep scan, caching | Phases 7–8 |
| **10** | Frontend | Simple + technical UI, all states | Phase 9 |
| **11** | Integration | End-to-end pipeline | Phases 9–10 |
| **12** | Security testing | SSRF suite, abuse cases | Phase 11 |
| **13** | Evaluation | RQ1–8 experiments, final report | Phase 12 |
| **14** | Deployment | Dockerized demo environment | Phase 13 |
| **15** | Documentation | Final report, demo script, poster | Phase 14 |

---

## Phase Details

### Phase 0 — Planning (Current)

- [x] SSOT documentation structure created
- [x] Decision log initialized
- [x] Data specification drafted
- [x] Feature specification drafted
- [x] Threat model documented

### Phase 1 — Data

- Collect and normalize phishing URLs (PhishTank, OpenPhish)
- Collect legitimate URLs (Tranco top-1M)
- Apply label normalization rules
- Deduplicate by URL and domain
- Create domain-level train/val/test splits
- Create temporal hold-out set
- Document dataset statistics in [08-data-specification.md](08-data-specification.md)

### Phase 2 — URL Engine

- Implement URL parser and normalizer
- Implement 15 URL features (Tier 0)
- Train Logistic Regression baseline (Experiment A)
- Document baseline metrics

### Phase 3 — Domain/TLS

- Implement DNS, WHOIS/RDAP, Tranco lookup
- Implement TLS certificate inspection
- Add domain features (Tier 1)
- Run Experiments B and C

### Phase 4 — Safe Fetch

- Implement SSRF guard module
- Implement isolated fetch worker (Docker)
- Implement HTML analyzer (forms, titles, scripts)
- Add HTML features (Tier 2)
- Run Experiment D

### Phase 5 — ML

- Train LightGBM on full feature set
- Hyperparameter tuning on validation set
- Calibration (Platt scaling if needed)
- SHAP analysis
- Feature ablation study

### Phase 6 — Threat Intel

- Implement TI provider adapters (PhishTank, Safe Browsing, VirusTotal)
- Add TI features (Tier 3)
- Run Experiment E
- Implement caching layer

### Phase 7 — Risk Engine

- Implement evidence aggregation
- Implement risk score calculation
- Implement confidence calculation
- Implement conflict detection
- Validate on hold-out set

### Phase 8 — Explainability

- Implement evidence templates
- Integrate SHAP into explanation output
- Implement summary generation
- Test explanation quality manually

### Phase 9 — Backend API

- Implement FastAPI endpoints per [14-api-contract.md](14-api-contract.md)
- Implement async deep scan with ARQ
- Implement rate limiting
- Integration tests

### Phase 10 — Frontend

- Implement React UI per [15-ui-ux.md](15-ui-ux.md)
- All UI states
- Simple + technical views
- E2E tests

### Phase 11 — Integration

- End-to-end pipeline testing
- Performance profiling (latency targets)
- Bug fixes

### Phase 12 — Security Testing

- SSRF test suite
- Redirect abuse tests
- Resource exhaustion tests
- Fix any vulnerabilities found

### Phase 13 — Evaluation

- Complete Experiments A–F
- Populate results in [17-evaluation-methodology.md](17-evaluation-methodology.md)
- Error analysis
- Update decision log with evidence-based decisions

### Phase 14 — Deployment

- Docker Compose production config
- Deploy to Railway/Render
- Verify demo accessibility

### Phase 15 — Documentation

- Final project report
- Demo script
- Poster/presentation content

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| API quota exhaustion | Deep scan fails | Medium | Cache, tiered usage, limit deep scans |
| SSRF vulnerability | Critical security issue | Low if tested | Dedicated guard module + security test suite |
| Dataset leakage | Invalid ML results | Medium | Domain/time splits, documented protocol |
| WHOIS unavailable | Missing features | High | Graceful missing handling; reduce confidence |
| Phishing page exploits fetch worker | High | Low | Isolation, no JS exec, size/time limits |
| Over-scoping | Project incomplete | High | Strict Core/Recommended/Optional tiers |
| False confidence in TI | Wrong verdicts | Medium | TI as evidence only; show conflicts |
| Class imbalance | Poor precision | High | PR-AUC focus, threshold tuning, class weights |
| Legal/ethical fetch concerns | Academic issue | Low | Public URLs only, identifiable UA, no auth bypass |
| Timeline slip | Incomplete project | Medium | Prioritize Core tier; defer Optional features |

---

## Definition of Done

Phishora AI v1 is **done** when:

- [x] SSOT documentation complete and version-controlled
- [ ] Core analysis pipeline operational (URL → domain → TLS → HTML → TI → risk)
- [ ] Tiered quick/deep scan implemented
- [ ] ML experiments A–F executed with documented results
- [ ] Risk engine with separate risk and confidence validated on hold-out sets
- [ ] Explainability outputs for both evidence and ML
- [ ] SSRF/security test suite passing
- [ ] UI covers all defined states (simple + technical views)
- [ ] Deployed demo accessible to evaluators
- [ ] Final report links design decisions to experimental evidence
- [ ] Decision log updated for all major choices

---

## Open Questions / Decisions Required

| ID | Question | Status | Recommendation |
|---|---|---|---|
| OQ-01 | Exact uncertain band thresholds for tier escalation | TBD after Experiment A | Start with 35–65; tune on validation |
| OQ-02 | Final feature count after ablation | TBD in Phase 5 | Target 25–35; prune redundant |
| OQ-03 | PostgreSQL vs SQLite for production demo | TBD in Phase 9 | PostgreSQL for demo |
| OQ-04 | Include urlscan.io or limit to 3 TI providers | Open | Max 3 for quota management |
| OQ-05 | URL retention policy (hash only vs full URL) | Open | Hash + optional full with consent |
| OQ-06 | Authentication for API (public demo vs API key) | Open | Public demo with rate limit |
| OQ-07 | Playwright deep scan: include or defer | Open | Optional if time permits |
| OQ-08 | Exact p95 latency targets | TBD after Phase 9 profiling | Quick ≤8s, deep ≤45s initial targets |

---

## Recommended Next Step

Phase 0 is complete. Proceed to **Phase 1 (Data)**:

1. Download PhishTank and Tranco datasets
2. Apply label normalization and deduplication
3. Create domain-level splits
4. Document statistics in [08-data-specification.md](08-data-specification.md)
5. Do **not** start frontend or API implementation until dataset spec is finalized
