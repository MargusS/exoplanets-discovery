import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LightCurveData(BaseModel):
    #  Pydantic configuration to allow arbitrary types (like pd.DataFrame) without validation errors.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    target_id: str = Field(..., description="Astronomical object ID, ej. 'KIC 3733346'")
    data: pd.DataFrame = Field(
        ..., description="DataFrame with required columns: 'time', 'flux'"
    )

    @field_validator("data")
    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:

        if df.empty:
            # Pydantic raises ValidationError, but we can raise a ValueError which will be caught and re-raised as a ValidationError by Pydantic.
            raise ValueError("The dataframe cannot be empty.")

        # 2. Validate that the required columns are present
        required_columns = {"time", "flux"}
        if not required_columns.issubset(df.columns):
            raise ValueError(
                f"The dataframe must have columns 'time' and 'flux'. Current columns: {list(df.columns)}"
            )

        return df


#
