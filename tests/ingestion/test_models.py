import pandas as pd
import pytest
from pydantic import ValidationError

from src.ingestion.models import LightCurveData


def test_valid_lightcurve_data_creation():
    """Happy path: testing a valid LightCurveData."""
    valid_df = pd.DataFrame({"time": [1.0, 2.0, 3.0], "flux": [100.5, 100.2, 99.8]})

    # Esto no debería lanzar ninguna excepción
    lc = LightCurveData(target_id="KIC 123", data=valid_df)

    assert lc.target_id == "KIC 123"
    assert len(lc.data) == 3


def test_missing_columns_raises_error():
    """Happy path: testing that missing required columns raise an error."""
    invalid_df = pd.DataFrame(
        {
            "time": [1.0, 2.0],
            "wrong_column": [100.5, 100.2],  # Falta 'flux'
        }
    )

    # pytest.raises es el equivalente a assertThrows en JUnit
    with pytest.raises(ValidationError) as exc_info:
        LightCurveData(target_id="KIC 123", data=invalid_df)

    assert "The dataframe must have columns 'time' and 'flux'" in str(exc_info.value)


def test_empty_dataframe_raises_error():
    """Happy path: testing that an empty DataFrame raises an error."""
    empty_df = pd.DataFrame(columns=["time", "flux"])

    with pytest.raises(ValidationError) as exc_info:
        LightCurveData(target_id="KIC 123", data=empty_df)

    assert "The dataframe cannot be empty" in str(exc_info.value)
