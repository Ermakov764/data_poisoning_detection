import torch

from src.core.factory import register_scanner
from src.scanners.base import BaseScanner, ScanContext, ScanResult, ScanStatus, ScannerCategory


@register_scanner
class WeightAnomalyScanner(BaseScanner):
    name = "Model: weight anomalies"
    category = ScannerCategory.MODEL

    def run(self, context: ScanContext) -> ScanResult:
        state_dict = context.model_state
        if not state_dict:
            return ScanResult(
                name=self.name,
                category=self.category,
                status=ScanStatus.FAILED,
                passed=False,
                details={"reason": "Model not loaded"},
            )

        nan_params = 0
        inf_params = 0
        max_abs = 0.0
        total_tensors = 0

        for tensor in state_dict.values():
            if not isinstance(tensor, torch.Tensor):
                continue
            total_tensors += 1
            nan_params += int(torch.isnan(tensor).sum().item())
            inf_params += int(torch.isinf(tensor).sum().item())
            max_abs = max(max_abs, float(tensor.abs().max().item()))

        passed = nan_params == 0 and inf_params == 0 and max_abs < 1e6

        return ScanResult(
            name=self.name,
            category=self.category,
            status=ScanStatus.PASSED if passed else ScanStatus.FAILED,
            passed=passed,
            details={
                "total_tensors": total_tensors,
                "nan_params": nan_params,
                "inf_params": inf_params,
                "max_abs": max_abs,
                "max_abs_threshold": 1e6,
            },
        )
