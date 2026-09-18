from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "myasset360-secret-key-change-in-production"
    DATABASE_URL: str = "sqlite:///./myasset360.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    UPLOAD_DIR: str = "./uploads"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
