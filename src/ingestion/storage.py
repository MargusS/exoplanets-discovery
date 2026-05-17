import re
from pathlib import Path

from .models import LightCurveData


class StorageManager:
    """Manages the persistence of astronomical data in optimized formats (Parquet)."""

    def __init__(self, output_dir: str | Path = "data/processed"):
        self.output_dir = Path(output_dir)
        # Create the directory structure if it does not exist (like 'mkdir -p' in bash)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """
        Internal method to convert a target ID into a safe OS filename.
        Example: 'KIC 12345' -> 'kic_12345'
        """
        clean_name = name.lower().strip()
        # Replace any non-alphanumeric character with an underscore
        clean_name = re.sub(r"[^a-z0-9]+", "_", clean_name)
        return clean_name

    def save_to_parquet(self, lc_data: LightCurveData) -> Path:
        """
        Serializes the LightCurveData DataFrame to a Parquet file.
        Returns the absolute path to the saved file.
        """
        safe_name = self._sanitize_filename(lc_data.target_id)
        file_path = self.output_dir / f"{safe_name}.parquet"

        # Write to disk using the pyarrow engine (which we installed earlier)
        # We explicitly set index=False because the Pandas index is usually meaningless
        # for our time-series and just wastes disk space.
        lc_data.data.to_parquet(file_path, engine="pyarrow", index=False)

        return file_path
