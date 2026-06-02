# Data Poisoning Detection Gate

CLI for dataset/model checks before training. Scanners are grouped by category: sanity, stats, model.

## Quick start

1) Install dependencies.
2) Put datasets under `data/` and models under `models/`.
3) Run the scanner.

## CLI usage

Default mode runs sanity + stats, then model scans only if previous checks pass.

```
python -m src.cli scan --dataset data/train.parquet --model models/model.pt
```

Run all categories regardless of failures:

```
python -m src.cli scan --mode all --dataset data/train.parquet --model models/model.pt
```

Run only one category:

```
python -m src.cli scan --mode only --only sanity --dataset data/train.parquet
```

## Add a scanner

Create a scanner class in `src/scanners/<category>/` and decorate it with `@register_scanner`.
Each scanner implements `run(self, context: ScanContext) -> ScanResult` and returns a status, pass/fail, and details.

## Report output

Reports are stored under `reports/` as JSON files:

```
reports/scan_report_<id>.json
```

