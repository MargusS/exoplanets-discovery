# import numpy as np
# import pandas as pd
# import plotly.graph_objects as go
# import pytest

# from src.eda.visualizer import Visualizer


# class TestVisualizerInit:
#     def test_raises_on_missing_time_column(self, sample_lightcurve_df):
#         with pytest.raises(ValueError, match="time"):
#             Visualizer(sample_lightcurve_df.drop(columns=["time"]))

#     def test_raises_on_missing_flux_column(self, sample_lightcurve_df):
#         with pytest.raises(ValueError, match="flux"):
#             Visualizer(sample_lightcurve_df.drop(columns=["flux"]))

#     def test_raises_on_empty_dataframe(self):
#         with pytest.raises(ValueError, match="empty"):
#             Visualizer(pd.DataFrame({"time": [], "flux": []}))


# class TestPlotRawLightcurve:
#     def test_returns_go_figure(self, sample_lightcurve_df):
#         assert isinstance(
#             Visualizer(sample_lightcurve_df).plot_raw_lightcurve(), go.Figure
#         )

#     def test_exactly_one_trace(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_raw_lightcurve()
#         assert len(fig.data) == 1

#     def test_trace_x_equals_time_values(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_raw_lightcurve()
#         np.testing.assert_array_equal(
#             fig.data[0].x, sample_lightcurve_df["time"].values
#         )

#     def test_trace_y_equals_flux_values(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_raw_lightcurve()
#         np.testing.assert_array_equal(
#             fig.data[0].y, sample_lightcurve_df["flux"].values
#         )

#     def test_xaxis_label_contains_time(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_raw_lightcurve()
#         assert "time" in fig.layout.xaxis.title.text.lower()

#     def test_yaxis_label_contains_flux(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_raw_lightcurve()
#         assert "flux" in fig.layout.yaxis.title.text.lower()

#     def test_custom_title_is_applied(self, sample_lightcurve_df):
#         custom = "Kepler-10b Photometry"
#         fig = Visualizer(sample_lightcurve_df).plot_raw_lightcurve(title=custom)
#         assert fig.layout.title.text == custom

#     def test_downsample_reduces_point_count(self, sample_lightcurve_df):
#         viz = Visualizer(sample_lightcurve_df)
#         full = viz.plot_raw_lightcurve(downsample_factor=1)
#         down = viz.plot_raw_lightcurve(downsample_factor=5)
#         assert len(down.data[0].x) < len(full.data[0].x)

#     def test_downsample_factor_one_preserves_all_points(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_raw_lightcurve(downsample_factor=1)
#         assert len(fig.data[0].x) == len(sample_lightcurve_df)

#     def test_raises_on_invalid_downsample_factor(self, sample_lightcurve_df):
#         with pytest.raises(ValueError):
#             Visualizer(sample_lightcurve_df).plot_raw_lightcurve(downsample_factor=0)


# class TestPlotPhaseFolded:
#     def test_returns_go_figure(self, sample_lightcurve_df, known_period, known_t0):
#         assert isinstance(
#             Visualizer(sample_lightcurve_df).plot_phase_folded(known_period, known_t0),
#             go.Figure,
#         )

#     def test_exactly_one_trace(self, sample_lightcurve_df, known_period, known_t0):
#         fig = Visualizer(sample_lightcurve_df).plot_phase_folded(known_period, known_t0)
#         assert len(fig.data) == 1

#     def test_trace_point_count_matches_input(
#         self, sample_lightcurve_df, known_period, known_t0
#     ):
#         fig = Visualizer(sample_lightcurve_df).plot_phase_folded(known_period, known_t0)
#         assert len(fig.data[0].x) == len(sample_lightcurve_df)

#     def test_phase_values_lower_bound(
#         self, sample_lightcurve_df, known_period, known_t0
#     ):
#         fig = Visualizer(sample_lightcurve_df).plot_phase_folded(known_period, known_t0)
#         assert np.all(np.array(fig.data[0].x) >= -0.5)

#     def test_phase_values_upper_bound(
#         self, sample_lightcurve_df, known_period, known_t0
#     ):
#         fig = Visualizer(sample_lightcurve_df).plot_phase_folded(known_period, known_t0)
#         assert np.all(np.array(fig.data[0].x) <= 0.5)

#     def test_xaxis_label_contains_phase(
#         self, sample_lightcurve_df, known_period, known_t0
#     ):
#         fig = Visualizer(sample_lightcurve_df).plot_phase_folded(known_period, known_t0)
#         assert "phase" in fig.layout.xaxis.title.text.lower()

#     def test_custom_title_is_applied(
#         self, sample_lightcurve_df, known_period, known_t0
#     ):
#         fig = Visualizer(sample_lightcurve_df).plot_phase_folded(
#             known_period, known_t0, title="Kepler-10b Phase Fold"
#         )
#         assert fig.layout.title.text == "Kepler-10b Phase Fold"

#     def test_raises_on_non_positive_period(self, sample_lightcurve_df):
#         with pytest.raises(ValueError, match="period"):
#             Visualizer(sample_lightcurve_df).plot_phase_folded(period=0.0, t0=0.0)


# class TestPlotFluxHistogram:
#     def test_returns_go_figure(self, sample_lightcurve_df):
#         assert isinstance(
#             Visualizer(sample_lightcurve_df).plot_flux_histogram(), go.Figure
#         )

#     def test_exactly_one_trace(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_flux_histogram()
#         assert len(fig.data) == 1

#     def test_trace_is_histogram_type(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_flux_histogram()
#         assert isinstance(fig.data[0], go.Histogram)

#     def test_xaxis_label_contains_flux(self, sample_lightcurve_df):
#         fig = Visualizer(sample_lightcurve_df).plot_flux_histogram()
#         assert "flux" in fig.layout.xaxis.title.text.lower()

#     def test_raises_on_zero_nbins(self, sample_lightcurve_df):
#         with pytest.raises(ValueError):
#             Visualizer(sample_lightcurve_df).plot_flux_histogram(nbins=0)
