
import pytest
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.task import Task  # noqa: F401


@pytest.fixture
def db_session():
    connection = engine.connect()
    outer_transaction = connection.begin()

    db = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield db
    finally:
        db.close()
        outer_transaction.rollback()
        connection.close()
