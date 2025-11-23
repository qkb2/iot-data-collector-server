from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Raw env vars
    DATABASE_URL: str | None = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "esp"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"

    @property
    def async_database_url(self) -> str:
        """
        If DATABASE_URL exists then return it, else build asyncpg URL from env vars.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
