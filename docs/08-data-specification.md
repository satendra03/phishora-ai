# 08 — Data Specification

> **Related:** [10-ml-specification.md](10-ml-specification.md) · [09-feature-specification.md](09-feature-specification.md) · [17-evaluation-methodology.md](17-evaluation-methodology.md)

Dataset strategy, sourcing, label normalization, deduplication, and split protocol.

---

## Problem Formulation

| Aspect | Definition |
|---|---|
| **Task** | Supervised binary classification (legitimate vs phishing) |
| **Inference mapping** | Probability + thresholds → {Safe, Suspicious, Phishing} |
| **Unit of analysis** | URL |
| **Grouping unit for splits** | Registered domain (eTLD+1) |
| **Positive class** | Confirmed phishing URLs |
| **Negative class** | Known legitimate URLs |

---

## Data Sources

### Phishing (Positive Class)

| Source | URL | Format | Update Frequency | License/Access |
|---|---|---|---|---|
| **PhishTank** | https://phishtank.org | CSV/JSON API | Continuous | Free API; attribution required |
| **OpenPhish** | https://openphish.com | Text feed (free tier) | Continuous | Free tier available |
| **URLhaus** | https://urlhaus.abuse.ch | CSV API | Continuous | Free; filter to phishing tags only |

**Primary source:** PhishTank (community verified).
**Supplementary:** OpenPhish for volume; URLhaus for recent campaigns.

### Legitimate (Negative Class)

| Source | URL | Format | Update Frequency | License/Access |
|---|---|---|---|---|
| **Tranco Top 1M** | https://tranco-list.eu | CSV | Daily | Open research dataset |
| **Majestic Million** | https://majestic.com/reports/majestic-million | CSV | Monthly | Free for research |
| **Common Crawl** | https://commoncrawl.org | WARC | Periodic | Open; sample URLs only |

**Primary source:** Tranco Top 1M (rank ≤ 100,000 for high-confidence negatives).
**Supplementary:** Majestic for diversity.

### Temporal Hold-Out (Evaluation Only)

| Source | Purpose |
|---|---|
| Recent PhishTank entries (last 3–6 months) | Temporal generalization test |
| Manually curated recent phishing URLs | Demo and qualitative evaluation |

---

## Label Normalization Rules

### Positive (phishing = 1)

Include URLs that meet **any** of:

- PhishTank `verified = yes`
- OpenPhish feed entry (active at collection time)
- URLhaus tag includes `phishing` or `phish`

Exclude from positive class:

- Malware-only URLs (no phishing tag) → label separately or exclude
- Defunct URLs returning persistent NXDOMAIN (mark as `inactive`, exclude from fetch-dependent experiments)
- Duplicate URLs within same campaign (deduplicate)

### Negative (legitimate = 0)

Include URLs that meet **all** of:

- Domain appears in Tranco top-100k OR Majestic top-100k
- URL uses HTTPS
- URL resolves successfully at collection time (DNS check)

Exclude from negative class:

- Domains also present in any phishing feed (cross-contamination check)
- URL paths containing login/payment on non-top sites (borderline → exclude or separate set)
- Parked domains or "coming soon" pages

### Borderline (evaluation only, not training)

- URL shortener links (bit.ly, t.co)
- New legitimate startups (< 90 days old, Tranco rank > 100k)
- Aged domains with login forms but Tranco rank < 500k
- Compromised legitimate domains (if identifiable)

Store in separate `borderline.csv` for demo and qualitative analysis only.

---

## Deduplication Protocol

### Step 1: URL normalization

Before deduplication, normalize each URL:

1. Lowercase scheme and host
2. Remove default ports (`:80`, `:443`)
3. Remove trailing slash from path (unless path is `/`)
4. Sort query parameters alphabetically
5. Decode percent-encoding where unambiguous
6. Convert punycode to Unicode for comparison (store both forms)

### Step 2: Exact URL deduplication

Remove exact duplicates after normalization. Keep earliest `collected_at` timestamp.

### Step 3: Domain-level deduplication for negatives

For legitimate class: keep **one URL per registered domain** (prefer HTTPS root or shortest path) to avoid over-representing large sites.

### Step 4: Near-duplicate path collapse (phishing)

For phishing URLs on same domain with same path prefix (e.g., `/campaign/page1`, `/campaign/page2`): keep one representative URL per unique path prefix (first 2 path segments).

### Step 5: Cross-contamination check

Remove any domain appearing in both positive and negative sets. Log removed domains for review.

---

## Dataset Versions

| Version | Contents | Purpose |
|---|---|---|
| `dataset_v1` | URL strings + labels only | Experiment A (URL-only baseline) |
| `dataset_v2` | v1 + domain features precomputed | Experiments B/C |
| `dataset_v3` | v2 + HTML/fetch features (fetch-success subset) | Experiments D/E |
| `dataset_temporal` | Recent phishing not in v1–v3 | Temporal evaluation (RQ8) |
| `dataset_borderline` | Borderline cases | Demo and qualitative only |

---

## Split Protocol

### Primary split: Domain-level holdout

**Critical rule:** No registered domain may appear in more than one of train/validation/test.

```
All URLs → Group by registered domain (eTLD+1)
         → Shuffle domains (seed=42)
         → Split domains: 60% train | 20% val | 20% test
         → Assign all URLs to split of their domain
```

### Class balance handling

Expected imbalance: more phishing URLs than unique legitimate domains.

| Strategy | Application |
|---|---|
| Undersample majority class domains | Training set only |
| Class weights in model | Logistic Regression, LightGBM |
| Report PR-AUC | Primary metric for imbalanced evaluation |
| Stratified domain sampling | Ensure both classes in each split |

Target balance (training set): ~1:1 to ~1:3 (legitimate:phishing) after undersampling.

### Temporal hold-out (separate from domain split)

```
PhishTank URLs from last 3-6 months
→ Remove any domain present in train/val/test
→ This becomes dataset_temporal
→ Never used for training or hyperparameter tuning
```

### Campaign leakage prevention

If campaign metadata available (URLhaus tags, PhishTank submission clusters):

- Group by campaign ID
- Assign entire campaign to same split as its domain
- Document campaigns that span multiple domains (rare)

---

## Dataset Schema

### Core CSV schema (`dataset_v1.csv`)

| Column | Type | Description |
|---|---|---|
| `url` | string | Normalized URL |
| `label` | int | 0 = legitimate, 1 = phishing |
| `registered_domain` | string | eTLD+1 extracted domain |
| `source` | string | Data source name |
| `collected_at` | datetime | Collection timestamp |
| `split` | string | train / val / test / temporal / borderline |
| `fetch_success` | bool | Null until fetched; True/False after |
| `inactive` | bool | True if NXDOMAIN at collection |

### Feature cache schema (`features_v2.parquet`)

| Column | Type | Description |
|---|---|---|
| `url_hash` | string | SHA256 of normalized URL |
| `{feature_name}` | varies | One column per feature (see 09-feature-specification) |
| `feature_tier` | int | Highest tier computed (0–3) |
| `computed_at` | datetime | Feature extraction timestamp |

---

## Collection Procedure

### Phase 1 checklist

- [ ] Register for PhishTank API key
- [ ] Download PhishTank CSV dump (verified entries)
- [ ] Download OpenPhish free feed
- [ ] Download URLhaus CSV (filter phishing tags)
- [ ] Download Tranco list (top 100k)
- [ ] Apply label normalization rules
- [ ] Apply deduplication protocol
- [ ] Run cross-contamination check
- [ ] Extract registered domains
- [ ] Create domain-level splits (seed=42)
- [ ] Create temporal hold-out set
- [ ] Document final statistics (below)
- [ ] Version and store in `data/` directory

### Directory structure (planned)

```text
data/
├── raw/
│   ├── phishtank/
│   ├── openphish/
│   ├── urlhaus/
│   └── tranco/
├── processed/
│   ├── dataset_v1.csv
│   ├── dataset_v2_features.parquet
│   ├── dataset_v3_features.parquet
│   ├── dataset_temporal.csv
│   └── dataset_borderline.csv
├── splits/
│   ├── train_domains.txt
│   ├── val_domains.txt
│   └── test_domains.txt
└── README.md
```

---

## Dataset Statistics (To Be Completed)

> Populate after Phase 1 collection is complete.

| Statistic | Train | Val | Test | Temporal |
|---|---|---|---|---|
| Total URLs | TBD | TBD | TBD | TBD |
| Unique domains | TBD | TBD | TBD | TBD |
| Phishing URLs | TBD | TBD | TBD | TBD |
| Legitimate URLs | TBD | TBD | TBD | TBD |
| Class ratio (leg:phish) | TBD | TBD | TBD | TBD |
| Date range | TBD | TBD | TBD | TBD |

---

## Data Quality Checks

Run before training:

| Check | Rule | Action if Failed |
|---|---|---|
| Domain leakage | No domain in multiple splits | Re-split |
| Cross-contamination | No domain in both classes | Remove domain |
| Duplicate URLs | Zero exact duplicates post-normalization | Re-deduplicate |
| Label consistency | All positives from approved sources | Review source |
| Inactive rate | < 30% inactive in phishing set | Collect fresher data |
| Fetch success rate | > 50% for dataset_v3 | Adjust fetch timeout/retry |

---

## Ethical and Legal Considerations

- Use only publicly available feeds and open research datasets
- Do not scrape login pages or submit credentials during collection
- Do not redistribute raw PhishTank data publicly (check license)
- Document data sources in final report with attribution
- Fetch worker uses identifiable bot User-Agent
- Analysis targets public URLs only; no authenticated pages

---

## Reproducibility

| Item | Location |
|---|---|
| Split seed | `seed=42` documented here |
| Raw data download date | Record in `data/README.md` |
| Processing script version | Git commit hash |
| Dataset version | Semantic version in filename |
| Feature extraction version | Linked to 09-feature-specification version |

Any change to split protocol requires a new dataset version and decision log entry.
