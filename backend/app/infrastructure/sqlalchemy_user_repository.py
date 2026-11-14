from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.entities import AuthUser
from ..domain.errors import EmailAlreadyRegisteredError
from .user_model import UserModel


class SQLAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_email(self, email: str) -> AuthUser | None:
        user = self._session.scalar(select(UserModel).where(UserModel.email == email))
        return self._to_entity(user) if user else None

    def find_by_id(self, user_id: UUID) -> AuthUser | None:
        user = self._session.get(UserModel, user_id)
        return self._to_entity(user) if user else None

    def create(self, email: str, password_hash: str) -> AuthUser:
        user = UserModel(email=email, password_hash=password_hash)
        self._session.add(user)
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise EmailAlreadyRegisteredError from error
        self._session.refresh(user)
        return self._to_entity(user)

    @staticmethod
    def _to_entity(user: UserModel) -> AuthUser:
        return AuthUser(id=user.id, email=user.email, password_hash=user.password_hash)
