from uuid import UUID, uuid4

import pytest

from backend.app.application.use_cases.authenticate_user import AuthenticateUser
from backend.app.application.use_cases.register_user import RegisterUser
from backend.app.domain.entities import AuthUser
from backend.app.domain.errors import EmailAlreadyRegisteredError, InvalidCredentialsError


class FakeUsers:
    def __init__(self) -> None:
        self.users: dict[str, AuthUser] = {}

    def find_by_email(self, email: str) -> AuthUser | None:
        return self.users.get(email)

    def find_by_id(self, user_id: UUID) -> AuthUser | None:
        return next((user for user in self.users.values() if user.id == user_id), None)

    def create(self, email: str, password_hash: str) -> AuthUser:
        if email in self.users:
            raise EmailAlreadyRegisteredError
        user = AuthUser(id=uuid4(), email=email, password_hash=password_hash)
        self.users[email] = user
        return user


class FakePasswords:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class FakeTokens:
    def issue(self, user_id: UUID) -> str:
        return f"token:{user_id}"

    def subject(self, token: str) -> UUID:
        return UUID(token.removeprefix("token:"))


def test_register_normalizes_email_and_returns_access_token():
    users = FakeUsers()
    result = RegisterUser(users, FakePasswords(), FakeTokens()).execute(
        "  USER@Example.com ",
        "a-long-test-password",
    )

    assert result.user.email == "user@example.com"
    assert result.access_token == f"token:{result.user.id}"
    assert result.user.password_hash == "hashed:a-long-test-password"


def test_register_rejects_an_existing_email():
    users = FakeUsers()
    register = RegisterUser(users, FakePasswords(), FakeTokens())
    register.execute("user@example.com", "a-long-test-password")

    with pytest.raises(EmailAlreadyRegisteredError):
        register.execute("USER@example.com", "another-long-password")


def test_authenticate_issues_token_for_valid_credentials():
    users = FakeUsers()
    passwords = FakePasswords()
    RegisterUser(users, passwords, FakeTokens()).execute(
        "user@example.com",
        "a-long-test-password",
    )

    result = AuthenticateUser(users, passwords, FakeTokens()).execute(
        "USER@example.com",
        "a-long-test-password",
    )

    assert result.user.email == "user@example.com"
    assert result.access_token == f"token:{result.user.id}"


@pytest.mark.parametrize(
    ("email", "password"),
    [("missing@example.com", "a-long-test-password"), ("user@example.com", "wrong-password")],
)
def test_authenticate_rejects_invalid_credentials(email: str, password: str):
    users = FakeUsers()
    passwords = FakePasswords()
    RegisterUser(users, passwords, FakeTokens()).execute(
        "user@example.com",
        "a-long-test-password",
    )

    with pytest.raises(InvalidCredentialsError):
        AuthenticateUser(users, passwords, FakeTokens()).execute(email, password)
