import re
from typing import Dict

import pandas as pd
from pandas.api.types import is_string_dtype

from src.core.factory import register_scanner
from src.scanners.base import BaseScanner, ScanContext, ScanResult, ScanStatus, ScannerCategory


@register_scanner
class SqlLikePayloadScanner(BaseScanner):
    name = "Sanity: SQL-like payloads"
    category = ScannerCategory.SANITY

    def run(self, context: ScanContext) -> ScanResult:
        dataset = context.dataset
        if dataset is None or not isinstance(dataset, pd.DataFrame):
            return ScanResult(
                name=self.name,
                category=self.category,
                status=ScanStatus.FAILED,
                passed=False,
                details={"reason": "Dataset not loaded"},
            )

        string_columns = [col for col in dataset.columns if is_string_dtype(dataset[col].dtype)]
        if not string_columns:
            return ScanResult(
                name=self.name,
                category=self.category,
                status=ScanStatus.SKIPPED,
                passed=True,
                details={"reason": "No string columns"},
            )

        pattern = re.compile(r"(?:select|insert|update|delete|drop|--|;|\bor\b|\band\b)", re.IGNORECASE)
        hits: Dict[str, int] = {}
        for column in string_columns:
            series = dataset[column].astype(str).fillna("")
            hits[column] = int(series.str.contains(pattern).sum())

        total_hits = sum(hits.values())
        hit_ratio = total_hits / max(len(dataset), 1)
        passed = total_hits == 0

        return ScanResult(
            name=self.name,
            category=self.category,
            status=ScanStatus.PASSED if passed else ScanStatus.FAILED,
            passed=passed,
            details={
                "string_columns": string_columns,
                "hit_counts": hits,
                "hit_ratio": hit_ratio,
                "threshold": 0,
            },
        )
