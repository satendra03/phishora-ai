# 01 — Project Overview

> **Related:** [02-raw-requirements.md](02-raw-requirements.md) · [04-project-constitution.md](04-project-constitution.md) · [19-development-roadmap.md](19-development-roadmap.md)

This document is the proposed **Single Source of Truth** entry point for Phishora AI. It separates **requirements (what)** from **design decisions (how)** and defers **implementation details (code)** until after approval.

---

## Executive Summary

| Field | Definition |
|---|---|
| **Project name** | Phishora AI |
| **One-line description** | An explainable, multi-evidence website risk assessment system that investigates URLs and related domain/website signals to produce a justified Safe / Suspicious / Phishing assessment. |
| **Problem** | Users cannot reliably judge whether a link is a phishing attempt; URL-only heuristics and single API lookups are brittle, opaque, and often disagree. |
| **Proposed solution** | A tiered analysis pipeline combining lexical URL analysis, domain/network intelligence, controlled website inspection, ML on engineered features, and external threat intelligence — aggregated through a transparent risk engine with separate confidence scoring. |
| **Expected outcome** | A working web application plus documented experiments demonstrating which evidence layers improve detection, with explainable outputs suitable for both non-technical and technical users. |

**Critical review of the initial idea:** The concept is sound and academically strong *if* it avoids becoming "call 5 APIs and average scores." The differentiator must be: (1) engineered multi-layer evidence, (2) controlled experimentation proving each layer's value, (3) explainability that distinguishes ML contributions from factual evidence, and (4) safe, tiered website investigation.

---

## Problem Definition

### What problem Phishora AI solves

Users receive links via email, SMS, social media, or ads and must decide whether to click, enter credentials, or report the link. Phishora helps them make an **informed risk decision** — not a guarantee of safety.

### Why phishing detection is difficult

- **Adversarial evolution:** Attackers rotate domains, mimic brands, abuse legitimate infrastructure, and use redirects.
- **Short-lived campaigns:** Phishing URLs may exist for hours; reputation lag is real.
- **Look-alike legitimacy:** New but legitimate sites can appear suspicious; old domains can be compromised.
- **Label ambiguity:** "Suspicious" is not binary; context matters (login form on unknown domain vs. blog page).
- **Evidence cost vs. speed:** Deep inspection is slow, risky, and quota-limited.

### Why URL-only detection is insufficient

URL lexical features catch many typosquats and obfuscation patterns but miss:

- Compromised legitimate domains
- Phishing on aged domains
- Content-only impersonation (copied login pages on benign-looking URLs)
- Redirect chains that hide the final destination

URL-only remains valuable as a **fast baseline**, not the final answer.

### Why domain/website-level investigation adds evidence

- **Domain age / registration patterns** expose newly registered impersonation domains.
- **TLS/certificate anomalies** can indicate impersonation (not safety — HTTPS ≠ legitimate).
- **HTML structure** reveals credential harvesting forms, hidden fields, brand impersonation in titles/content.
- **Redirect behavior** exposes cloaking and destination mismatch.
- **External TI** provides community-verified signals for known campaigns.

### How Phishora differs from "just use VirusTotal"

| Aspect | API-only approach | Phishora AI |
|---|---|---|
| Decision basis | Opaque vendor score | Multi-source evidence + ML + explicit rules |
| Unknown URLs | Often "unknown" | Engineered feature analysis still runs |
| Explainability | Vendor-dependent | Structured evidence report + ML contributions |
| Research value | Low | Experiments per evidence layer |
| Offline/limit mode | Fails when APIs fail | Graceful degradation |

### Terminology boundaries (do not conflate)

| Term | Meaning for Phishora |
|---|---|
| **Phishing detection** | Detecting deceptive sites intended to steal credentials, payment data, or sensitive info via impersonation. **Core scope.** |
| **Suspicious website detection** | Broader weak signals without confirmed phishing intent. **Output tier (Suspicious), not a separate product goal.** |
| **Malicious website detection** | Includes malware delivery, exploit kits, drive-by downloads. **Partially out of scope** unless encountered during inspection. |
| **Malware detection** | Binary/host analysis. **Out of scope.** |
| **Scam detection** | Fraud, fake shops, advance-fee scams without classic credential phishing. **Out of scope for v1.** |
| **Reputation checking** | Lookup in blocklists/reputation feeds. **One evidence input, not the whole system.** |

### What the system should NOT claim

- It does **not** guarantee a site is safe.
- It does **not** detect all malware or scams.
- It does **not** replace enterprise email/web security gateways.
- It does **not** perform active exploitation or credential submission testing.

---

## Goals and Objectives

### Main objectives

1. Accept a URL and produce a **3-tier classification**: Safe, Suspicious, Phishing.
2. Produce a **risk score (0–100)** and a **separate confidence score (0–100)**.
3. Gather and present **explainable evidence** from multiple independent layers.
4. Implement **tiered analysis**: fast scan first, conditional deep investigation.
5. Train and evaluate ML models with a **scientifically defensible dataset protocol**.
6. Demonstrate through experiments **which layers improve detection**.

### Secondary objectives

- Optional deep-scan mode (user opt-in).
- Technical evidence panel for security-aware users.
- Analysis history (minimal metadata, privacy-conscious).
- Exportable analysis report (PDF/JSON — optional).

### Success criteria (qualitative until experiments run)

- System completes a standard scan within acceptable latency (TBD after prototyping).
- Experiments A→F show measurable layer contributions (or document when they do not).
- Security test suite passes for SSRF, redirect abuse, and resource exhaustion cases.
- UI communicates uncertainty and limitations clearly.

---

## Scope and Boundaries

### In scope (v1)

- URL validation and normalization
- Lexical/structural URL feature extraction
- Domain age, DNS, WHOIS (where obtainable), TLS/certificate inspection
- Controlled HTTP fetch with redirect tracking (no JS execution in core path)
- Static HTML analysis (forms, titles, keywords, external resources)
- ML classifiers on engineered tabular features
- External TI integration (limited, justified providers)
- Evidence aggregation and explainability
- Web UI with simple + technical views
- Evaluation on public datasets with domain/time-aware splits

### Out of scope (v1)

- Email header analysis, attachment scanning
- Browser extension / mobile app
- Real-time network traffic inspection
- Malware binary analysis
- Full headless browser automation for all requests (optional advanced module only)
- CNN/visual phishing detection on screenshots (future work)
- Automated takedown or reporting to registrars
- Multi-tenant enterprise admin, SSO, RBAC

### Classification: Core / Recommended / Optional / Future

| Capability | Tier |
|---|---|
| URL + domain + TLS + static HTML analysis | **Core** |
| Tiered quick/deep scan | **Core** |
| ML tabular models + experiments | **Core** |
| External TI (2–3 providers) | **Recommended** |
| Screenshot capture | **Optional** |
| Visual ML / brand logo matching | **Future Work** |
| Headless JS rendering (Playwright) | **Optional** (deep scan only, sandboxed) |

---

## Stakeholders and Users

### Primary users (confirmed: mixed audience)

| User type | Needs |
|---|---|
| **General user** | Simple verdict, plain-language explanation, clear warnings |
| **Technical user** | Evidence breakdown, DNS/TLS details, ML feature contributions, TI raw results |
| **Evaluator (faculty/jury)** | Architecture depth, experiments, reproducibility, security awareness |

### Stakeholders

- Project developer(s)
- Academic supervisor
- End users (demo participants)

### Key use cases

1. **UC-01 Quick check:** User pastes a suspicious link → receives verdict + top reasons in <10s (target TBD).
2. **UC-02 Deep investigation:** User opts into deep scan when quick scan is inconclusive.
3. **UC-03 Technical review:** User expands evidence panel to inspect DNS, TLS, forms, TI results.
4. **UC-04 Partial failure:** One TI provider is down → system still returns result with reduced confidence.
5. **UC-05 Unreachable site:** Domain does not resolve → system reports analysis limits, uses URL/domain-only evidence.

---

## Critical Summary

Phishora AI is **viable and strong** for a major project if it emphasizes:

- Tiered, security-conscious investigation (not blind crawling)
- Experiment-driven justification for each layer
- Evidence fusion instead of API averaging
- Honest 3-class output with separate confidence
- Dual-audience explainability

The biggest risks to avoid are: unsafe fetching, dataset leakage, over-reliance on TI APIs, and scope creep into visual ML or malware analysis.
