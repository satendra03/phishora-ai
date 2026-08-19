# 09 — Feature Specification

> **Related:** [08-data-specification.md](08-data-specification.md) · [10-ml-specification.md](10-ml-specification.md) · [12-risk-engine.md](12-risk-engine.md)

Formal feature taxonomy: 30 defensible features with tier, availability, and metadata.

**Version:** 1.0.0
**Status:** Draft — prune after Experiment A ablation

---

## Feature Tiers

| Tier | Name | Availability | Requires Visit? |
|---|---|---|---|
| **0** | Instant | From URL string alone | No |
| **1** | Passive | DNS, WHOIS, TLS handshake | Partial (TLS probe only) |
| **2** | Active | HTTP fetch + HTML parse | Yes |
| **3** | External | Threat intelligence APIs | No (API call) |

ML training must document which tier each feature belongs to and ensure inference parity.

---

## Feature Catalog

### Tier 0 — URL Features (15 features)

| # | Name | Type | Description | External API? | Cost | Relevance | Limitations |
|---|---|---|---|---|---|---|---|
| F01 | `url_length` | int | Total character count of normalized URL | No | Low | Medium | Legitimate CDN URLs can be long |
| F02 | `domain_length` | int | Character count of registered domain | No | Low | Medium | Short domains not always malicious |
| F03 | `path_length` | int | Character count of URL path component | No | Low | Medium | API endpoints have long paths |
| F04 | `subdomain_count` | int | Number of dot-separated subdomain labels | No | Low | Medium-High | CDN patterns (e.g., `cdn.shop.example.com`) |
| F05 | `url_has_ip` | bool | Host is a literal IPv4/IPv6 address | No | Low | High | Rare legitimate uses (dev servers) |
| F06 | `num_digits_in_domain` | int | Count of digit characters in domain | No | Low | Medium | Some legit domains have digits |
| F07 | `digit_ratio_domain` | float | Digits / total domain length | No | Low | Medium | Normalized version of F06 |
| F08 | `special_char_count` | int | Count of `-`, `_`, `@`, `%`, `=` in URL | No | Low | Medium | Query params inflate count |
| F09 | `suspicious_keyword_count` | int | Count of keywords: login, verify, secure, account, update, confirm, banking, password, wallet | No | Low | Medium | Common on legitimate login pages |
| F10 | `has_punycode` | bool | Domain contains `xn--` (IDN/punycode) | No | Low | High | Homograph attack indicator |
| F11 | `domain_entropy` | float | Shannon entropy of domain string (bits) | No | Low | Medium-High | Random DGA domains; needs threshold |
| F12 | `has_at_symbol` | bool | URL contains `@` (credential hiding trick) | No | Low | High | Rare; strong obfuscation signal |
| F13 | `num_query_params` | int | Count of query string parameters | No | Low | Low-Medium | Tracking params on legit sites |
| F14 | `has_port` | bool | URL specifies non-default port | No | Low | Medium | Dev servers use custom ports |
| F15 | `is_trusted_tld` | bool | TLD in common legitimate set (.com, .org, .net, .edu, .gov) | No | Low | Low | Weak alone; `.com` very common in phishing |

---

### Tier 1 — Domain & Passive Network Features (8 features)

| # | Name | Type | Description | External API? | Cost | Relevance | Limitations |
|---|---|---|---|---|---|---|---|
| F16 | `domain_age_days` | int | Days since domain registration | Yes (WHOIS/RDAP) | Medium | High | Missing for some TLDs/privacy |
| F17 | `whois_privacy_enabled` | bool | WHOIS privacy/proxy service detected | Yes (WHOIS/RDAP) | Medium | Low-Medium | Common on legit sites too |
| F18 | `in_tranco_top1m` | bool | Domain in Tranco top 1 million | Yes (Tranco list) | Low | Medium | Legitimacy prior only |
| F19 | `tranco_rank` | int | Tranco rank (0 if not listed) | Yes (Tranco list) | Low | Medium | Lower rank = more popular |
| F20 | `dns_a_record_count` | int | Number of A records returned | No (DNS) | Low | Low | Infrastructure diversity |
| F21 | `has_mx_record` | bool | Domain has MX (mail) DNS record | No (DNS) | Low | Low | Established domains usually have MX |
| F22 | `has_https` | bool | HTTPS connection succeeds (TLS probe) | No (TLS) | Low | Low alone | **Must not imply safety** |
| F23 | `cert_valid` | bool | TLS certificate is currently valid (not expired) | No (TLS) | Medium | Medium | Valid cert on phishing sites exists |

---

### Tier 2 — Active Fetch Features (7 features)

| # | Name | Type | Description | External API? | Cost | Relevance | Limitations |
|---|---|---|---|---|---|---|---|
| F24 | `redirect_count` | int | Number of HTTP redirects followed | No | Medium | High | Needs successful fetch |
| F25 | `cross_domain_redirect` | bool | Final domain differs from submitted domain | No | Medium | High | Legitimate URL shorteners |
| F26 | `cert_domain_mismatch` | bool | TLS cert CN/SAN does not match domain | No (TLS) | Medium | High | Needs fetch to final URL |
| F27 | `has_password_field` | bool | HTML contains `<input type="password">` | No | Medium | High | Legit login pages too |
| F28 | `form_action_external` | bool | Form `action` attribute points to different domain | No | Medium | High | Strong credential theft signal |
| F29 | `hidden_input_count` | int | Count of `<input type="hidden">` elements | No | Medium | Medium | Tracking forms on legit sites |
| F30 | `iframe_count` | int | Count of `<iframe>` elements in HTML | No | Medium | Medium | Ads and embeds on legit sites |

---

## Feature Summary by Experiment

| Experiment | Features | Count |
|---|---|---|
| **A** (URL-only) | F01–F15 | 15 |
| **B** (+ domain) | F01–F23 | 23 |
| **C** (B + active TLS/redirect) | F01–F26 | 26 |
| **D** (+ HTML) | F01–F30 | 30 |
| **E** (+ TI) | F01–F30 + TI features* | 30+ |

*TI features (Tier 3) are evidence items for the risk engine, not ML training features in core experiments. See [11-external-intelligence.md](11-external-intelligence.md).

---

## Feature Extraction Notes

### F04 — subdomain_count

```
Extract host from URL → split by '.' → count labels minus TLD minus registered domain labels
Example: "login.secure.example.com" → subdomain_count = 1 ("login")
Example: "example.com" → subdomain_count = 0
```

Use Public Suffix List for registered domain extraction.

### F11 — domain_entropy

```
H = -Σ p(c) * log2(p(c)) for each character c in domain
High entropy (> 3.5) suggests randomly generated DGA domain
```

Threshold to be tuned on validation set.

### F16 — domain_age_days

```
domain_age_days = (today - whois_creation_date).days
If WHOIS unavailable: impute as null; handle in model as missing
If domain_age_days < 0: set to 0 (clock skew)
```

### F28 — form_action_external

```
For each <form> with action attribute:
  Parse action URL → extract domain
  If domain != page domain AND domain != registered domain of page: True
Also check for password field in same form (compound signal)
```

---

## Missing Value Handling

| Feature | Missing When | Imputation Strategy |
|---|---|---|
| F16, F17 | WHOIS unavailable | Null; LightGBM handles natively |
| F18, F19 | Domain not in Tranco | `in_tranco_top1m = False`, `tranco_rank = 0` |
| F22, F23 | TLS probe fails | Null |
| F24–F30 | Fetch fails/unreachable | Null; exclude from Tier 2 experiments |

**Rule:** Never impute missing Tier 2 features with zero — use null to distinguish "not fetched" from "fetched and absent."

---

## Security and Privacy

| Feature | Security Concern | Mitigation |
|---|---|---|
| F24–F30 | Require active fetch of potentially malicious URL | Safe fetch worker with SSRF guard |
| F16, F17 | WHOIS query reveals analysis intent | Rate limit; cache results |
| All | Feature values logged | Log feature vector, not raw HTML |

---

## Ablation Priority

After Experiment A, ablate in this order (highest expected redundancy first):

1. F07 vs F06 (digit_ratio vs num_digits — keep one)
2. F15 (is_trusted_tld — likely weak)
3. F13 (num_query_params)
4. F21 (has_mx_record)
5. F29 (hidden_input_count)

Document removed features in decision log after ablation.

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-08-18 | Initial 30-feature specification |
