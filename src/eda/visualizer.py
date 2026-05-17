import pandas as pd
import plotly.graph_objects as go


class Visualizer:
    """
    Produces interactive Plotly figures from a validated light curve DataFrame.
    Stateful: holds the raw DataFrame provided at construction.
    Does NOT perform I/O or data transformations internally.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Parameters
        ----------
        df : pd.DataFrame
            Must contain 'time' and 'flux' columns. Must not be empty.

        Raises
        ------
        ValueError
            If 'time' or 'flux' columns are absent, or if the DataFrame is empty.
        """
        ...

    def plot_raw_lightcurve(
        self,
        title: str = "Raw Light Curve",
        downsample_factor: int = 1,
    ) -> go.Figure:
        """
        Plot flux vs. time as a single Scatter trace.

        Parameters
        ----------
        title : str
            Figure title, set on fig.layout.title.text.
        downsample_factor : int
            If > 1, keeps every Nth row (df.iloc[::downsample_factor]).
            Must be >= 1; raises ValueError otherwise.

        Returns
        -------
        go.Figure
            Single trace. X-axis labeled 'Time (BKJD days)',
            Y-axis labeled 'Normalized Flux'.
        """
        ...

    def plot_phase_folded(
        self,
        period: float,
        t0: float,
        title: str = "Phase-Folded Light Curve",
    ) -> go.Figure:
        """
        Phase-fold the stored light curve and plot phase vs. flux.

        Internally instantiates PhaseFolding(self._df).fold(period, t0).
        Phase range is normalized to [-0.5, 0.5].

        Parameters
        ----------
        period : float
            Orbital period in days. Forwarded to PhaseFolding.fold().
        t0 : float
            Reference epoch in days. Forwarded to PhaseFolding.fold().
        title : str
            Figure title.

        Returns
        -------
        go.Figure
            Single trace. X-axis labeled 'Phase', Y-axis labeled 'Normalized Flux'.
            Point count equals len(self._df).

        Raises
        ------
        ValueError
            If period <= 0 (propagated from PhaseFolding).
        """
        ...

    def plot_flux_histogram(
        self,
        nbins: int = 50,
        title: str = "Flux Distribution",
    ) -> go.Figure:
        """
        Plot a histogram of flux values to surface outliers and baseline drift.

        Parameters
        ----------
        nbins : int
            Number of bins. Must be >= 1.
        title : str
            Figure title.

        Returns
        -------
        go.Figure
            Single Histogram trace. X-axis labeled 'Normalized Flux',
            Y-axis labeled 'Count'.

        Raises
        ------
        ValueError
            If nbins < 1.
        """
        ...
