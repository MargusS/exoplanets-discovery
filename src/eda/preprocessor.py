import pandas as pd


class Preprocessor:
    def __init__(self, df: pd.DataFrame):
        if "time" not in df.columns or "flux" not in df.columns:
            raise ValueError("Input DataFrame must contain 'time' and 'flux' columns")
        if df["time"].isnull().any():
            raise ValueError(
                "The 'time' column contains NaN values. Please remove or impute them before preprocessing."
            )
        if df["flux"].isnull().any():
            raise ValueError(
                "The 'flux' column contains NaN values. Please remove or impute them before preprocessing."
            )

        self.df = df.sort_values(by="time").reset_index(drop=True)

    def preprocess(self) -> pd.DataFrame:
        if self.df.empty:
            raise ValueError("Input DataFrame is empty")

        list_quarters = self.detect_quarters()
        normalized_df = self.normalize_quarters(list_quarters)
        return self.remove_outliers(normalized_df)

    def detect_quarters(self, gap_threshold: float = 1.0) -> list[pd.DataFrame]:
        if gap_threshold <= 0:
            raise ValueError("gap_threshold must be a positive number")

        list_quarters = list()

        diff_time = self.df["time"].diff()
        index_quarters = diff_time[diff_time > gap_threshold].index.tolist()
        index_quarters.insert(0, 0)
        index_quarters.append(len(self.df))

        for i in range(1, len(index_quarters)):
            start_idx = index_quarters[i - 1]
            end_idx = index_quarters[i]
            quarter_df = self.df.iloc[start_idx:end_idx]
            list_quarters.append(quarter_df)

        return list_quarters

    def normalize_quarters(self, quarters: list[pd.DataFrame]) -> pd.DataFrame:
        for quarter in quarters:
            median_flux = quarter["flux"].median()
            if median_flux == 0:
                quarter["flux"] = 0.0
            else:
                quarter["flux"] /= median_flux
        normalized_df = pd.concat(quarters, ignore_index=True)
        return normalized_df

    def remove_outliers(
        self, df: pd.DataFrame, threshold: float = 0.05
    ) -> pd.DataFrame:
        if threshold <= 0:
            raise ValueError("threshold must be a positive number")
        lower_bound = 1.0 - threshold
        upper_bound = 1.0 + threshold
        return df[(df["flux"] >= lower_bound) & (df["flux"] <= upper_bound)]
