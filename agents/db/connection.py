from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from . import models

DATABASE_URL = "sqlite:///./recruitment.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

LocalSession = sessionmaker(bind=engine)


def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()