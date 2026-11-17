
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.base import Base

# Import model registration module.
# This ensures all related SQLAlchemy models are registered.
import backend.db.init_db

from agents.ranker import nodes as ranker_nodes


@pytest.fixture
def db_setup(tmp_path, monkeypatch):
    """
    Create an isolated SQLite database for each test.
    """

    database_path = tmp_path / "test_recruitment.db"

    test_engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=test_engine)

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False
    )

    # Make Ranker nodes use the temporary test database.
    monkeypatch.setattr(
        ranker_nodes,
        "LocalSession",
        TestSessionLocal
    )

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        test_engine.dispose()
