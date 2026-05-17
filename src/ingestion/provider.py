from abc import ABC, abstractmethod

import lightkurve as lk

from .models import LightCurveData


class BaseProvider(ABC):
    """Abstract interface for astronomical data retrieval."""

    @abstractmethod
    def fetch_lightcurve(self, target_id: str) -> LightCurveData:
        pass


class MASTProvider(BaseProvider):
    """Concrete implementation consuming the NASA MAST API via lightkurve."""

    def __init__(self, author: str = "Kepler", exptime: int = 1800):
        self.author = author
        self.exptime = exptime

    def fetch_lightcurve(self, target_id: str) -> LightCurveData:
        # 1. Search the MAST archive
        search_result = lk.search_lightcurve(
            target_id, author=self.author, exptime=self.exptime
        )

        if not search_result:
            raise ValueError(f"No light curve data found for target: {target_id}")

        # 2. Download all quarters and stitch them together
        lc_collection = search_result.download_all()
        lc_stitched = lc_collection.stitch()

        # 3. Convert to Pandas DataFrame
        df_raw = lc_stitched.to_pandas()

        # lightkurve sets 'time' as the index. We need it as a regular column.
        # reset_index() moves the index back into the dataframe as a column named 'time'
        if df_raw.index.name == "time":
            df_raw = df_raw.reset_index()

        # 4. Data Cleaning (Crucial for ML)
        if "pdcsap_flux" not in df_raw.columns:
            raise ValueError(f"Missing 'pdcsap_flux' in data for {target_id}")

        # Now 'time' is guaranteed to be a column, so this will work:
        df_cleaned = df_raw[["time", "pdcsap_flux"]].rename(
            columns={"pdcsap_flux": "flux"}
        )

        # Drop any rows where time or flux is NaN
        df_cleaned = df_cleaned.dropna()

        # 5. Return the validated domain model
        return LightCurveData(target_id=target_id, data=df_cleaned)
