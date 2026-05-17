import logging
import sys

from src.ingestion.pipeline import IngestionPipeline
from src.ingestion.provider import MASTProvider
from src.ingestion.storage import StorageManager


def setup_logging():
    """Configures the global logging format and output destination."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)  # Print everything to the console
        ],
    )


def main():
    """Main application entry point."""
    # 1. Initialize the global configuration
    setup_logging()
    logger = logging.getLogger("ExoplanetApp")

    logger.info("Initializing Exoplanet Data Ingestion System...")

    # 2. Dependency Injection: We create the concrete implementations here
    # This allows us to easily swap MASTProvider for a 'LocalDiskProvider' later if needed.
    provider = MASTProvider(author="Kepler", exptime=1800)
    storage = StorageManager(output_dir="data/processed")

    # 3. Inject them into the pipeline
    pipeline = IngestionPipeline(provider=provider, storage=storage)

    # 4. Define our test batch
    # We use a mix of famous stars with confirmed planets (Kepler-10, Kepler-186)
    # and a deliberate fake ID to test our error handling and retry logic.
    targets = [
        "Kepler-10",  # Famous rocky exoplanet (Kepler-10b)
        "Kepler-186",  # First Earth-size planet in habitable zone (Kepler-186f)
        "INVALID_STAR_999",  # Deliberately fake to test error handling
    ]

    # 5. Execute the batch
    report = pipeline.run_batch(targets)

    # 6. Final output
    logger.info("=== BATCH EXECUTION REPORT ===")
    logger.info(f"Successful targets: {report['successful']}")
    logger.info(f"Failed targets: {report['failed']}")


if __name__ == "__main__":
    # This block only executes if you run `uv run main.py` in the terminal
    main()
