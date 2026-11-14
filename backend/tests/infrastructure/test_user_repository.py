from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.infrastructure.database import Base
from backend.app.infrastructure.sqlalchemy_user_repository import SQLAlchemyUserRepository
from backend.app.infrastructure.user_model import UserModel


def test_user_repository_persists_and_finds_by_email_and_id():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        users = SQLAlchemyUserRepository(session)
        created = users.create("user@example.com", "argon2-hash")

        assert users.find_by_email("user@example.com") == created
        assert users.find_by_id(created.id) == created
        assert created.password_hash == "argon2-hash"

    engine.dispose()
