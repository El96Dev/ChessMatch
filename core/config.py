from pydantic_settings import BaseSettings
from pydantic import BaseModel
import os



class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class MatchmakingConfig(BaseModel):
    initial_elo_difference: int = 100
    elo_step: int = 100
    step_seconds_interval: int = 5
    max_elo_diff: int = 500


class ApiV1Prefix(BaseModel):
    prefix: str= "/v1"
    auth: str = "/auth"
    users: str = "/users"
    games: str = "/games"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        parts = (self.prefix, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        return path.removeprefix("/")


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str = os.getenv("RESET_PASSWORD_TOKEN")
    verification_token_secret: str = os.getenv("VERIFICATION_TOKEN_SECRET")


class CeleryConfig(BaseModel):
    broker_url: str = os.getenv("CELERY_BROKER_URL")
    backend_url: str = os.getenv("CELERY_RESULT_BACKEND")


class DatabaseConfig(BaseModel):
    user: str = os.getenv('DB_USER')
    password: str = os.getenv('DB_PASSWORD')
    db: str = os.getenv('DB_NAME')
    host: str = os.getenv('DB_HOST')
    port: str = os.getenv('DB_PORT')
    echo: bool = True

    @property
    def url(self):
        # return "postgresql+asyncpg://postgres:postgres@localhost:5432/chessmatch"
        # return "postgresql+asyncpg://postgres:postgres@localhost:5432/chessmatch"
        return "postgresql+asyncpg://" + self.user + ":" + self.password + "@" + \
                self.host + ":" + self.port + "/" + self.db


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig = DatabaseConfig()
    celery: CeleryConfig = CeleryConfig()
    access_token: AccessToken = AccessToken()
    matchmaking: MatchmakingConfig = MatchmakingConfig()


settings = Settings()