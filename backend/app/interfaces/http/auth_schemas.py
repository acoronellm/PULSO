from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from ...application.use_cases.authenticate_user import AuthenticatedUser
from ...domain.entities import AuthUser


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr

    @classmethod
    def from_domain(cls, user: AuthUser) -> "UserResponse":
        return cls(id=user.id, email=user.email)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

    @classmethod
    def from_result(cls, result: AuthenticatedUser, expires_in: int) -> "AuthResponse":
        return cls(
            access_token=result.access_token,
            expires_in=expires_in,
            user=UserResponse.from_domain(result.user),
        )
