import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_lightcurve_df() -> pd.DataFrame:
    """
    500-point synthetic light curve with a deterministic injected transit.
    Period: 5.0 days, transit depth: 1%, duration: 0.5 days, t0: 2.5.
    Uses a fixed seed for full reproducibility.
    """
    rng = np.random.default_rng(seed=42)
    n = 500
    time = np.linspace(0, 30.0, n)
    flux = rng.normal(loc=1.0, scale=0.001, size=n)

    PERIOD, T0, DEPTH, DURATION = 5.0, 2.5, 0.01, 0.5
    phase = (time - T0) % PERIOD
    in_transit = (phase < DURATION) | (phase > PERIOD - DURATION)
    flux[in_transit] -= DEPTH

    return pd.DataFrame({"time": time, "flux": flux})


@pytest.fixture
def known_period() -> float:
    return 5.0


@pytest.fixture
def known_t0() -> float:
    return 2.5
