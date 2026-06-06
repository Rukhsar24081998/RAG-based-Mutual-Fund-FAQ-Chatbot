"""
Scheduled jobs for the HDFC Mutual Fund FAQ Assistant.

Each job is a standalone function so additional tasks can be added
to the scheduler without modifying core.py.
"""

import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def monthly_data_refresh():
    """
    Monthly data refresh job — re-ingests all sources and rebuilds ChromaDB.
    
    Executes the full data pipeline:
    1. Downloads latest PDFs from HDFC (fetcher.py with --force flag)
    2. Extracts text content (extractor.py)
    3. Chunks documents (chunker.py)
    4. Rebuilds ChromaDB embeddings (embedder.py)
    
    Runs on the 1st of every month at 02:00 AM IST.
    """
    job_start = datetime.now(timezone.utc)
    logger.info("monthly_data_refresh: started at %s", job_start.isoformat())
    
    results = {}
    # Use --force flag for fetcher to re-download all PDFs
    pipeline_scripts = [
        ("fetcher", ["ingest/fetcher.py", "--force"]),
        ("extractor", ["ingest/extractor.py"]),
        ("chunker", ["ingest/chunker.py"]),
        ("embedder", ["ingest/embedder.py"]),
    ]
    
    for step_name, script_args in pipeline_scripts:
        step_start = datetime.now(timezone.utc)
        logger.info(f"monthly_data_refresh: executing {step_name} ({' '.join(script_args)})")
        
        try:
            # Run the script using the current Python interpreter
            cmd = [sys.executable] + script_args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10-minute timeout per step
                check=True,
            )
            
            step_duration = (datetime.now(timezone.utc) - step_start).total_seconds()
            results[step_name] = f"OK (completed in {step_duration:.1f}s)"
            logger.info(f"monthly_data_refresh: {step_name} completed successfully")
            logger.debug(f"monthly_data_refresh: {step_name} output: {result.stdout}")
            
        except subprocess.TimeoutExpired:
            results[step_name] = f"FAIL (timeout after 600s)"
            logger.error(f"monthly_data_refresh: {step_name} timed out")
            break  # Stop pipeline on failure
            
        except subprocess.CalledProcessError as e:
            results[step_name] = f"FAIL (exit code {e.returncode})"
            logger.error(f"monthly_data_refresh: {step_name} failed: {e.stderr}")
            break  # Stop pipeline on failure
            
        except Exception as e:
            results[step_name] = f"FAIL ({str(e)})"
            logger.exception(f"monthly_data_refresh: {step_name} unexpected error")
            break  # Stop pipeline on failure
    
    job_end = datetime.now(timezone.utc)
    duration_ms = (job_end - job_start).total_seconds() * 1000
    
    all_ok = all(v.startswith("OK") for v in results.values())
    status = "PASS" if all_ok else "PARTIAL_FAILURE"
    
    logger.info(
        "monthly_data_refresh: completed in %.1fms — status=%s — %s",
        duration_ms, status, results,
    )
    
    return {
        "job": "monthly_data_refresh",
        "status": status,
        "results": results,
        "duration_ms": round(duration_ms, 1),
        "executed_at": job_start.isoformat(),
    }
