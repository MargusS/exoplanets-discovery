import pandas as pd
import pytest

from src.eda.loader import EDALoader


class TestEDALoaderInit:
    def test_stores_path_attribute(self, tmp_path):
        path = tmp_path / "star.parquet"
        loader = EDALoader(path)
        assert loader.path == path


class TestEDALoaderLoad:
    def test_returns_dataframe(self, tmp_path, sample_lightcurve_df):
        p = tmp_path / "star.parquet"
        sample_lightcurve_df.to_parquet(p, index=False)
        assert isinstance(EDALoader(p).load(), pd.DataFrame)

    def test_loaded_df_has_time_column(self, tmp_path, sample_lightcurve_df):
        p = tmp_path / "star.parquet"
        sample_lightcurve_df.to_parquet(p, index=False)
        assert "time" in EDALoader(p).load().columns

    def test_loaded_df_has_flux_column(self, tmp_path, sample_lightcurve_df):
        p = tmp_path / "star.parquet"
        sample_lightcurve_df.to_parquet(p, index=False)
        assert "flux" in EDALoader(p).load().columns

    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            EDALoader(tmp_path / "ghost.parquet").load()

    def test_raises_on_missing_time_column(self, tmp_path):
        bad = pd.DataFrame({"flux": [1.0, 0.99]})
        p = tmp_path / "bad.parquet"
        bad.to_parquet(p, index=False)
        with pytest.raises(ValueError, match="time"):
            EDALoader(p).load()

    def test_raises_on_missing_flux_column(self, tmp_path):
        bad = pd.DataFrame({"time": [0.0, 1.0]})
        p = tmp_path / "bad.parquet"
        bad.to_parquet(p, index=False)
        with pytest.raises(ValueError, match="flux"):
            EDALoader(p).load()

    def test_raises_on_empty_dataframe(self, tmp_path):
        empty = pd.DataFrame({"time": [], "flux": []})
        p = tmp_path / "empty.parquet"
        empty.to_parquet(p, index=False)
        with pytest.raises(ValueError, match="empty"):
            EDALoader(p).load()
