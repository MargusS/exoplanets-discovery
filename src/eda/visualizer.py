import pandas as pd
import plotly.graph_objects as go

from src.eda.phase_folder import PhaseFolding


class Visualizer:
    """
    Produces interactive Plotly figures from a validated light curve DataFrame.
    Stateful: holds the raw DataFrame provided at construction.
    Does NOT perform I/O or data transformations internally.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("DataFrame must not be empty.")
        if "time" not in df.columns:
            raise ValueError("DataFrame must contain a 'time' column.")
        if "flux" not in df.columns:
            raise ValueError("DataFrame must contain a 'flux' column.")
        self._df = df
        self._df["flux"] = _normalize_flux(self._df["flux"])

    # Plotting raw light curve with optional downsampling for performance
    def plot_raw_lightcurve(
        self,
        title: str = "Raw Light Curve",
        downsample_factor: int = 1,
    ) -> go.Figure:

        if downsample_factor < 1:
            raise ValueError("downsample_factor must be >= 1.")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self._df["time"].iloc[::downsample_factor],
                y=self._df["flux"].iloc[::downsample_factor],
                mode="markers",
            )
        )
        fig.update_layout(title_text=title)
        fig.update_xaxes(title_text="Time (BKJD days)")
        fig.update_yaxes(title_text="Normalized Flux")
        return fig

    # Plotting phase-folded light curve to reveal periodic signals, using known period and t0 for Kepler-10b
    def plot_phase_folded(
        self,
        period: float,
        t0: float,
        title: str = "Phase-Folded Light Curve",
    ) -> go.Figure:

        folded_df = PhaseFolding(self._df).fold(period, t0)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=folded_df["phase"],
                y=folded_df["flux"],
                mode="markers",
            )
        )
        fig.update_layout(title_text=title)
        fig.update_xaxes(title_text="Phase")
        fig.update_yaxes(title_text="Normalized Flux")
        return fig

    # Plotting flux histogram to visualize distribution and noise characteristics
    def plot_flux_histogram(
        self,
        nbins: int = 50,
        title: str = "Flux Distribution",
    ) -> go.Figure:
        if nbins < 1:
            raise ValueError("nbins must be >= 1.")
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=self._df["flux"],
                nbinsx=nbins,
            )
        )
        fig.update_layout(title_text=title)
        fig.update_xaxes(title_text="Normalized Flux")
        fig.update_yaxes(title_text="Count")
        return fig


def _normalize_flux(flux: pd.Series) -> pd.Series:
    median_flux = flux.median()
    if median_flux == 0:
        raise ValueError("Median flux is zero, cannot normalize.")
    return flux / median_flux
