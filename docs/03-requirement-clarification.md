# 03 — Requirement Clarification

> **Related:** [02-raw-requirements.md](02-raw-requirements.md) · [20-decision-log.md](20-decision-log.md)

Critical ambiguities resolved or marked TBD. Each entry follows: question → why it matters → choices → decision → reasoning.

---

## RC-01: Should every submitted website be visited?

- **Why it matters:** Active fetching introduces SSRF risk, latency, and malicious content exposure.
- **Choices:** (A) Always visit, (B) Never visit, (C) Tiered visit.
- **Decision:** **(C) Tiered** — quick scan uses URL + passive domain/TLS lookup; HTTP fetch only in deep phase or when quick score is in uncertain band (e.g., 35–65).
- **Reasoning:** Balances safety, speed, and academic depth.

---

## RC-02: JavaScript-heavy websites?

- **Decision:** Core path uses **static HTTP fetch only**. Optional deep mode may use sandboxed headless browser — **Optional**, not core.
- **Reason:** Full JS rendering is expensive, risky, and hard to evaluate fairly in a student timeline.

---

## RC-03: Screenshots?

- **Decision:** **Optional module.** Capture only in deep scan, store temporarily, display in technical panel.
- **Reason:** Useful for demo/explainability; visual ML is future work.

---

## RC-04: What does risk score 80 mean?

- **Decision:** Risk score is a **normalized 0–100 index** representing estimated phishing/malicious-web risk based on weighted evidence. It is **not** a probability percentage unless calibrated and documented as such.
- **Calibration:** Platt scaling or isotonic regression on validation set — **TBD in ML phase**.

---

## RC-05: Is confidence the same as risk?

- **Decision:** **No.** Confidence measures certainty based on evidence quantity, source agreement, and model calibration — independent of risk magnitude.
- **Example:** High risk + low confidence = "looks bad but we lack corroboration"; low risk + low confidence = "probably fine but insufficient evidence."

---

## RC-06: Classification categories?

- **Decision:** **3-class output:** Safe, Suspicious, Phishing.
- **Reason:** Binary forces borderline cases into false certainty; Suspicious communicates uncertainty honestly.

---

## RC-07: Conflicting API results?

- **Decision:** No majority-vote. Use **reliability-weighted evidence fusion** with conflict flagging in explainability output.
- **Reason:** APIs have different coverage, lag, and error profiles; voting hides nuance.

---

## RC-08: Data retention?

- **Decision:** Store analysis ID, URL hash (optional), verdict, scores, evidence summary, timestamps. **Do not** persist full HTML by default. Configurable retention window (e.g., 7 days) — TBD.

---

## RC-09: Acceptable analysis time?

- **Decision:** Quick scan target **≤ 8s p95**; deep scan target **≤ 45s p95** — refine after prototyping (TBD).

---

## RC-10: WHOIS unavailable?

- **Decision:** Mark feature as missing; reduce confidence; continue analysis with other signals.

---

## RC-11: Login form detection?

- **Decision:** Detect `<form>` with `type=password` or `name` patterns (password, passwd, pwd), hidden fields, external form actions — static HTML heuristics.

---

## RC-12: How to safely analyze malicious sites?

- **Decision:** Isolated fetch worker, no JS exec (core), no file downloads executed, no credential submission, response size caps, content-type validation, sandbox network egress allowlist.

---

## Open Questions (Unresolved)

See [19-development-roadmap.md](19-development-roadmap.md#open-questions--decisions-required) for OQ-01 through OQ-08.
