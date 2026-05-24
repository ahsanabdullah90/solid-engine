from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import config
from app.database.models import Base

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
