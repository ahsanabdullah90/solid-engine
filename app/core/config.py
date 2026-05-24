import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mediaportfolio")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    MOONDREAM_MODEL = os.getenv("MOONDREAM_MODEL", "moondream")

config = Config()
