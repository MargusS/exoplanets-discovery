from unittest.mock import MagicMock

import pandas as pd

from src.ingestion.models import LightCurveData
from src.ingestion.provider import MASTProvider


def test_fetch_lightcurve_success(mocker):
    """
    Test that MASTProvider correctly fetches, cleans, and formats a light curve.
    'mocker' is a fixture provided automatically by pytest-mock.
    """
    target_id = "KIC 123"

    # 1. Create the fake DataFrame that the API *would* return
    fake_df = pd.DataFrame(
        {
            "time": [1.0, 2.0, 3.0],
            "pdcsap_flux": [
                100.5,
                None,
                99.8,
            ],  # We inject a None (NaN) to test cleaning
        }
    )

    # 2. Build the chain of Mocks
    mock_stitched = MagicMock()
    mock_stitched.to_pandas.return_value = fake_df

    mock_collection = MagicMock()
    mock_collection.stitch.return_value = mock_stitched

    mock_search_result = MagicMock()
    mock_search_result.download_all.return_value = mock_collection

    # 3. Patch the actual lightkurve search function
    # Whenever src.ingestion.provider calls lightkurve.search_lightcurve,
    # it will return our mock_search_result instead of hitting the internet.
    mock_search = mocker.patch("src.ingestion.provider.lk.search_lightcurve")
    mock_search.return_value = mock_search_result

    # 4. Execute the code under test
    provider = MASTProvider(author="Kepler", exptime=1800)
    result = provider.fetch_lightcurve(target_id)

    # 5. Assertions
    # Verify the API was called with the right arguments
    mock_search.assert_called_once_with(target_id, author="Kepler", exptime=1800)

    # Verify the resulting object is exactly what we expect
    assert isinstance(result, LightCurveData)
    assert result.target_id == target_id

    # The original DataFrame had 3 rows, but one had a NaN flux.
    # Our provider MUST drop it, so the final data should only have 2 rows.
    assert len(result.data) == 2
    assert "time" in result.data.columns
    assert "flux" in result.data.columns
