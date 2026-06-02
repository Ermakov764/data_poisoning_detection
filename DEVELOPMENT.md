# Руководство разработчика

Этот документ объясняет, как расширять систему сканеров и не дублировать общую логику.

## В .gitignore нет исключений для `data/` и `models/`. Если оно вам на гите не нужно - удаляйте из индекса гита руками

## Структура проекта

- `data/` и `models/` — единственные допустимые места для входных данных.
- `reports/` хранит JSON-отчеты.
- `src/scanners/` содержит реализации сканеров по категориям.
- `src/core/` содержит пайплайн, загрузчики и реестр.

## Как добавить новый сканер

1) Создайте файл в нужной категории:
   - `src/scanners/sanity/` — проверки здравого смысла
   - `src/scanners/stats/` — статистические проверки
   - `src/scanners/model_scan/` — проверки модели

2) Можно возврящать не только 'PASSED'/'FAILED', но и 'SKIPPED/HAND_CHECK' для промежуточных состояний, если это имеет смысл для вашей проверки."

3) Реализуйте класс, унаследованный от `BaseScanner`, и добавьте декоратор `@register_scanner`.

Минимальный шаблон:

```python
from src.core.factory import register_scanner
from src.scanners.base import BaseScanner, ScanContext, ScanResult, ScanStatus, ScannerCategory


@register_scanner
class MyScanner(BaseScanner):
    name = "Sanity: my check"
    category = ScannerCategory.SANITY

    def run(self, context: ScanContext) -> ScanResult:
        # Используйте context.dataset, context.model_state, context.metadata
        passed = True
        return ScanResult(
            name=self.name,
            category=self.category,
            status=ScanStatus.PASSED if passed else ScanStatus.FAILED,
            passed=passed,
            details={"note": "описание метрик"},
        )
```

## Не дублируйте загрузку данных/модели

Используйте общие загрузчики из `src/core/loaders.py`:
- `load_dataset(...)` поддерживает `csv` и `parquet`.
- `load_model(...)` поддерживает `.pt` и `.safetensors`.

Так мы гарантируем:
- единые проверки путей (`data/` и `models/`)
- единые метаданные (например, `num_params`)
- одно место для расширения форматов и логики

## Правила выполнения

- По умолчанию сначала идут sanity и stats, потом model.
- Если любой блок sanity/stats провален, модельные проверки не запускаются.
- Поведение можно переопределить через CLI `--mode all` или `--mode only`.

## Режимы CLI

- `default`: sanity + stats; model только если прошли предыдущие блоки
- `all`: запускать все категории независимо от ошибок
- `only`: запускать только одну категорию (`sanity`, `stats`, `model`)

## Формат отчета

Каждый запуск пишет JSON-отчет в `reports/`:

```
reports/scan_report_<id>.json
```

При добавлении сканера убедитесь, что `details` сериализуется в JSON.

## Соглашения

- Не печатайте в консоль из сканеров — возвращайте данные в `details`.
- Пороговые значения держите рядом в коде сканера (так проще читать).

## English version (мне все еще хочется потом добавить это в cv:)

This section mirrors the Russian guide for reference.

### Project layout

- `data/` and `models/` are the only allowed input locations.
- `reports/` stores JSON reports.
- `src/scanners/` contains scanners grouped by category.
- `src/core/` contains the pipeline, loaders, and registry.

### Add a new scanner

1) Create a file under the right category:
   - `src/scanners/sanity/` for sanity checks
   - `src/scanners/stats/` for statistical checks
   - `src/scanners/model_scan/` for model checks

2) Implement a `BaseScanner` and register it with `@register_scanner`.

Minimal template:

```python
from src.core.factory import register_scanner
from src.scanners.base import BaseScanner, ScanContext, ScanResult, ScanStatus, ScannerCategory


@register_scanner
class MyScanner(BaseScanner):
    name = "Sanity: my check"
    category = ScannerCategory.SANITY

    def run(self, context: ScanContext) -> ScanResult:
        # Use context.dataset, context.model_state, context.metadata
        passed = True
        return ScanResult(
            name=self.name,
            category=self.category,
            status=ScanStatus.PASSED if passed else ScanStatus.FAILED,
            passed=passed,
            details={"note": "metrics description"},
        )
```

### Do not duplicate loaders

Use shared loaders in `src/core/loaders.py`:
- `load_dataset(...)` supports `csv` and `parquet`.
- `load_model(...)` supports `.pt` and `.safetensors`.

This guarantees:
- consistent path checks (`data/` and `models/`)
- consistent metadata (for example, `num_params`)
- one place to extend formats and logic

### Execution rules

- By default, sanity and stats run first, then model checks.
- If any sanity/stats block fails, model checks are skipped.
- Override with CLI `--mode all` or `--mode only`.

### CLI modes

- `default`: sanity + stats; model only if previous blocks pass
- `all`: run all categories regardless of failures
- `only`: run a single category (`sanity`, `stats`, `model`)

### Report output

Each run writes a JSON report to `reports/`:

```
reports/scan_report_<id>.json
```

When adding a scanner, ensure `details` is JSON-serializable.

### Conventions

- Do not print from scanners; return data in `details`.
- Keep thresholds close to the scanner code for readability.
