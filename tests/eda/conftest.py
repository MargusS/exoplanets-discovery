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


@pytest.fixture
def sample_df_with_gap_and_outliers() -> pd.DataFrame:
    """
    DataFrame with two Quarters separated by a gap, plus some outliers.
    Quarter 1: days 0-10, median ~1.0 (normal behavior)
    Quarter 2: days 20-30, median ~0.96 (instrumental drift)
    Outliers: 3 points at 0.90
    """
    rng = np.random.default_rng(seed=99)

    time_q1 = np.linspace(0, 10, 100)
    flux_q1 = rng.normal(loc=1.0, scale=0.002, size=100)

    time_q2 = np.linspace(20, 30, 100)
    flux_q2 = rng.normal(loc=0.96, scale=0.002, size=100)

    time_out = np.array([5.0, 6.0, 25.0])
    flux_out = np.array([0.90, 0.90, 0.90])

    time = np.concatenate([time_q1, time_q2, time_out])
    flux = np.concatenate([flux_q1, flux_q2, flux_out])

    idx = np.argsort(time)
    return pd.DataFrame({"time": time[idx], "flux": flux[idx]})
