from celery import Celery

from chessmatch_api.core.config import settings


celery = Celery('celery', broker=settings.celery.broker_url, backend=settings.celery.backend_url)


@celery.task
def add(x, y):
    return x + y