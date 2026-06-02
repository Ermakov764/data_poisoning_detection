from pathlib import Path

import pandas as pd
import torch

from src.core.loaders import project_root


def init_demo_assets() -> tuple[str, str]:
    root = project_root()
    data_dir = root / "data"
    model_dir = root / "models"
    data_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = data_dir / "sample.csv"
    model_path = model_dir / "sample.pt"

    df = pd.DataFrame(
        {
            "text": ["hello", "world", "select * from users"],
            "label": [0, 0, 1],
        }
    )
    df.to_csv(dataset_path, index=False)

    model = torch.nn.Linear(4, 2)
    torch.save(model.state_dict(), model_path)

    return str(dataset_path), str(model_path)

