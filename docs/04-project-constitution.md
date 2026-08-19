# 04 — Project Constitution

> **Related:** [01-project-overview.md](01-project-overview.md) · [20-decision-log.md](20-decision-log.md)

Formal rules governing Phishora AI throughout development.

---

## Principles

1. **Scope Principle:** Phishora assesses website phishing risk; it is not a full security platform.

2. **Evidence Principle:** Decisions use multiple independent signals where feasible; no single signal is absolute.

3. **Explainability Principle:** Verdicts include understandable reasons; distinguish facts from model inference.

4. **Security Principle:** User-submitted URLs are untrusted input; SSRF protections are mandatory.

5. **Privacy Principle:** Collect and retain minimum data necessary; prefer hashes over raw URLs in logs.

6. **Reliability Principle:** Provider failure degrades gracefully; partial analysis is valid output.

7. **Scientific Evaluation Principle:** Performance claims require measured experiments on documented splits.

8. **Reproducibility Principle:** Datasets, features, models, and splits are versioned and documented.

9. **Architecture Principle:** Feature extractors, TI providers, and scorers are replaceable modules.

10. **Honesty Principle:** UI displays limitations, low-confidence warnings, and unreachable-site caveats.

11. **No Safety Theater Principle:** HTTPS, professional design, or domain age alone never imply Safe.

12. **Tiered Analysis Principle:** Expensive/risky operations run only when justified.

---

## Enforcement

- Any change that violates these principles requires a [decision-log](20-decision-log.md) entry with explicit rationale.
- Code reviews (self or peer) should verify alignment before merging implementation work.
