import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.running = False
        self.jobs = {}
    
    def start(self):
        self.running = True
        logger.info("Scheduler started (simplified mode)")
    
    def stop(self):
        self.running = False
        logger.info("Scheduler stopped")
    
    def schedule_daily_google_fit_sync(self, job_func: Callable, hour: int = 7, minute: int = 0):
        logger.info(f"Scheduled daily Google Fit sync at {hour}:{minute} (not implemented in simplified mode)")
    
    def schedule_daily_insights(self, job_func: Callable, hour: int = 7, minute: int = 30):
        logger.info(f"Scheduled daily insights generation at {hour}:{minute} (not implemented in simplified mode)")
    
    def schedule_custom_job(self, job_func: Callable, job_id: str, trigger: str, **trigger_args):
        logger.info(f"Custom job {job_id} scheduled (not implemented in simplified mode)")
    
    def remove_job(self, job_id: str):
        logger.info(f"Removed job: {job_id}")
    
    def get_jobs(self):
        return []
    
    def pause_job(self, job_id: str):
        logger.info(f"Paused job: {job_id}")
    
    def resume_job(self, job_id: str):
        logger.info(f"Resumed job: {job_id}")

scheduler_service = SchedulerService()
