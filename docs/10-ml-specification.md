# 10 — ML Specification

> **Related:** [08-data-specification.md](08-data-specification.md) · [09-feature-specification.md](09-feature-specification.md) · [17-evaluation-methodology.md](17-evaluation-methodology.md)

Machine learning problem definition, model selection, and experimental progression.

---

## ML Problem Definition

| Aspect | Definition |
|---|---|
| **Predict** | P(phishing \| available features at scan tier) |
| **Training label** | Binary `{legitimate, phishing}` from curated datasets |
| **Inference mapping** | Probability + rules → {Safe, Suspicious, Phishing} |
| **Unit of analysis** | URL (domain-level grouping for evaluation splits) |

---

## Model Candidates

| Model | Pros | Cons | Fit |
|---|---|---|---|
| Logistic Regression | Interpretable baseline | Linear | Experiment A baseline |
| Random Forest | Strong tabular, feature importances | Less calibrated | Good default |
| XGBoost/LightGBM | High performance on tabular | Tuning needed | Recommended primary |
| Neural nets on raw URL chars | Research appeal | Needs more data, harder to explain | Optional stretch |

**Recommendation:** Logistic Regression (baseline) → LightGBM (primary) → compare.

---

## Experimental Progression

| Experiment | Features | Question Answered |
|---|---|---|
| **A** | URL-only (~15 features) | Baseline effectiveness |
| **B** | A + domain/DNS | Value of domain intelligence |
| **C** | B + TLS/redirect | Value of network inspection |
| **D** | C + HTML features | Value of content analysis |
| **E** | D + TI features | Value of external intelligence |
| **F** | Full pipeline + risk engine | End-to-end system vs model-only |

Each experiment must use the same domain-holdout test set. Report metrics on both domain-holdout and temporal hold-out sets.

---

## Metrics

### Classification metrics

- Accuracy, Precision, Recall, F1 (per class and macro)
- ROC-AUC, PR-AUC (important for class imbalance)
- Confusion matrix on domain-holdout and temporal test

### Calibration

- Reliability diagrams (predicted probability vs observed frequency)
- Brier score
- Platt scaling or isotonic regression applied on validation set if needed

### Error analysis

- False positive analysis on Tranco sample (legitimate sites flagged as phishing)
- False negative analysis on recent PhishTank samples
- Per-feature ablation to identify redundant features

**Do not report fabricated numbers before running experiments.**

---

## Training Protocol

1. **Split:** Domain-level 60/20/20 train/val/test (see [08-data-specification.md](08-data-specification.md))
2. **Feature parity:** Training features must match inference-time availability per tier
3. **Class imbalance:** Use class weights or SMOTE on training only; evaluate with PR-AUC
4. **Hyperparameter tuning:** On validation set only; never tune on test
5. **Model versioning:** `{model_name}_v{version}_exp{letter}_date`

---

## Explainability for ML

| Method | Scope | When Used |
|---|---|---|
| Feature importances (LightGBM) | Global model behavior | Always in technical view |
| SHAP values | Per-prediction contributions | Validation sample + inference |
| Logistic coefficients | Baseline interpretability | Experiment A only |

**Scope rule:** Explain ML contribution only; do not SHAP-explain API/TI results (those are system evidence).

---

## Inference Integration

ML output feeds the risk engine as one evidence item:

```json
{
  "type": "model",
  "source": "lightgbm_v1_expD",
  "probability_phishing": 0.72,
  "reliability_weight": 0.85,
  "top_features": [
    {"name": "domain_age_days", "shap_value": -0.31},
    {"name": "has_password_field", "shap_value": 0.28}
  ]
}
```

Reliability weight derived from validation-set F1 on the feature tier used at inference time.

---

## Artifacts to Produce

| Artifact | Location (planned) |
|---|---|
| Trained models | `models/` |
| Experiment notebooks | `notebooks/experiments/` |
| Metrics tables | `docs/17-evaluation-methodology.md` (results section) |
| Feature importance plots | Included in final report |
