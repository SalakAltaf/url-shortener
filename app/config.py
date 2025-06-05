import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into environment

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shortener.db")
    SECRET_TOKEN: str = os.getenv("SECRET_TOKEN", "changeme")

settings = Settings()