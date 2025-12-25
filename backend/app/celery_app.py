"""
Celery Application Configuration
Handles asynchronous task processing for log ingestion and analytics
"""

import os
from celery import Celery

# Initialize Celery app
celery_app = Celery(
    'ecommerce_logs',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks from app.tasks module
celery_app.autodiscover_tasks(['app.tasks'])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery functionality"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'
