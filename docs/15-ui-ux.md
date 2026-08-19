# 15 — UI/UX Plan

> **Related:** [13-explainability.md](13-explainability.md) · [14-api-contract.md](14-api-contract.md) · [01-project-overview.md](01-project-overview.md)

User experience design for mixed-audience (general + technical) users.

---

## Design Principles

1. **Honesty first:** Always show limitations and low-confidence warnings prominently.
2. **Progressive disclosure:** Simple verdict default; technical detail on demand.
3. **Actionable guidance:** Tell users what to do (avoid entering credentials, try deep scan).
4. **No false certainty:** Suspicious is a valid outcome; do not force binary safe/unsafe.

---

## Page Structure

```
┌─────────────────────────────────────────────────┐
│  Phishora AI                          [About]   │
├─────────────────────────────────────────────────┤
│  [ URL input field                    ] [Analyze] │
│  [ ] Deep Scan (slower, more thorough)          │
├─────────────────────────────────────────────────┤
│  ┌─ Verdict Badge ──────────────────────────┐   │
│  │  SUSPICIOUS          Risk: 58  Conf: 62% │   │
│  └──────────────────────────────────────────┘   │
│  Summary text (2-3 sentences)                     │
│  • Top reason 1                                   │
│  • Top reason 2                                   │
│  • Top reason 3                                   │
│  [ Show Technical Details ▼ ]                     │
├─────────────────────────────────────────────────┤
│  (Technical panel — collapsed by default)         │
│  [URL|Domain|TLS|HTML|TI|ML] tabs                 │
└─────────────────────────────────────────────────┘
```

---

## Simple View (Default)

| Element | Description |
|---|---|
| URL input | Single-line text field with paste support |
| Analyze button | Primary action; disabled during analysis |
| Deep Scan toggle | Checkbox; tooltip explains slower but more thorough |
| Verdict badge | Large color-coded: Green (Safe), Amber (Suspicious), Red (Phishing) |
| Risk meter | Horizontal bar 0–100 with numeric label |
| Confidence indicator | Separate meter or badge; low confidence triggers warning banner |
| Summary | Plain-language 2–3 sentence explanation |
| Top reasons | 3–5 bullet points from `top_risk_factors` |
| Limitations banner | Amber banner when `partial_analysis` or confidence < 50 |

---

## Technical View (Expandable Panel)

Triggered by "Show Technical Details" accordion.

### Tabs

| Tab | Contents |
|---|---|
| **URL** | Lexical features, entropy, keyword matches, punycode detection |
| **Domain** | Age, registrar, DNS records, Tranco rank, WHOIS privacy |
| **TLS** | Certificate validity, issuer, domain match, expiry |
| **HTML** | Form analysis, password fields, iframes, external scripts, title |
| **Threat Intel** | Provider cards with verdict, timestamp, raw response |
| **ML** | Model probability, SHAP chart, feature importances |

### Additional elements

- Redirect chain visualization (step diagram)
- Optional screenshot thumbnail (deep scan)
- Conflicts section (amber highlight)
- Raw JSON export button
- Copy analysis ID button

---

## UI States

| State | Visual Treatment | User Action |
|---|---|---|
| **Idle** | Empty input, Analyze enabled | Enter URL |
| **Validating** | Input border check, brief spinner | Wait |
| **Analyzing (quick)** | Progress indicator, "Analyzing URL..." | Wait (<8s) |
| **Analyzing (deep)** | Progress stages shown, "Deep scan in progress..." | Wait or poll |
| **Invalid URL** | Red inline error below input | Fix URL |
| **Safe** | Green badge, mitigating factors shown | None required |
| **Suspicious** | Amber badge, "Exercise caution" message | Consider deep scan |
| **Phishing** | Red badge, "Do not enter credentials" warning | Do not visit |
| **API failure** | Partial result with unavailable sources listed | Retry later |
| **Website unreachable** | Verdict with limitations banner | Result based on URL/domain only |
| **Analysis timeout** | Partial result, completed phases listed | Retry or accept partial |
| **Partial analysis** | Confidence reduced, banner explains gaps | Optional deep scan retry |
| **Rate limit** | Friendly message with retry countdown | Wait and retry |
| **Insufficient evidence** | "Inconclusive" styling, low confidence | Recommend deep scan |

---

## Accessibility

- Color is not the only indicator (icons + text labels for verdicts)
- Sufficient contrast ratios for badge colors
- Keyboard navigation for tabs and accordion
- Screen reader labels for risk/confidence meters

---

## Responsive Design

- Mobile: stacked layout, technical panel as full-screen drawer
- Desktop: side-by-side input and results
- Minimum supported width: 320px

---

## Copy Guidelines

| Verdict | Recommended Copy |
|---|---|
| Safe | "No significant phishing indicators were detected." |
| Suspicious | "This website shows some warning signs. Proceed with caution." |
| Phishing | "This website is likely a phishing attempt. Do not enter personal information." |
| Low confidence | "Our confidence in this assessment is limited. Consider running a deep scan." |
| Partial | "Some analysis steps could not be completed. Results may be incomplete." |

Avoid: "This site is 100% safe" or "Guaranteed clean."

---

## Optional Features (v1 stretch)

- Analysis history (last 5 scans, session-only)
- Share link for analysis result (analysis ID in URL)
- Export report as JSON download
