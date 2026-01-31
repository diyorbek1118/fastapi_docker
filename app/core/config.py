from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://user:password@db:3306/fastapi_db"

settings = Settings()
