"""
Scheduled jobs for the HDFC Mutual Fund FAQ Assistant.

Each job is a standalone function so additional tasks can be added
to the scheduler without modifying core.py.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("scheduler.jobs")


def daily_health_check():
    """
    Daily health check job — runs at 10:00 AM IST.

    Validates that critical components are operational:
    - SCHEME_DATA is loaded
    - ChromaDB collection is accessible

    This job can be extended with additional checks (e.g., API ping,
    data freshness validation, cache warming).
    """
    job_start = datetime.now(timezone.utc)
    logger.info("daily_health_check: started at %s", job_start.isoformat())

    results = {}

    # Check 1: Verify SCHEME_DATA is loaded
    try:
        from rag.assembler import SCHEME_DATA
        scheme_count = len(SCHEME_DATA)
        results["scheme_data"] = f"OK ({scheme_count} schemes loaded)"
        logger.info("daily_health_check: SCHEME_DATA OK — %d schemes", scheme_count)
    except Exception as e:
        results["scheme_data"] = f"FAIL ({e})"
        logger.error("daily_health_check: SCHEME_DATA check failed — %s", e)

    # Check 2: Verify ChromaDB collection is accessible
    try:
        from rag.retriever import get_collection
        collection = get_collection()
        doc_count = collection.count()
        results["chromadb"] = f"OK ({doc_count} documents)"
        logger.info("daily_health_check: ChromaDB OK — %d documents", doc_count)
    except Exception as e:
        results["chromadb"] = f"FAIL ({e})"
        logger.error("daily_health_check: ChromaDB check failed — %s", e)

    job_end = datetime.now(timezone.utc)
    duration_ms = (job_end - job_start).total_seconds() * 1000

    all_ok = all(v.startswith("OK") for v in results.values())
    status = "PASS" if all_ok else "PARTIAL_FAILURE"

    logger.info(
        "daily_health_check: completed in %.1fms — status=%s — %s",
        duration_ms, status, results,
    )

    return {
        "job": "daily_health_check",
        "status": status,
        "results": results,
        "duration_ms": round(duration_ms, 1),
        "executed_at": job_start.isoformat(),
    }
