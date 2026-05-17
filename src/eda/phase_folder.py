import pandas as pd


class PhaseFolding:
    """
    Wraps lightkurve.LightCurve.fold() and returns a clean pd.DataFrame.
    Keeps lightkurve as an implementation detail — callers see only pandas.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def fold(self, period: float, t0: float) -> pd.DataFrame:

        if period <= 0:
            raise ValueError(f"period must be positive. Got: {period}")

        time = self.df["time"].to_numpy()

        phase = ((time - t0) % period) / period  # [0.0, 1.0)

        phase[phase > 0.5] -= 1.0  # shift to [-0.5, 0.5)

        return pd.DataFrame(
            {"phase": phase, "flux": self.df["flux"].to_numpy()},
            index=self.df.index,
        )
