# 13 — Explainability

> **Related:** [12-risk-engine.md](12-risk-engine.md) · [10-ml-specification.md](10-ml-specification.md) · [15-ui-ux.md](15-ui-ux.md)

Explainability layer design distinguishing system evidence from model inference.

---

## Two Explanation Types

| Type | Source | Example | Display Location |
|---|---|---|---|
| **System evidence** | Factual observations from analysis | "Domain registered 2 days ago" | Evidence tabs |
| **Model explanation** | ML inference on engineered features | "High subdomain count increased model score" | ML tab + SHAP chart |

**Critical distinction:** An external security database result is **system evidence**, not a SHAP feature contribution.

---

## Explanation Output Structure

```json
{
  "verdict": "Suspicious",
  "risk_score": 58,
  "confidence": 62,
  "summary": "This website shows several warning signs including a recently registered domain and a login form pointing to an external server. Threat intelligence did not flag it, so confidence is moderate.",
  "top_risk_factors": [
    {
      "type": "evidence",
      "layer": "domain",
      "label": "Domain registered 2 days ago",
      "impact": "high",
      "risk_contribution": 0.7
    },
    {
      "type": "evidence",
      "layer": "html",
      "label": "Password input field with form submitting to external domain",
      "impact": "high",
      "risk_contribution": 0.6
    },
    {
      "type": "model",
      "layer": "model",
      "label": "ML model assigns 72% phishing probability",
      "impact": "medium",
      "risk_contribution": 0.44
    }
  ],
  "mitigating_factors": [
    {
      "type": "evidence",
      "layer": "domain",
      "label": "Domain uses valid HTTPS with matching certificate",
      "impact": "low",
      "risk_contribution": 0.0
    },
    {
      "type": "evidence",
      "layer": "threat_intel",
      "label": "Not found in PhishTank or Safe Browsing databases",
      "impact": "medium",
      "risk_contribution": -0.3
    }
  ],
  "conflicts": [
    {
      "description": "Clean threat intelligence but suspicious page content detected",
      "items": ["phishtank_clean", "has_password_field"]
    }
  ],
  "evidence_by_layer": {
    "url": [],
    "domain": [],
    "tls": [],
    "html": [],
    "threat_intel": [],
    "model": []
  },
  "limitations": [
    "Website content analysis based on static HTML only; JavaScript-rendered content not evaluated"
  ]
}
```

---

## Evidence Templates (Rule-Based)

Templates map feature values to human-readable strings:

| Feature Condition | Template |
|---|---|
| `domain_age_days < 30` | "Domain was registered {domain_age_days} days ago, which is unusually recent" |
| `has_password_field == true` | "Page contains a password input field" |
| `form_action_external == true` | "Login form submits data to a different domain ({form_action_domain})" |
| `redirect_count > 2` | "URL redirects {redirect_count} times before reaching final destination" |
| `cert_domain_mismatch == true` | "SSL certificate does not match the domain name" |
| `in_tranco_top1m == true` | "Domain appears in Tranco top 1 million popular sites" |
| `phishtank_verified == true` | "Confirmed as phishing by PhishTank community verification" |
| `url_entropy > threshold` | "Domain name appears randomly generated (high entropy)" |

Templates support `{variable}` substitution from feature values.

---

## ML Explainability Methods

| Method | When Used | Output |
|---|---|---|
| LightGBM feature importances | Global model view | Bar chart of top 10 features |
| SHAP values | Per-prediction explanation | Top 5 contributing features with direction |
| Logistic coefficients | Experiment A baseline | Signed coefficient table |

### SHAP scope rules

- Compute SHAP on the feature vector used at inference time
- Only include features that were available (not imputed defaults)
- Display in ML tab of technical view
- Do not use SHAP to explain TI API results

---

## Summary Generation

v1 uses **template-based summaries**, not LLM generation (avoids hallucination):

```
IF verdict == "Phishing":
  "This website is likely a phishing attempt. {top_factor_1}. {top_factor_2}. Do not enter credentials."
ELIF verdict == "Suspicious":
  "This website shows some warning signs. {top_factor_1}. Exercise caution before entering personal information."
ELSE:
  "No significant phishing indicators detected. {mitigating_factor_1 if available}."
```

If confidence < 50, append: "However, our confidence in this assessment is limited due to {reason}."

---

## UI Presentation

### Simple View

- Plain-language summary (2–3 sentences)
- Top 3–5 risk factors as bullet points
- Mitigating factors if Safe verdict
- Limitations banner when partial/low confidence

### Technical View

- Evidence organized by layer tabs
- Raw feature values alongside templates
- SHAP waterfall or bar chart for ML
- TI provider cards with timestamps and raw responses
- Conflicts highlighted in amber
- JSON export of full explanation payload

---

## Methods Explicitly Excluded from v1

| Method | Reason |
|---|---|
| LLM-generated explanations | Hallucination risk; not reproducible |
| LIME on raw URL strings | Less stable than SHAP for tabular features |
| Attention visualization | No neural model in core path |
| Automated visual explanation | No visual ML in v1 |
