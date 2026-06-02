from typing import Optional

import pandas as pd

from src.core.factory import register_scanner
from src.scanners.base import BaseScanner, ScanContext, ScanResult, ScanStatus, ScannerCategory


@register_scanner
class ClassBalanceScanner(BaseScanner):
    name = "Stats: class balance"
    category = ScannerCategory.STATS

    def _find_label_column(self, dataset: pd.DataFrame) -> Optional[str]:
        for candidate in ("label", "target", "y", "class"):
            if candidate in dataset.columns:
                return candidate
        return None

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

        label_column = self._find_label_column(dataset)
        if label_column is None:
            return ScanResult(
                name=self.name,
                category=self.category,
                status=ScanStatus.SKIPPED,
                passed=True,
                details={"reason": "No label column found"},
            )

        counts = dataset[label_column].value_counts()
        min_count = int(counts.min()) if not counts.empty else 0
        max_count = int(counts.max()) if not counts.empty else 0
        imbalance_ratio = (max_count / max(min_count, 1)) if counts.size > 0 else 0.0
        threshold = 5.0
        passed = imbalance_ratio <= threshold

        return ScanResult(
            name=self.name,
            category=self.category,
            status=ScanStatus.PASSED if passed else ScanStatus.FAILED,
            passed=passed,
            details={
                "label_column": label_column,
                "class_counts": counts.to_dict(),
                "imbalance_ratio": imbalance_ratio,
                "threshold": threshold,
            },
        )

