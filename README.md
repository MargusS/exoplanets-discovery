# 🔭 Exoplanets Discovery

A production-grade **astronomical data ingestion and exploratory analysis pipeline** that fetches, validates, stores, and visualizes stellar light curve data from NASA's MAST archive — the raw photometric signal used to detect exoplanets via the **transit method**.

This is a **bridge project** in the Deep Tech / Applied AI track, focused on building robust data infrastructure and signal analysis tooling over real-world scientific data as a precursor to ML-based transit detection.

---

## Architecture Overview

The system is structured in two independent, composable layers:

```
main.py
└── [Layer 1] IngestionPipeline (ETL orchestrator)
    ├── BaseProvider (abstract interface)
    │   └── MASTProvider      → fetches from NASA MAST via lightkurve
    └── StorageManager        → serializes to Parquet

src/eda/
└── [Layer 2] EDA (read-only analysis on stored data)
    ├── EDALoader             → loads & validates Parquet files
    ├── PhaseFolding          → folds time series onto orbital period
    └── Visualizer            → produces interactive Plotly figures
```

**Key design decisions:**
- **Dependency Injection**: `IngestionPipeline` depends on the `BaseProvider` abstraction, not the concrete `MASTProvider`. Swapping to a local disk provider or a mock requires zero changes to business logic.
- **Layer decoupling**: The EDA layer is strictly read-only and stateless with respect to ingestion. `EDALoader` reads from Parquet; it has no knowledge of how that data was produced.
- **Pydantic data contracts**: The `LightCurveData` model enforces structural and domain-level validation (non-empty DataFrame, required `time`/`flux` columns) at ingestion time — catching data corruption before it propagates downstream.
- **Resilience via Tenacity**: Each target fetch is wrapped in an exponential backoff retry decorator (up to 3 attempts: 2s → 4s → 8s), handling transient network failures gracefully.
- **Structured error handling**: `ValueError` (target not found) and `ValidationError` (corrupted data) are handled distinctly — so a single bad target never aborts the full batch.

---

## Project Structure

```
exoplanets-discovery/
├── main.py                      # Application entry point
├── pyproject.toml               # Project metadata and dependencies (uv)
├── data/
│   └── processed/               # Output directory for ingested Parquet files
├── src/
│   ├── ingestion/               # Layer 1: ETL pipeline
│   │   ├── models.py            # Pydantic domain model (LightCurveData)
│   │   ├── provider.py          # BaseProvider ABC + MASTProvider implementation
│   │   ├── pipeline.py          # IngestionPipeline: batch orchestration + retry logic
│   │   └── storage.py           # StorageManager: Parquet serialization
│   └── eda/                     # Layer 2: Exploratory Data Analysis (v1)
│       ├── loader.py            # EDALoader: Parquet loading + schema validation
│       ├── phase_folder.py      # PhaseFolding: orbital period folding
│       └── visualizer.py        # Visualizer: raw curve, phase fold, flux histogram
└── tests/                       # Pytest test suite
```

---

## Data Model

The central domain object is `LightCurveData`, a Pydantic model representing a validated, cleaned time series for a single stellar target:

| Field | Type | Description |
|---|---|---|
| `target_id` | `str` | Astronomical identifier (e.g., `"Kepler-10"`) |
| `data` | `pd.DataFrame` | Cleaned time series with columns `time` and `flux` |

The `flux` column corresponds to **PDCSAP flux** (Pre-search Data Conditioning Simple Aperture Photometry) — photometric flux corrected for systematic errors, which is the standard signal used for transit detection. The EDA layer further normalizes flux by its median, producing a dimensionless ratio centred around `1.0`, where transits appear as dips below that baseline.

---

## EDA Layer — v1

The `src/eda/` module provides three composable components designed to be used sequentially:

### `EDALoader`
Loads a Parquet file produced by the ingestion pipeline and enforces schema integrity before returning the DataFrame. Raises `FileNotFoundError`, `ValueError` on empty files or schema mismatches.

```python
from pathlib import Path
from src.eda.loader import EDALoader

df = EDALoader(Path("data/processed/Kepler-10.parquet")).load()
```

### `Visualizer`
Stateful class that wraps a validated DataFrame and exposes three plot methods. Flux normalization (division by median) is applied once at construction — all plots share the same normalized signal.

| Method | Description | Key Parameter |
|---|---|---|
| `plot_raw_lightcurve()` | Full time series scatter plot | `downsample_factor` for performance |
| `plot_phase_folded()` | Folds time axis onto orbital period | `period` (days), `t0` (reference epoch) |
| `plot_flux_histogram()` | Flux value distribution | `nbins` |

```python
from src.eda.visualizer import Visualizer

viz = Visualizer(df)
viz.plot_raw_lightcurve(title="Kepler-10 Raw Flux", downsample_factor=5).show()
viz.plot_phase_folded(period=0.8375, t0=2455700.5, title="Kepler-10b Transit").show()
viz.plot_flux_histogram(nbins=100).show()
```

### `PhaseFolding`
Performs orbital phase folding: maps timestamps onto the interval `[-0.5, 0.5)` relative to a known orbital period and reference epoch `t0`. The transformation applied is:

```
phase = ((time - t0) % period) / period   # → [0.0, 1.0)
phase[phase > 0.5] -= 1.0                 # → [-0.5, 0.5)
```

This collapses all observed transits onto a single dip centred at phase `0`, which is the standard representation used in transit photometry and the direct input for BLS periodogram analysis in Phase 3.

---

## Tech Stack

| Dependency | Role |
|---|---|
| [`lightkurve`](https://docs.lightkurve.org/) | NASA MAST API client; light curve download and stitching |
| [`pandas`](https://pandas.pydata.org/) | Time series manipulation and cleaning |
| [`pyarrow`](https://arrow.apache.org/docs/python/) | Parquet serialization engine |
| [`plotly`](https://plotly.com/python/) | Interactive visualization (EDA layer) |
| [`pydantic`](https://docs.pydantic.dev/) | Runtime data validation and domain modelling |
| [`tenacity`](https://tenacity.readthedocs.io/) | Retry logic with exponential backoff |
| [`pytest`](https://docs.pytest.org/) | Unit and integration testing |
| [`ruff`](https://docs.astral.sh/ruff/) | Linter and formatter |

---

## Getting Started

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

**1. Clone the repository and switch to `dev`:**
```bash
git clone https://github.com/MargusS/exoplanets-discovery.git
cd exoplanets-discovery
git checkout dev
```

**2. Install dependencies:**
```bash
uv sync
```

**3. Run the ingestion pipeline:**
```bash
uv run main.py
```

This fetches light curves for `Kepler-10` and `Kepler-186` from NASA MAST and saves them as Parquet files under `data/processed/`. `INVALID_STAR_999` is intentionally included to demonstrate graceful error handling.

**Expected output:**
```
2026-05-17 18:00:00 - ExoplanetApp - INFO - Initializing Exoplanet Data Ingestion System...
2026-05-17 18:00:01 - IngestionPipeline - INFO - Starting batch processing for 3 targets.
...
2026-05-17 18:00:30 - ExoplanetApp - INFO - === BATCH EXECUTION REPORT ===
2026-05-17 18:00:30 - ExoplanetApp - INFO - Successful targets: ['Kepler-10', 'Kepler-186']
2026-05-17 18:00:30 - ExoplanetApp - INFO - Failed targets: ['INVALID_STAR_999']
```

**4. Run EDA on ingested data:**
```python
from pathlib import Path
from src.eda.loader import EDALoader
from src.eda.visualizer import Visualizer

df = EDALoader(Path("data/processed/Kepler-10.parquet")).load()
viz = Visualizer(df)
viz.plot_raw_lightcurve(downsample_factor=5).show()
viz.plot_phase_folded(period=0.8375, t0=2455700.5).show()
```

---

## Running Tests

```bash
uv run pytest tests/ -v
```

---

## Roadmap

- [x] Phase 1 — Data Ingestion: resilient ETL pipeline with MAST integration
- [x] Phase 2 — EDA v1: light curve loading, normalization, phase folding, and interactive visualization
- [ ] Phase 3 — Feature Engineering: Box Least-Squares (BLS) periodogram, transit depth and duration extraction
- [ ] Phase 4 — ML Model: binary classifier for transit detection (confirmed planet vs. false positive)

---

## License

MIT — see [LICENSE](./LICENSE) for details.
