"""
Scheduler package — production-ready APScheduler integration for FastAPI.

Usage:
    from scheduler import start_scheduler, stop_scheduler, get_scheduler_status
"""

from scheduler.core import start_scheduler, stop_scheduler, get_scheduler_status

__all__ = ["start_scheduler", "stop_scheduler", "get_scheduler_status"]
