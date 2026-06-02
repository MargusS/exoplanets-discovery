import numpy as np
import pandas as pd
import pytest

from src.eda.preprocessor import Preprocessor


class TestDetectQuarters:
    def test_returns_list(self, sample_df_with_gap_and_outliers):
        quarters = Preprocessor(sample_df_with_gap_and_outliers).detect_quarters()
        assert isinstance(quarters, list)

    def test_detects_two_quarters(self, sample_df_with_gap_and_outliers):
        quarters = Preprocessor(sample_df_with_gap_and_outliers).detect_quarters()
        assert len(quarters) == 2

    def test_each_quarter_is_dataframe(self, sample_df_with_gap_and_outliers):
        quarters = Preprocessor(sample_df_with_gap_and_outliers).detect_quarters()
        assert all(isinstance(q, pd.DataFrame) for q in quarters)

    def test_quarters_cover_all_rows(self, sample_df_with_gap_and_outliers):
        quarters = Preprocessor(sample_df_with_gap_and_outliers).detect_quarters()
        total = sum(len(q) for q in quarters)
        assert total == len(sample_df_with_gap_and_outliers)

    def test_no_gap_produces_one_quarter(self, sample_lightcurve_df):
        quarters = Preprocessor(sample_lightcurve_df).detect_quarters()
        assert len(quarters) == 1

    def test_time_is_monotonic_within_each_quarter(
        self, sample_df_with_gap_and_outliers
    ):
        quarters = Preprocessor(sample_df_with_gap_and_outliers).detect_quarters()
        for q in quarters:
            assert q["time"].is_monotonic_increasing


class TestNormalizeQuarters:
    def test_returns_dataframe(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        quarters = p.detect_quarters()
        result = p.normalize_quarters(quarters)
        assert isinstance(result, pd.DataFrame)

    def test_output_has_same_columns(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.normalize_quarters(p.detect_quarters())
        assert "time" in result.columns
        assert "flux" in result.columns

    def test_output_has_same_row_count(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.normalize_quarters(p.detect_quarters())
        assert len(result) == len(sample_df_with_gap_and_outliers)

    def test_each_quarter_median_near_one(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.normalize_quarters(p.detect_quarters())
        quarters_after = Preprocessor(result).detect_quarters()
        for q in quarters_after:
            assert abs(q["flux"].median() - 1.0) < 0.01

    def test_time_column_unchanged(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.normalize_quarters(p.detect_quarters())
        np.testing.assert_array_equal(
            result["time"].values, sample_df_with_gap_and_outliers["time"].values
        )


class TestRemoveOutliers:
    def test_returns_dataframe(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.remove_outliers(sample_df_with_gap_and_outliers)
        assert isinstance(result, pd.DataFrame)

    def test_removes_points_below_threshold(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.remove_outliers(sample_df_with_gap_and_outliers, threshold=0.05)
        assert (result["flux"] >= 0.95).all()

    def test_removes_points_above_threshold(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.remove_outliers(sample_df_with_gap_and_outliers, threshold=0.05)
        assert (result["flux"] <= 1.05).all()

    def test_output_has_fewer_rows_than_input(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        result = p.remove_outliers(sample_df_with_gap_and_outliers, threshold=0.05)
        assert len(result) < len(sample_df_with_gap_and_outliers)

    def test_raises_on_invalid_threshold(self, sample_df_with_gap_and_outliers):
        p = Preprocessor(sample_df_with_gap_and_outliers)
        with pytest.raises(ValueError, match="threshold"):
            p.remove_outliers(sample_df_with_gap_and_outliers, threshold=0.0)

    def test_clean_data_unchanged(self, sample_lightcurve_df):
        """Datos sin outliers extremos no deben perder filas con threshold generoso."""
        p = Preprocessor(sample_lightcurve_df)
        result = p.remove_outliers(sample_lightcurve_df, threshold=0.10)
        assert len(result) == len(sample_lightcurve_df)


class TestPreprocess:
    def test_returns_dataframe(self, sample_df_with_gap_and_outliers):
        result = Preprocessor(sample_df_with_gap_and_outliers).preprocess()
        assert isinstance(result, pd.DataFrame)

    def test_output_has_fewer_rows_than_input(self, sample_df_with_gap_and_outliers):
        result = Preprocessor(sample_df_with_gap_and_outliers).preprocess()
        assert len(result) < len(sample_df_with_gap_and_outliers)

    def test_flux_median_near_one(self, sample_df_with_gap_and_outliers):
        result = Preprocessor(sample_df_with_gap_and_outliers).preprocess()
        assert abs(result["flux"].median() - 1.0) < 0.01

    def test_no_extreme_outliers_remain(self, sample_df_with_gap_and_outliers):
        result = Preprocessor(sample_df_with_gap_and_outliers).preprocess()
        assert (result["flux"] >= 0.95).all()
        assert (result["flux"] <= 1.05).all()

    def test_output_preserves_time_order(self, sample_df_with_gap_and_outliers):
        result = Preprocessor(sample_df_with_gap_and_outliers).preprocess()
        assert result["time"].is_monotonic_increasing

    def test_output_has_required_columns(self, sample_df_with_gap_and_outliers):
        result = Preprocessor(sample_df_with_gap_and_outliers).preprocess()
        assert "time" in result.columns
        assert "flux" in result.columns
