from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # -------------------------
    # Database
    # -------------------------
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int

    # -------------------------
    # JWT / Security
    # -------------------------
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_TIME_MIN: int
    JWT_REFRESH_TOKEN_TIME_MIN: int

    # -------------------------
    # Tokens
    # -------------------------
    EMAIL_VERIFICATION_TOKEN_TIME_HOUR: int
    EMAIL_PASSWORD_RESET_TOKEN_TIME_HOUR: int

    # -------------------------
    # Frontend
    # -------------------------
    FRONTEND_URL: str

    # -------------------------
    # Derived values
    # -------------------------
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:"
            f"{self.DB_PASS}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "forbid"   # keep strict 🔒


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
