from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.infrastructure.database import Base
from backend.app.infrastructure.sqlalchemy_analysis_history_repository import (
    SQLAlchemyAnalysisHistoryRepository,
)
from backend.app.infrastructure.sqlalchemy_user_repository import SQLAlchemyUserRepository

from conftest import PREDICTION


def test_analysis_history_persists_results_and_scopes_them_to_the_user():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        users = SQLAlchemyUserRepository(session)
        first_user = users.create("first@example.com", "hash")
        second_user = users.create("second@example.com", "hash")
        repository = SQLAlchemyAnalysisHistoryRepository(session)
        first_entry = repository.save(
            uuid4(),
            first_user.id,
            PREDICTION,
        )
        repository.save(uuid4(), second_user.id, PREDICTION)

    with Session(engine) as session:
        repository = SQLAlchemyAnalysisHistoryRepository(session)
        entries = repository.list_for_user(first_user.id, limit=10, offset=0)

    assert len(entries) == 1
    assert entries[0] == first_entry
    assert entries[0].probability == PREDICTION.probability
    assert entries[0].classification == PREDICTION.classification
    assert entries[0].threshold == PREDICTION.threshold
    assert entries[0].model_version == PREDICTION.model_version
    engine.dispose()
