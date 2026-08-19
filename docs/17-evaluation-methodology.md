# 17 — Evaluation Methodology

> **Related:** [08-data-specification.md](08-data-specification.md) · [10-ml-specification.md](10-ml-specification.md) · [16-testing-strategy.md](16-testing-strategy.md)

Research questions, experiment design, and deliverables for academic evaluation.

---

## Research Questions

| ID | Question | Experiment | Metric |
|---|---|---|---|
| RQ1 | How effective is URL-only detection alone? | A | F1, PR-AUC on domain-holdout |
| RQ2 | How much do domain features improve performance? | B vs A | Δ F1, Δ PR-AUC |
| RQ3 | How much does static HTML analysis add? | D vs C | Δ F1 on fetch-success subset |
| RQ4 | What is the marginal value of external TI? | E vs D | Δ F1, false positive rate |
| RQ5 | Does evidence fusion reduce false positives vs any single source? | F vs best single source | FP count on Tranco sample |
| RQ6 | Which features contribute most? | Ablation + SHAP | Feature importance ranking |
| RQ7 | Generalization to unseen domains? | Domain-holdout test | F1 on domain-holdout vs random split |
| RQ8 | Performance on recent phishing vs training-era data? | Temporal test set | Recall on temporal hold-out |

---

## Experiment Design

### Controlled variables

- Same domain-holdout test set across experiments A–E
- Same random seed for reproducibility
- Same hyperparameter tuning protocol (validation set only)
- Same class weighting strategy

### Independent variables

- Feature tier (URL → domain → TLS → HTML → TI)
- Model type (Logistic Regression vs LightGBM)
- Risk engine vs model-only decision

### Dependent variables

- F1 (macro), PR-AUC, false positive rate, false negative rate
- Calibration (Brier score)
- End-to-end latency (quick vs deep scan)

---

## Experiment Report Structure

Each experiment produces a report section:

```markdown
## Experiment {Letter}: {Title}

### Hypothesis
{What we expect to happen}

### Setup
- Features: {list}
- Model: {type}
- Train/val/test sizes: {counts}
- Class balance: {ratio}

### Results
| Metric | Value |
|--------|-------|
| F1 (macro) | TBD |
| PR-AUC | TBD |
| FP rate (Tranco) | TBD |

### Comparison to Previous
| Metric | Exp {N-1} | Exp {N} | Δ |
|--------|-----------|---------|---|

### Conclusion
{Did the added layer justify its cost/complexity?}
```

**Do not fabricate results.** All metric cells marked TBD until experiments run.

---

## Ablation Study (RQ6)

For the final model (Experiment E or F):

1. Train full model with all features
2. For each feature group (URL, domain, TLS, HTML, TI):
   - Remove group entirely
   - Retrain and evaluate on same test set
   - Record Δ F1
3. For top 10 individual features (by SHAP):
   - Remove one at a time
   - Record Δ F1

Present as table and bar chart in final report.

---

## Domain Generalization Study (RQ7)

Compare two split strategies on the same data:

| Split Strategy | Description | Expected Outcome |
|---|---|---|
| Random URL split | Standard random 80/20 | Optimistic metrics |
| Domain-holdout split | No domain overlap between train/test | Realistic metrics |
| Temporal split | Train on older, test on recent | Measures concept drift |

Report metrics for all three to demonstrate why domain-holdout is used.

---

## Temporal Evaluation (RQ8)

- Collect phishing URLs from last 3–6 months (PhishTank, OpenPhish)
- Ensure zero domain overlap with training set
- Measure recall specifically (phishing detection rate on new campaigns)
- Compare to recall on training-era test set

---

## End-to-End System Evaluation (Experiment F)

Beyond ML metrics, evaluate the full pipeline:

| Aspect | Method |
|---|---|
| Verdict accuracy | Compare system verdict to ground truth on evaluation set |
| Explainability quality | Manual review: do top 3 reasons match ground truth? |
| Latency | Measure p50, p95 for quick and deep scans |
| Graceful degradation | Disable each TI provider; verify partial results |
| Security | Run SSRF test suite; verify all blocked |

---

## Deliverables

| Deliverable | Format | Location |
|---|---|---|
| Experiment results tables | Markdown + CSV | `docs/17-evaluation-methodology.md` (results section) |
| Confusion matrices | PNG/SVG plots | `reports/figures/` |
| Calibration plots | PNG/SVG | `reports/figures/` |
| SHAP summary plot | PNG/SVG | `reports/figures/` |
| Ablation table | Markdown | Final report |
| Demo script | Markdown | `docs/demo-script.md` |
| Decision log updates | Markdown | [20-decision-log.md](20-decision-log.md) |

---

## Demo Script (Outline)

Live demonstration using held-out examples:

1. **Safe site** (Tranco top site) → Safe verdict, high confidence, mitigating factors
2. **Known phishing** (recent PhishTank) → Phishing verdict, TI evidence highlighted
3. **Borderline** (new domain with login form) → Suspicious, low-medium confidence, conflict shown
4. **Unreachable site** → Partial analysis, limitations banner
5. **Technical view** → Expand evidence panel, show SHAP chart

Prepare 5–7 URLs in advance; verify they produce expected behavior before demo.

---

## Statistical Significance

For comparing experiments:

- Use McNemar's test for paired classification comparisons
- Report confidence intervals on F1 (bootstrap, 1000 iterations)
- Mark improvements as significant only if p < 0.05

---

## Results Section (To Be Completed)

> This section will be populated after experiments A–F are executed.

### Experiment A Results

TBD

### Experiment B Results

TBD

### Experiment C Results

TBD

### Experiment D Results

TBD

### Experiment E Results

TBD

### Experiment F Results

TBD

### Summary Comparison

TBD
