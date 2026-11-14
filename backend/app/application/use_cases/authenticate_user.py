from dataclasses import dataclass

from ...domain.entities import AuthUser
from ...domain.errors import InvalidCredentialsError
from ...domain.ports import AccessTokenIssuer, PasswordHasher, UserRepository


@dataclass(frozen=True)
class AuthenticatedUser:
    user: AuthUser
    access_token: str


class AuthenticateUser:
    def __init__(
        self,
        users: UserRepository,
        passwords: PasswordHasher,
        tokens: AccessTokenIssuer,
    ) -> None:
        self._users = users
        self._passwords = passwords
        self._tokens = tokens

    def execute(self, email: str, password: str) -> AuthenticatedUser:
        user = self._users.find_by_email(email.strip().lower())
        if user is None or not self._passwords.verify(password, user.password_hash):
            raise InvalidCredentialsError
        return AuthenticatedUser(user=user, access_token=self._tokens.issue(user.id))
