# 12 — Risk Engine

> **Related:** [11-external-intelligence.md](11-external-intelligence.md) · [13-explainability.md](13-explainability.md) · [10-ml-specification.md](10-ml-specification.md)

Evidence-based fusion for risk scoring and confidence calculation.

---

## Design Rationale

### Reject naive score averaging

Simple `40% ML + 60% APIs` is **not scientifically justified** because:

- Sources have different reliability, coverage, and correlation.
- Missing data breaks fixed weights.
- APIs are not calibrated probabilities.

---

## Evidence Model

Each evidence item `e_i` produces:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique evidence identifier |
| `layer` | enum | url, domain, tls, html, threat_intel, model |
| `type` | enum | evidence, model |
| `label` | string | Human-readable description |
| `risk_contribution` | float ∈ [-1, +1] | Negative = reduces risk; positive = increases risk |
| `weight` | float | base_reliability × availability × source_confidence |
| `raw_value` | any | Original signal value for technical view |

---

## Risk Score Calculation

```
risk_raw = sum(w_i * r_i) / sum(w_i)    # where w_i > 0
risk_score = scale_to_0_100(risk_raw)   # map [-1, +1] → [0, 100]
```

Where `scale_to_0_100(x) = (x + 1) * 50`

### Classification thresholds (initial — tune on validation)

| Label | Risk Score Range |
|---|---|
| Safe | < 35 |
| Suspicious | 35 ≤ score < 65 |
| Phishing | ≥ 65 |

Thresholds must be validated against confusion matrix on validation set. Do not use arbitrary values in final report without tuning evidence.

---

## Confidence Score Calculation

Confidence is **independent** of risk magnitude.

### Factors

| Factor | Weight | Description |
|---|---|---|
| **Completeness** | 0.30 | Percentage of expected evidence items available |
| **Agreement** | 0.30 | Degree of consensus among independent layers |
| **Calibration** | 0.20 | Model calibration quality on validation set |
| **Recency** | 0.10 | Freshness of TI and domain data |
| **Tier depth** | 0.10 | Whether deep scan was performed |

```
confidence = 100 * (
    0.30 * completeness +
    0.30 * agreement +
    0.20 * calibration +
    0.10 * recency +
    0.10 * tier_depth
)
```

### Agreement calculation

- For each pair of independent layers with risk direction (positive/negative/neutral), compute agreement
- Conflicting signals (e.g., TI says safe, HTML shows password form on mismatched domain) reduce agreement sharply
- Flag conflicts in explainability output

---

## Evidence Normalization Examples

| Signal | Raw Value | risk_contribution | weight |
|---|---|---|---|
| Domain age 2 days | 2 | +0.7 | 0.75 |
| In Tranco top-1M | true | -0.5 | 0.60 |
| PhishTank verified | true | +0.9 | 0.90 |
| Has password field | true | +0.6 | 0.80 |
| ML P(phishing) = 0.72 | 0.72 | +0.44 | 0.85 |
| Valid HTTPS | true | 0.0 | 0.0 (no auto-reduction) |
| Safe Browsing clean | true | -0.3 | 0.85 |

**Rule:** HTTPS availability contributes **zero** weight by default (No Safety Theater Principle).

---

## Conflict Handling

When conflicting evidence detected:

1. Flag `conflicting_evidence: true` in output
2. List conflicting items in `conflicts` array
3. Increase risk toward Suspicious/Phishing if content evidence conflicts with TI clean result
4. Decrease confidence proportionally to conflict severity
5. Never silently resolve conflicts — always surface to user

### Example conflict

```json
{
  "conflicts": [
    {
      "description": "PhishTank reports clean but page contains password form on unrelated domain",
      "items": ["phishtank_clean", "has_password_field", "form_action_external"],
      "resolution": "Content evidence weighted higher for credential phishing assessment"
    }
  ]
}
```

---

## Missing Data Handling

| Scenario | Behaviour |
|---|---|
| WHOIS unavailable | Skip domain age evidence; reduce completeness |
| Website unreachable | Skip HTML/TLS fetch evidence; quick-scan evidence only |
| TI provider down | Redistribute weight among available providers |
| All deep-scan evidence missing | Return quick-scan result with low confidence and `partial_analysis: true` |

Weights are redistributed proportionally among available items in the same layer. Cross-layer weights are not redistributed.

---

## ML Integration

ML probability feeds as one evidence item:

```
risk_contribution_ml = 2 * P(phishing) - 1   # maps [0,1] to [-1,+1]
weight_ml = model_reliability * feature_completeness_at_tier
```

Model reliability = validation F1 on the feature tier available at inference time.

---

## Tier Escalation Logic

```
IF deep_scan_requested:
    RUN deep scan
ELIF risk_score in [35, 65]:
    RUN deep scan (automatic escalation)
ELSE:
    SKIP deep scan; use quick-scan evidence only
```

Uncertain band thresholds (OQ-01) to be tuned after Experiment A baseline results.

---

## Output Schema

```json
{
  "verdict": "Suspicious",
  "risk_score": 58,
  "confidence": 62,
  "risk_breakdown": {
    "url_layer": 0.35,
    "domain_layer": 0.55,
    "tls_layer": null,
    "html_layer": 0.70,
    "threat_intel_layer": 0.20,
    "model_layer": 0.60
  },
  "confidence_breakdown": {
    "completeness": 0.72,
    "agreement": 0.55,
    "calibration": 0.80,
    "recency": 0.90,
    "tier_depth": 0.50
  },
  "partial_analysis": false,
  "conflicting_evidence": true
}
```
