import pandas as pd
import pytest

from src.eda.phase_folder import PhaseFolding


class TestPhaseFoldingFold:
    def test_returns_dataframe(self, sample_lightcurve_df, known_period, known_t0):
        result = PhaseFolding(sample_lightcurve_df).fold(known_period, known_t0)
        assert isinstance(result, pd.DataFrame)

    def test_output_has_phase_column(
        self, sample_lightcurve_df, known_period, known_t0
    ):
        result = PhaseFolding(sample_lightcurve_df).fold(known_period, known_t0)
        assert "phase" in result.columns

    def test_output_has_flux_column(self, sample_lightcurve_df, known_period, known_t0):
        result = PhaseFolding(sample_lightcurve_df).fold(known_period, known_t0)
        assert "flux" in result.columns

    def test_no_data_loss(self, sample_lightcurve_df, known_period, known_t0):
        result = PhaseFolding(sample_lightcurve_df).fold(known_period, known_t0)
        assert len(result) == len(sample_lightcurve_df)

    def test_phase_lower_bound(self, sample_lightcurve_df, known_period, known_t0):
        result = PhaseFolding(sample_lightcurve_df).fold(known_period, known_t0)
        assert result["phase"].min() >= -0.5

    def test_phase_upper_bound(self, sample_lightcurve_df, known_period, known_t0):
        result = PhaseFolding(sample_lightcurve_df).fold(known_period, known_t0)
        assert result["phase"].max() <= 0.5

    def test_epoch_maps_to_phase_zero(
        self, sample_lightcurve_df, known_period, known_t0
    ):
        """The data point nearest t0 must have a phase closest to 0."""
        result = PhaseFolding(sample_lightcurve_df).fold(known_period, known_t0)
        idx = (sample_lightcurve_df["time"] - known_t0).abs().idxmin()
        assert abs(result.loc[idx, "phase"]) < 0.01

    def test_raises_on_zero_period(self, sample_lightcurve_df):
        with pytest.raises(ValueError, match="period"):
            PhaseFolding(sample_lightcurve_df).fold(period=0.0, t0=0.0)

    def test_raises_on_negative_period(self, sample_lightcurve_df):
        with pytest.raises(ValueError, match="period"):
            PhaseFolding(sample_lightcurve_df).fold(period=-3.0, t0=0.0)
