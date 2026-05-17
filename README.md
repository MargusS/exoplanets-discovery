# 🔭 Exoplanets Discovery

A production-grade **astronomical data ingestion pipeline** that fetches, validates, and stores stellar light curve data from NASA's MAST archive — the raw signal used to detect exoplanets via the **transit method**.

This is a **bridge project** in the Deep Tech / Applied AI track, focused on building robust data infrastructure over noisy, real-world scientific data as a precursor to ML-based transit detection.

---

## Architecture Overview

The system follows a clean **Extract → Transform → Load (ETL)** pattern with Dependency Injection at its core:

```
main.py
└── IngestionPipeline (orchestrator)
    ├── BaseProvider (abstract interface)
    │   └── MASTProvider (NASA MAST via lightkurve)
    └── StorageManager (Parquet serialization)
```

**Key design decisions:**
- **Dependency Injection**: `IngestionPipeline` depends on the `BaseProvider` abstraction, not the concrete `MASTProvider`. Swapping to a local disk provider or a mock for testing requires zero changes to business logic.
- **Pydantic data contracts**: The `LightCurveData` model enforces structural and domain-level validation (non-empty DataFrame, required `time`/`flux` columns) at ingestion time — catching data corruption before it propagates.
- **Resilience via Tenacity**: Each target fetch is wrapped in an exponential backoff retry decorator (up to 3 attempts), handling transient network failures gracefully without crashing the batch.
- **Structured error handling**: `ValueError` (target not found) and `ValidationError` (corrupted data) are handled distinctly — warnings vs. errors — so a single bad target does not abort the entire run.

---

## Project Structure

```
exoplanets-discovery/
├── main.py                    # Application entry point
├── pyproject.toml             # Project metadata and dependencies (uv)
├── data/
│   └── processed/             # Output directory for Parquet files
├── src/
│   ├── ingestion/
│   │   ├── models.py          # Pydantic domain model (LightCurveData)
│   │   ├── provider.py        # BaseProvider ABC + MASTProvider implementation
│   │   ├── pipeline.py        # IngestionPipeline: batch orchestration + retry logic
│   │   └── storage.py         # StorageManager: Parquet serialization
│   └── eda/                   # Exploratory Data Analysis (in progress)
└── tests/                     # Pytest test suite
```

---

## Data Model

The central domain object is `LightCurveData`, a Pydantic model representing a validated, cleaned time series for a single stellar target:

| Field | Type | Description |
|---|---|---|
| `target_id` | `str` | Astronomical identifier (e.g., `"Kepler-10"`) |
| `data` | `pd.DataFrame` | Cleaned time series with columns `time` and `flux` |

The `flux` column corresponds to **PDCSAP flux** (Pre-search Data Conditioning Simple Aperture Photometry) — the photometric flux corrected for systematic errors, which is the standard signal used for transit detection.

---

## Tech Stack

| Dependency | Role |
|---|---|
| [`lightkurve`](https://docs.lightkurve.org/) | NASA MAST API client; light curve download and stitching |
| [`pandas`](https://pandas.pydata.org/) | Time series manipulation and cleaning |
| [`pyarrow`](https://arrow.apache.org/docs/python/) | Parquet serialization engine |
| [`pydantic`](https://docs.pydantic.dev/) | Runtime data validation and domain modelling |
| [`tenacity`](https://tenacity.readthedocs.io/) | Retry logic with exponential backoff |
| [`pytest`](https://docs.pytest.org/) | Unit and integration testing |
| [`ruff`](https://docs.astral.sh/ruff/) | Linter and formatter |

---

## Getting Started

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

**1. Clone the repository:**
```bash
git clone https://github.com/MargusS/exoplanets-discovery.git
cd exoplanets-discovery
```

**2. Install dependencies:**
```bash
uv sync
```

**3. Run the ingestion pipeline:**
```bash
uv run main.py
```

This will fetch light curves for `Kepler-10` and `Kepler-186` from the NASA MAST archive and save them as Parquet files under `data/processed/`. The `INVALID_STAR_999` target is intentionally included to demonstrate graceful error handling.

**Expected output:**
```
2026-05-17 18:00:00 - ExoplanetApp - INFO - Initializing Exoplanet Data Ingestion System...
2026-05-17 18:00:01 - IngestionPipeline - INFO - Starting batch processing for 3 targets.
...
2026-05-17 18:00:30 - ExoplanetApp - INFO - === BATCH EXECUTION REPORT ===
2026-05-17 18:00:30 - ExoplanetApp - INFO - Successful targets: ['Kepler-10', 'Kepler-186']
2026-05-17 18:00:30 - ExoplanetApp - INFO - Failed targets: ['INVALID_STAR_999']
```

---

## Running Tests

```bash
uv run pytest tests/ -v
```

---

## Roadmap

- [x] Phase 1 — Data Ingestion: resilient ETL pipeline with MAST integration
- [ ] Phase 2 — EDA: transit signal characterization and visualization
- [ ] Phase 3 — Feature Engineering: period folding, box least-squares (BLS) analysis
- [ ] Phase 4 — ML Model: binary classifier for transit detection (positive vs. false positive)

---

## License

MIT — see [LICENSE](./LICENSE) for details.
