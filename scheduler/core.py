"""
APScheduler core — singleton scheduler lifecycle management.

Provides start_scheduler() and stop_scheduler() for FastAPI lifespan events,
plus get_scheduler_status() for the /scheduler/status API endpoint.
"""

import logging
import threading
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from scheduler.jobs import daily_health_check, monthly_data_refresh

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Cron: 10:00 AM IST daily for health check
# Cron: 02:00 AM IST on 1st of every month for data refresh
IST = pytz.timezone("Asia/Kolkata")
DAILY_CRON_HOUR = 10
DAILY_CRON_MINUTE = 0
MONTHLY_CRON_DAY = 1
MONTHLY_CRON_HOUR = 2
MONTHLY_CRON_MINUTE = 0

# Module-level singleton
_scheduler: Optional[BackgroundScheduler] = None
_lock = threading.Lock()
_last_run_info: Optional[dict] = None

logger = logging.getLogger("scheduler")


# ---------------------------------------------------------------------------
# Job wrapper — captures return value for status reporting
# ---------------------------------------------------------------------------
def _job_wrapper(job_func):
    """Wraps a job function to capture its result for status reporting."""
    def wrapper():
        global _last_run_info
        job_name = job_func.__name__
        logger.info("Executing job: %s", job_name)
        try:
            result = job_func()
            _last_run_info = {
                "job": job_name,
                "status": "success",
                "result": result,
                "finished_at": datetime.now(timezone.utc).isoformat(),
            }
            logger.info("Job %s completed successfully", job_name)
        except Exception as e:
            _last_run_info = {
                "job": job_name,
                "status": "failed",
                "error": str(e),
                "finished_at": datetime.now(timezone.utc).isoformat(),
            }
            logger.exception("Job %s failed: %s", job_name, e)
    return wrapper


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def start_scheduler() -> BackgroundScheduler:
    """
    Start the APScheduler BackgroundScheduler (singleton, thread-safe).

    Called from FastAPI's lifespan on_startup.
    Returns the running scheduler instance.
    """
    global _scheduler

    with _lock:
        if _scheduler is not None and _scheduler.running:
            logger.warning("Scheduler already running — skipping duplicate start")
            return _scheduler

        scheduler = BackgroundScheduler(
            timezone=IST,
            job_defaults={
                "coalesce": True,          # Combine missed runs into one
                "max_instances": 1,         # Prevent overlapping executions
                "misfire_grace_time": 300,  # 5-min grace window after missed fire
            },
        )

        # Register jobs
        scheduler.add_job(
            func=_job_wrapper(daily_health_check),
            trigger=CronTrigger(
                hour=DAILY_CRON_HOUR,
                minute=DAILY_CRON_MINUTE,
                timezone=IST,
            ),
            id="daily_health_check",
            name="Daily Health Check (10:00 AM IST)",
            replace_existing=True,
        )
        
        scheduler.add_job(
            func=_job_wrapper(monthly_data_refresh),
            trigger=CronTrigger(
                day=MONTHLY_CRON_DAY,
                hour=MONTHLY_CRON_HOUR,
                minute=MONTHLY_CRON_MINUTE,
                timezone=IST,
            ),
            id="monthly_data_refresh",
            name="Monthly Data Refresh (1st of month, 02:00 AM IST)",
            replace_existing=True,
        )

        scheduler.start()
        _scheduler = scheduler

        health_next_run = scheduler.get_job("daily_health_check").next_run_time
        refresh_next_run = scheduler.get_job("monthly_data_refresh").next_run_time
        logger.info(
            "Scheduler started — daily_health_check next run: %s, monthly_data_refresh next run: %s",
            health_next_run.isoformat() if health_next_run else "N/A",
            refresh_next_run.isoformat() if refresh_next_run else "N/A",
        )

        return scheduler


def stop_scheduler():
    """Shut down the scheduler gracefully. Called from lifespan on_shutdown."""
    global _scheduler

    with _lock:
        if _scheduler is not None and _scheduler.running:
            _scheduler.shutdown(wait=False)
            logger.info("Scheduler shut down")
            _scheduler = None


def get_scheduler_status() -> dict:
    """Return current scheduler status for the /scheduler/status endpoint."""
    if _scheduler is None or not _scheduler.running:
        return {
            "status": "stopped",
            "timezone": str(IST),
            "jobs": [],
            "last_run": _last_run_info,
        }

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {
        "status": "running",
        "timezone": str(IST),
        "cron_expression": f"{DAILY_CRON_MINUTE} {DAILY_CRON_HOUR} * * * (Asia/Kolkata)",
        "jobs": jobs,
        "last_run": _last_run_info,
    }
