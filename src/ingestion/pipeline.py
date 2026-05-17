import logging
from pathlib import Path
from typing import List, Optional

from pydantic import ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .provider import BaseProvider
from .storage import StorageManager

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Orchestrates the extraction and loading of astronomical data.
    Uses Dependency Injection to receive its components.
    """

    def __init__(self, provider: BaseProvider, storage: StorageManager):
        # We depend on the abstractions (BaseProvider), not the concrete MASTProvider
        self.provider = provider
        self.storage = storage

    # 2. Resilience: The Tenacity Retry Decorator
    # If a network error occurs (like Timeout or temporary 502 Bad Gateway),
    # this will retry up to 3 times. It waits 2 seconds, then 4s, then 8s (Exponential Backoff).
    # We explicitly tell it NOT to retry if it's a Pydantic ValidationError (bad data won't fix itself).
    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _process_single_target(self, target_id: str) -> Optional[Path]:
        """Processes a single star, wrapped in a retry mechanism."""
        logger.info(f"Fetching data for target: {target_id}")

        try:
            # Step A: Extract & Transform
            lc_data = self.provider.fetch_lightcurve(target_id)

            # Step B: Load (Save to disk)
            saved_path = self.storage.save_to_parquet(lc_data)

            logger.info(f"Successfully processed and saved {target_id} to {saved_path}")
            return saved_path

        except ValueError as e:
            # Expected business logic errors (e.g., target not found in NASA database)
            # We log the warning but don't crash the whole batch
            logger.warning(f"Skipping {target_id}: {str(e)}")
            return None
        except ValidationError as e:
            # Data corruption errors detected by Pydantic
            logger.error(f"Data corruption in {target_id}: {str(e)}")
            return None

    def run_batch(self, target_ids: List[str]) -> dict:
        """
        Main entry point. Processes a list of star IDs and returns a summary report.
        """
        logger.info(f"Starting batch processing for {len(target_ids)} targets.")

        report = {"successful": [], "failed": []}

        for target_id in target_ids:
            try:
                # We call our protected, retry-enabled method
                result_path = self._process_single_target(target_id)
                if result_path:
                    report["successful"].append(target_id)
                else:
                    report["failed"].append(target_id)

            except Exception as e:
                # If it still fails after all 3 retries, we catch the final exception here
                logger.error(
                    f"Critical failure processing {target_id} after retries: {str(e)}"
                )
                report["failed"].append(target_id)

        logger.info(
            f"Batch complete. Success: {len(report['successful'])}, Failed: {len(report['failed'])}"
        )
        return report
