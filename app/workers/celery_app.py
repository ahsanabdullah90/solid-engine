from celery import Celery
from app.core.config import config

celery_app = Celery(
    "mediaportfolio",
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
