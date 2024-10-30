from pydantic_settings import BaseSettings
from pydantic import BaseModel
import os



class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix_v1: str = "/api/v1"


class DatabaseConfig(BaseModel):
    user: str = os.getenv('DB_USER')
    password: str = os.getenv('DB_PASSWORD')
    db: str = os.getenv('DB_NAME')
    host: str = os.getenv('DB_HOST')
    port: str = os.getenv('DB_PORT')
    echo: bool = True

    @property
    def url(self):
        return "postgresql+asyncpg://" + self.user + ":" + self.password + "@" + \
                self.host + ":" + self.port + "/" + self.db


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()