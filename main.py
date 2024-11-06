from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api_v1 import router as api_v1_router
from core.config import settings
from core.models import db_helper
from api_v1.dependencies.games.matchmaking import update_elo_diff


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.start()
    print(scheduler.running, "scheduler running")
    scheduler.add_job(update_elo_diff, 'interval', seconds=settings.matchmaking.step_seconds_interval+1)
    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(api_v1_router, prefix=settings.api.prefix)


if __name__ == "__main__":
    print(settings.celery.backend_url, settings.celery.broker_url)
    uvicorn.run("main:app", host=settings.run.host, port=settings.run.port, reload=True)

