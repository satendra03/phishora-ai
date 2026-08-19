# Phishora AI — Single Source of Truth (SSOT)

This directory is the **Single Source of Truth** for the Phishora AI major project. All implementation decisions must be traceable to documents here.

## SSOT Baseline Approval

| Field | Value |
|---|---|
| **Version** | 1.0.0 |
| **Status** | Approved as project baseline |
| **Approved date** | 2026-08-18 |
| **Scope** | Planning and requirements (pre-implementation) |

The master plan has been reviewed and approved as the SSOT baseline. Implementation must follow the requirements (what) and design decisions (how) documented here. Technology choices in [18-deployment.md](18-deployment.md) are recommendations until validated during implementation.

## Document Index

| # | Document | Contents |
|---|---|---|
| 01 | [project-overview.md](01-project-overview.md) | Executive overview, problem, goals, scope, stakeholders |
| 02 | [raw-requirements.md](02-raw-requirements.md) | Initial functional and non-functional requirements |
| 03 | [requirement-clarification.md](03-requirement-clarification.md) | Resolved ambiguities and TBD items |
| 04 | [project-constitution.md](04-project-constitution.md) | Governing principles for the project |
| 05 | [srs.md](05-srs.md) | Software Requirements Specification (consolidated) |
| 06 | [system-architecture.md](06-system-architecture.md) | Components, capabilities, data flow |
| 07 | [threat-model.md](07-threat-model.md) | STRIDE analysis, SSRF controls, safe fetch |
| 08 | [data-specification.md](08-data-specification.md) | Dataset strategy, splits, label normalization |
| 09 | [feature-specification.md](09-feature-specification.md) | Feature taxonomy (25–35 features) |
| 10 | [ml-specification.md](10-ml-specification.md) | ML problem, experiments, metrics |
| 11 | [external-intelligence.md](11-external-intelligence.md) | TI provider evaluation and abstraction |
| 12 | [risk-engine.md](12-risk-engine.md) | Evidence fusion, risk vs confidence |
| 13 | [explainability.md](13-explainability.md) | System evidence vs model explanation |
| 14 | [api-contract.md](14-api-contract.md) | Backend API endpoints and schemas |
| 15 | [ui-ux.md](15-ui-ux.md) | User interface and UX states |
| 16 | [testing-strategy.md](16-testing-strategy.md) | Software, ML, and security testing |
| 17 | [evaluation-methodology.md](17-evaluation-methodology.md) | Research questions and experiments |
| 18 | [deployment.md](18-deployment.md) | Technology evaluation and deployment |
| 19 | [development-roadmap.md](19-development-roadmap.md) | Phased roadmap, risks, definition of done |
| 20 | [decision-log.md](20-decision-log.md) | Decision record with alternatives and rationale |

## Cross-Reference Conventions

- Requirements use IDs: `FR-XX` (functional), `NFR-XX` (non-functional), `RC-XX` (clarifications), `OQ-XX` (open questions)
- Decisions use IDs: `DEC-XXX`
- Experiments use IDs: `A` through `F`
- Research questions use IDs: `RQ1` through `RQ8`

## Change Control

1. Propose change in [decision-log.md](20-decision-log.md) with alternatives and rationale
2. Update affected SSOT documents
3. Do not begin implementation of changed behavior until SSOT is updated
