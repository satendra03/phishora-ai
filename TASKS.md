# Phishora AI - Task Tracker

## Phase 0: Planning ✅ COMPLETE
- [x] SSOT documentation structure created
- [x] Decision log initialized
- [x] Data specification drafted (docs/08-data-specification.md)
- [x] Feature specification drafted (docs/09-feature-specification.md)
- [x] Threat model documented (docs/07-threat-model.md)
- [x] Project constitution (docs/04-project-constitution.md)
- [x] SRS (docs/05-srs.md)
- [x] System architecture (docs/06-system-architecture.md)
- [x] Risk engine (docs/12-risk-engine.md)
- [x] ML specification (docs/10-ml-specification.md)
- [x] Explainability (docs/13-explainability.md)
- [x] API contract (docs/14-api-contract.md)
- [x] UI/UX (docs/15-ui-ux.md)
- [x] Development roadmap (docs/19-development-roadmap.md)

## Phase 1: Data 🔄 IN PROGRESS
- [x] **Data collection** - All 4 files provided:
  - [x] PhishTank CSV (verified entries) → `data/raw/phishtank/online-valid.csv` (13.8 MB)
  - [x] OpenPhish feed → `data/raw/openphish/feed.txt` (16 KB)
  - [x] URLhaus CSV (phishing tags) → `data/raw/urlhaus/urlhaus.csv` (3.2 MB)
  - [x] Tranco Top 1M CSV → `data/raw/tranco/top-1m.csv` (22.6 MB)
- [ ] Data processing script ready (scripts/collect_data.py)
- [ ] Run processing: normalize, deduplicate, cross-contamination check
- [ ] Create domain-level splits (60/20/20 train/val/test, seed=42)
- [ ] Create temporal hold-out set
- [ ] Document statistics in docs/08-data-specification.md

## Phase 2: URL Engine ⏳ PENDING
- [ ] URL parser and normalizer
- [ ] 15 URL features (Tier 0) implementation
- [ ] Experiment A: Logistic Regression baseline
- [ ] Document baseline metrics

## Phase 3: Domain/TLS ⏳ PENDING
- [ ] DNS, WHOIS/RDAP, Tranco lookup
- [ ] TLS certificate inspection
- [ ] Domain features (Tier 1)
- [ ] Experiments B and C

## Phase 4: Safe Fetch ⏳ PENDING
- [ ] SSRF guard module
- [ ] Isolated fetch worker
- [ ] HTML analyzer (forms, titles, scripts)
- [ ] HTML features (Tier 2)
- [ ] Experiment D

## Phase 5: ML ⏳ PENDING
- [ ] LightGBM training on full feature set
- [ ] Hyperparameter tuning
- [ ] Calibration (Platt scaling)
- [ ] SHAP analysis
- [ ] Feature ablation study

## Phase 6: Threat Intel ⏳ PENDING
- [ ] TI provider adapters
- [ ] TI features (Tier 3)
- [ ] Experiment E
- [ ] Caching layer

## Phase 7: Risk Engine ⏳ PENDING
- [ ] Evidence aggregation
- [ ] Risk score calculation
- [ ] Confidence calculation
- [ ] Conflict detection
- [ ] Validate on hold-out set

## Phase 8: Explainability ⏳ PENDING
- [ ] Evidence templates
- [ ] SHAP integration
- [ ] Summary generation
- [ ] Test explanation quality

## Phase 9: Backend API ⏳ PENDING
- [ ] FastAPI endpoints per api-contract.md
- [ ] Async deep scan with ARQ
- [ ] Rate limiting
- [ ] Integration tests

## Phase 10: Frontend ⏳ PENDING
- [ ] React UI per ui-ux.md
- [ ] All UI states
- [ ] Simple + technical views
- [ ] E2E tests

## Phase 11-15: Integration, Security, Evaluation, Deployment, Documentation ⏳ PENDING