from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ScannerCategory(str, Enum):
    SANITY = "sanity"
    STATS = "stats"
    MODEL = "model"


class ScanStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    HAND_CHECK = "hand_check"


@dataclass
class ScanContext:
    dataset_path: str
    model_path: str
    dataset: Optional[Any] = None
    model_state: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResult:
    name: str
    category: ScannerCategory
    status: ScanStatus
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)


class BaseScanner(ABC):
    name: str = "Abstract Base Scanner"
    category: ScannerCategory = ScannerCategory.SANITY

    @abstractmethod
    def run(self, context: ScanContext) -> ScanResult:
        """
        Должен возвращать ScanResult.
        - status: ScanStatus
        - passed: bool (для быстрой остановки пайплайна)
        - details: метрики/описания
        """
        raise NotImplementedError
