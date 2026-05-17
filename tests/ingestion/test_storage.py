from pathlib import Path

import pandas as pd

from src.ingestion.models import LightCurveData
from src.ingestion.storage import StorageManager


def test_save_to_parquet_success(tmp_path: Path):
    """
    Test that the StorageManager correctly serializes a LightCurveData
    object to a Parquet file in the specified directory.
    'tmp_path' is a pytest fixture that provides a temporary directory unique to this test.
    """
    # 1. Arrange: Create the dummy data and the manager
    df = pd.DataFrame({"time": [1.0, 2.0], "flux": [100.0, 99.5]})
    lc_data = LightCurveData(target_id="KIC 12345", data=df)

    # We point the manager to the temporary test directory, not 'data/processed'
    manager = StorageManager(output_dir=tmp_path)

    # 2. Act: Save the data
    saved_path = manager.save_to_parquet(lc_data)

    # 3. Assert: Verify the file system state
    assert saved_path.exists()
    assert saved_path.suffix == ".parquet"
    assert (
        saved_path.name == "kic_12345.parquet"
    )  # It should sanitize the filename (lowercase, spaces to underscores)

    # 4. Assert: Verify Data Integrity (Idempotency)
    # Read the file back from disk and ensure no data was corrupted during serialization
    loaded_df = pd.read_parquet(saved_path)
    assert len(loaded_df) == 2
    assert "time" in loaded_df.columns
    assert "flux" in loaded_df.columns
    assert loaded_df["flux"].iloc[0] == 100.0
