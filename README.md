# Phishora AI

An explainable, multi-evidence website risk assessment system that investigates URLs and related domain/website signals to produce a justified **Safe / Suspicious / Phishing** assessment.

## Documentation (Single Source of Truth)

All project requirements, architecture, and design decisions are maintained in the [`docs/`](docs/) directory.

| Document | Description |
|---|---|
| [docs/README.md](docs/README.md) | SSOT index and baseline approval |
| [docs/01-project-overview.md](docs/01-project-overview.md) | Executive overview, problem definition, scope |
| [docs/20-decision-log.md](docs/20-decision-log.md) | Record of major architectural decisions |

**Status:** Planning phase complete. Implementation follows SSOT documents.

## Project Principles

- Tiered, security-conscious website investigation
- Experiment-driven justification for each evidence layer
- Evidence fusion (not naive API score averaging)
- Separate risk score and confidence score
- Dual-audience explainability (simple + technical views)

## Next Steps

See [docs/19-development-roadmap.md](docs/19-development-roadmap.md) — Phase 1 (Data) begins after SSOT approval.
