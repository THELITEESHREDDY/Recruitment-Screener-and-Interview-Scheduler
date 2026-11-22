from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Absolute path to the project root
BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "recruitment.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

LocalSession = sessionmaker(bind=engine)


def get_db():
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()