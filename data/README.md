# Data Directory

This directory stores datasets for Phishora AI ML experiments.

**Do not commit raw downloaded feeds or large processed files to git.**

See [docs/08-data-specification.md](../docs/08-data-specification.md) for full data strategy.

## Structure

```text
data/
├── raw/           # Downloaded feeds (gitignored)
├── processed/     # Normalized datasets (gitignored if large)
├── splits/        # Domain split lists
└── README.md      # This file
```

## Setup (Phase 1)

1. Obtain PhishTank API key
2. Download feeds per 08-data-specification.md
3. Run processing scripts (to be created in Phase 1)
4. Record download dates and statistics in 08-data-specification.md

## Gitignore

Add to `.gitignore`:

```
data/raw/
data/processed/*.csv
data/processed/*.parquet
```

Keep split domain lists and README version-controlled.
