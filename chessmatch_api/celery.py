from celery import Celery

from chessmatch_api.core.config import settings
from api_v1.dependencies.games import ThreadSafeDeque, Player, Game


players = ThreadSafeDeque()
games = ThreadSafeDeque()

celery = Celery('celery', broker=settings.celery.broker_url, backend=settings.celery.backend_url)


@celery.task
def find_matches():
    pass


@celery.task
def update_elo_diff():
    pass