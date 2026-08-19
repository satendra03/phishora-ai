#!/usr/bin/env python3
"""
Phase 1: Data Collection & Processing for Phishora AI
Downloads phishing and legitimate URL datasets, applies normalization,
deduplication, and creates domain-level splits.
"""

import os
import sys
import csv
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from collections import defaultdict
import requests
import tldextract

DATA_ROOT = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_ROOT / "raw"
PROCESSED_DIR = DATA_ROOT / "processed"
SPLITS_DIR = DATA_ROOT / "splits"

PHISHTANK_URL = "https://data.phishtank.com/data/online-valid.csv"
OPENPHISH_URL = "https://openphish.com/feed.txt"
URLHAUS_URL = "https://urlhaus.abuse.ch/downloads/csv/"
TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"

HEADERS = {
    "User-Agent": "PhishoraAI/1.0 (+https://github.com/phishora-ai; research project)"
}


def ensure_dirs():
    for d in [RAW_DIR / "phishtank", RAW_DIR / "openphish", RAW_DIR / "urlhaus", RAW_DIR / "tranco", PROCESSED_DIR, SPLITS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path, desc: str = ""):
    print(f"Downloading {desc} from {url}...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  Saved to {dest} ({dest.stat().st_size:,} bytes)")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def normalize_url(url: str) -> str:
    """Normalize URL per specification."""
    try:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        if netloc.startswith("www."):
            netloc = netloc[4:]

        if ":80" in netloc and scheme == "http":
            netloc = netloc.replace(":80", "")
        if ":443" in netloc and scheme == "https":
            netloc = netloc.replace(":443", "")

        path = parsed.path
        if path != "/" and path.endswith("/"):
            path = path[:-1]

        query_params = parse_qs(parsed.query, keep_blank_values=True)
        sorted_params = sorted(query_params.items())
        query = urlencode(sorted_params, doseq=True)

        normalized = urlunparse((scheme, netloc, path, parsed.params, query, ""))
        return normalized
    except Exception:
        return url.strip().lower()


def get_registered_domain(url: str) -> str:
    """Extract registered domain (eTLD+1) using tldextract."""
    try:
        extracted = tldextract.extract(url)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}".lower()
        return ""
    except Exception:
        return ""


def load_phishtank(filepath: Path) -> list[dict]:
    """Load PhishTank CSV, filter verified entries."""
    entries = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("verified", "").lower() == "yes":
                url = row.get("url", "").strip()
                if url:
                    entries.append({
                        "url": url,
                        "label": 1,
                        "source": "phishtank",
                        "collected_at": datetime.utcnow().isoformat(),
                        "verified": True
                    })
    return entries


def load_openphish(filepath: Path) -> list[dict]:
    """Load OpenPhish text feed."""
    entries = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            url = line.strip()
            if url and not url.startswith("#"):
                entries.append({
                    "url": url,
                    "label": 1,
                    "source": "openphish",
                    "collected_at": datetime.utcnow().isoformat()
                })
    return entries


def load_urlhaus(filepath: Path) -> list[dict]:
    """Load URLhaus CSV, filter phishing tags."""
    entries = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            if len(row) >= 5:
                url = row[2].strip()
                tags = row[4].lower() if len(row) > 4 else ""
                if url and ("phishing" in tags or "phish" in tags):
                    entries.append({
                        "url": url,
                        "label": 1,
                        "source": "urlhaus",
                        "collected_at": datetime.utcnow().isoformat(),
                        "tags": tags
                    })
    return entries


def load_tranco(filepath: Path, max_rank: int = 100000) -> list[dict]:
    """Load Tranco top 1M, filter to top N."""
    entries = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                try:
                    rank = int(row[0])
                    domain = row[1].strip()
                    if rank <= max_rank:
                        url = f"https://{domain}/"
                        entries.append({
                            "url": url,
                            "label": 0,
                            "source": "tranco",
                            "collected_at": datetime.utcnow().isoformat(),
                            "tranco_rank": rank
                        })
                except ValueError:
                    continue
    return entries


def deduplicate_entries(entries: list[dict]) -> list[dict]:
    """Apply deduplication protocol."""
    print(f"Deduplicating {len(entries)} entries...")

    # Step 1: Normalize URLs
    for e in entries:
        e["normalized_url"] = normalize_url(e["url"])
        e["registered_domain"] = get_registered_domain(e["normalized_url"])

    # Step 2: Exact URL deduplication (keep earliest)
    url_to_entry = {}
    for e in entries:
        norm_url = e["normalized_url"]
        if norm_url not in url_to_entry:
            url_to_entry[norm_url] = e
        else:
            existing = url_to_entry[norm_url]
            if e["collected_at"] < existing["collected_at"]:
                url_to_entry[norm_url] = e

    entries = list(url_to_entry.values())
    print(f"  After exact URL dedup: {len(entries)}")

    # Step 3: Domain-level deduplication for negatives
    neg_entries = [e for e in entries if e["label"] == 0]
    pos_entries = [e for e in entries if e["label"] == 1]

    domain_to_neg = {}
    for e in neg_entries:
        domain = e["registered_domain"]
        if domain and domain not in domain_to_neg:
            domain_to_neg[domain] = e

    neg_deduped = list(domain_to_neg.values())
    print(f"  Negative domains after dedup: {len(neg_deduped)}")

    # Step 4: Near-duplicate path collapse for positives
    pos_by_domain = defaultdict(list)
    for e in pos_entries:
        pos_by_domain[e["registered_domain"]].append(e)

    pos_deduped = []
    for domain, urls in pos_by_domain.items():
        seen_prefixes = set()
        for e in urls:
            parsed = urlparse(e["normalized_url"])
            path_parts = [p for p in parsed.path.split("/") if p]
            prefix = "/".join(path_parts[:2]) if len(path_parts) >= 2 else (path_parts[0] if path_parts else "")
            key = f"{domain}/{prefix}"
            if key not in seen_prefixes:
                seen_prefixes.add(key)
                pos_deduped.append(e)

    print(f"  Positive URLs after path collapse: {len(pos_deduped)}")

    # Step 5: Cross-contamination check
    neg_domains = {e["registered_domain"] for e in neg_deduped if e["registered_domain"]}
    pos_domains = {e["registered_domain"] for e in pos_deduped if e["registered_domain"]}
    overlap = neg_domains & pos_domains

    if overlap:
        print(f"  WARNING: {len(overlap)} domains in both classes, removing...")
        for domain in overlap:
            print(f"    Removing: {domain}")
        neg_deduped = [e for e in neg_deduped if e["registered_domain"] not in overlap]
        pos_deduped = [e for e in pos_deduped if e["registered_domain"] not in overlap]

    return neg_deduped + pos_deduped


def create_splits(entries: list[dict], seed: int = 42) -> dict[str, list[str]]:
    """Create domain-level splits: 60/20/20 train/val/test."""
    import random
    random.seed(seed)

    domains = list(set(e["registered_domain"] for e in entries if e["registered_domain"]))
    random.shuffle(domains)

    n = len(domains)
    train_end = int(n * 0.6)
    val_end = train_end + int(n * 0.2)

    splits = {
        "train": set(domains[:train_end]),
        "val": set(domains[train_end:val_end]),
        "test": set(domains[val_end:])
    }

    for e in entries:
        domain = e["registered_domain"]
        if domain in splits["train"]:
            e["split"] = "train"
        elif domain in splits["val"]:
            e["split"] = "val"
        else:
            e["split"] = "test"

    return splits


def save_dataset(entries: list[dict], filepath: Path):
    """Save dataset to CSV with schema."""
    fieldnames = ["url", "label", "registered_domain", "source", "collected_at", "split", "fetch_success", "inactive"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in entries:
            row = {k: e.get(k, "") for k in fieldnames}
            writer.writerow(row)
    print(f"Saved {len(entries)} entries to {filepath}")


def save_splits(splits: dict[str, set[str]], split_dir: Path):
    """Save domain split lists."""
    for name, domains in splits.items():
        filepath = split_dir / f"{name}_domains.txt"
        with open(filepath, "w") as f:
            for domain in sorted(domains):
                f.write(f"{domain}\n")
        print(f"Saved {len(domains)} domains to {filepath}")


def print_statistics(entries: list[dict]):
    """Print dataset statistics."""
    by_split = defaultdict(lambda: {"total": 0, "phish": 0, "legit": 0, "domains": set()})
    for e in entries:
        s = e.get("split", "unknown")
        by_split[s]["total"] += 1
        by_split[s]["domains"].add(e.get("registered_domain", ""))
        if e["label"] == 1:
            by_split[s]["phish"] += 1
        else:
            by_split[s]["legit"] += 1

    print("\n=== Dataset Statistics ===")
    for split in ["train", "val", "test", "temporal", "borderline"]:
        if split not in by_split:
            continue
        stats = by_split[split]
        domains = len(stats["domains"])
        phish = stats["phish"]
        legit = stats["legit"]
        ratio = f"{legit}:{phish}" if phish > 0 else "N/A"
        print(f"  {split:10s} | URLs: {stats['total']:6d} | Domains: {domains:5d} | Phish: {phish:5d} | Legit: {legit:5d} | Ratio: {ratio}")


def main():
    parser = argparse.ArgumentParser(description="Phase 1: Data collection and processing")
    parser.add_argument("--download", action="store_true", help="Download raw datasets")
    parser.add_argument("--process", action="store_true", help="Process and create splits")
    parser.add_argument("--all", action="store_true", help="Run download and process")
    args = parser.parse_args()

    if not any([args.download, args.process, args.all]):
        args.all = True

    ensure_dirs()

    if args.download or args.all:
        print("\n=== Downloading Raw Datasets ===")
        download_file(PHISHTANK_URL, RAW_DIR / "phishtank" / "online-valid.csv", "PhishTank")
        download_file(OPENPHISH_URL, RAW_DIR / "openphish" / "feed.txt", "OpenPhish")
        download_file(URLHAUS_URL, RAW_DIR / "urlhaus" / "urlhaus.csv", "URLhaus")
        download_file(TRANCO_URL, RAW_DIR / "tranco" / "top-1m.csv.zip", "Tranco")

        import zipfile
        tranco_zip = RAW_DIR / "tranco" / "top-1m.csv.zip"
        tranco_csv = RAW_DIR / "tranco" / "top-1m.csv"
        if tranco_zip.exists():
            with zipfile.ZipFile(tranco_zip, "r") as z:
                z.extractall(RAW_DIR / "tranco")

    if args.process or args.all:
        print("\n=== Processing Datasets ===")

        phish_entries = []
        if (RAW_DIR / "phishtank" / "online-valid.csv").exists():
            phish_entries.extend(load_phishtank(RAW_DIR / "phishtank" / "online-valid.csv"))
        if (RAW_DIR / "openphish" / "feed.txt").exists():
            phish_entries.extend(load_openphish(RAW_DIR / "openphish" / "feed.txt"))
        if (RAW_DIR / "urlhaus" / "urlhaus.csv").exists():
            phish_entries.extend(load_urlhaus(RAW_DIR / "urlhaus" / "urlhaus.csv"))

        legit_entries = []
        if (RAW_DIR / "tranco" / "top-1m.csv").exists():
            legit_entries.extend(load_tranco(RAW_DIR / "tranco" / "top-1m.csv", max_rank=100000))

        print(f"Loaded {len(phish_entries)} phishing, {len(legit_entries)} legitimate URLs")

        all_entries = deduplicate_entries(phish_entries + legit_entries)

        splits = create_splits(all_entries)

        save_dataset(all_entries, PROCESSED_DIR / "dataset_v1.csv")
        save_splits(splits, SPLITS_DIR)
        print_statistics(all_entries)

        with open(DATA_ROOT / "README.md", "a") as f:
            f.write(f"\n\n## Collection Run: {datetime.utcnow().isoformat()}\n")
            f.write(f"- PhishTank entries: {len(phish_entries)}\n")
            f.write(f"- OpenPhish entries: {len([e for e in phish_entries if e['source']=='openphish'])}\n")
            f.write(f"- URLhaus entries: {len([e for e in phish_entries if e['source']=='urlhaus'])}\n")
            f.write(f"- Tranco entries: {len(legit_entries)}\n")
            f.write(f"- After dedup: {len(all_entries)}\n")


if __name__ == "__main__":
    main()