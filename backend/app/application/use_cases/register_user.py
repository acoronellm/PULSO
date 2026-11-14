from ...domain.entities import AuthUser
from ...domain.errors import EmailAlreadyRegisteredError
from ...domain.ports import AccessTokenIssuer, PasswordHasher, UserRepository
from .authenticate_user import AuthenticatedUser


class RegisterUser:
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
        normalized_email = email.strip().lower()
        if self._users.find_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError

        user: AuthUser = self._users.create(
            normalized_email,
            self._passwords.hash(password),
        )
        return AuthenticatedUser(user=user, access_token=self._tokens.issue(user.id))
