import pandas as pd
from typing import List
from pydantic import BaseModel


def save_to_csv_pd(records: List[BaseModel], file_path: str) -> None:
    if not records:
        print(f"No records to write for {file_path}")
        return

    rows = [r.model_dump(by_alias=True) for r in records]
    df = pd.DataFrame(rows)
    df.to_csv(file_path, index=False)

    print(f"CSV written: {file_path}")
