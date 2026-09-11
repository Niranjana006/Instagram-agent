from celery import Celery
from influencer_agent.app.core.config import settings
import os

# Force Windows to behave
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_pool="solo",
    
    # --- WINDOWS CONNECTION FIXES ---
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_transport_options={
        'visibility_timeout': 3600,
        'socket_timeout': 10,
        'socket_connect_timeout': 10
    }
)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "influencer_agent.app.tasks.posting_tasks",
    "influencer_agent.app.tasks.scheduler_tasks",
    "influencer_agent.app.tasks.moderation_tasks",
    "influencer_agent.app.tasks.updates_tasks"
])