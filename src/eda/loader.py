from pathlib import Path

import pandas as pd


class EDALoader:
    REQUIRED_COLUMNS: frozenset[str] = frozenset({"time", "flux"})

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> pd.DataFrame:

        if not self.path.is_file():
            raise FileNotFoundError(f"File not found: {self.path}")

        if self.path.stat().st_size == 0:
            raise ValueError(f"File is empty: {self.path}")

        df = pd.read_parquet(self.path)
        self._validate_schema(df)
        return df

    def _validate_schema(self, df: pd.DataFrame) -> None:
        missing = self.REQUIRED_COLUMNS.difference(df.columns)
        if missing:
            raise ValueError(
                f"The dataframe must have columns {missing}. Current columns: {list(df.columns)}"
            )

        if df.empty:
            raise ValueError("The dataframe cannot be empty.")
