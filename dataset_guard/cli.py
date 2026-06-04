from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .gate import DatasetSecurityGate
from .models import Decision
from .report import print_summary, write_findings_csv, write_json_report


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="dataset-security-gate",
        description="Scan tabular datasets for security payloads, PII, and suspicious content.",
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input dataset file or directory. Supported formats: CSV, JSON, JSONL, Parquet.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("outputs/dataset_security_gate/report.json"),
        help="Path to the JSON report output.",
    )

    parser.add_argument(
        "--findings-csv",
        type=Path,
        default=None,
        help="Optional path to a flat CSV file with one row per finding.",
    )

    parser.add_argument(
        "--allow-degraded",
        action="store_true",
        help="Allow degraded mode when optional engines are unavailable.",
    )

    parser.add_argument(
        "--no-presidio",
        action="store_true",
        help="Disable Presidio even if it is enabled through environment variables.",
    )

    parser.add_argument(
        "--presidio",
        action="store_true",
        help="Enable Presidio for slow PII scanning.",
    )

    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Return non-zero exit codes for REVIEW or BLOCK decisions.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point.
    """

    parser = build_parser()
    args = parser.parse_args(argv)

    _apply_cli_env_overrides(args)

    gate = DatasetSecurityGate.from_env(Path.cwd())
    report = gate.scan_path(args.input)

    write_json_report(report, args.output)

    if args.findings_csv is not None:
        write_findings_csv(report, args.findings_csv)

    print_summary(report)

    if not args.exit_code:
        return 0

    if report.decision == Decision.BLOCK:
        return 2

    if report.decision == Decision.REVIEW:
        return 1

    return 0


def _apply_cli_env_overrides(args: argparse.Namespace) -> None:
    """
    Apply simple CLI flags as environment overrides.

    This keeps AppConfig.from_env() as the single configuration assembly point.
    """

    import os

    if args.allow_degraded:
        os.environ["DATASET_SECURITY_ALLOW_DEGRADED"] = "1"

    if args.no_presidio:
        os.environ["DATASET_SECURITY_ENABLE_PRESIDIO"] = "0"

    if args.presidio:
        os.environ["DATASET_SECURITY_ENABLE_PRESIDIO"] = "1"


if __name__ == "__main__":
    raise SystemExit(main())