from fastapi import APIRouter, Depends, HTTPException, status

from ....application.use_cases.authenticate_user import AuthenticateUser
from ....application.use_cases.register_user import RegisterUser
from ....domain.entities import AuthUser
from ....domain.errors import EmailAlreadyRegisteredError, InvalidCredentialsError
from ....infrastructure.config import Settings
from ..dependencies import (
    get_authenticate_user,
    get_current_user,
    get_register_user,
    get_settings,
)
from ..auth_schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    use_case: RegisterUser = Depends(get_register_user),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    try:
        result = use_case.execute(str(payload.email), payload.password)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo.",
        ) from None
    return AuthResponse.from_result(result, settings.access_token_expire_minutes * 60)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    use_case: AuthenticateUser = Depends(get_authenticate_user),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    try:
        result = use_case.execute(str(payload.email), payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return AuthResponse.from_result(result, settings.access_token_expire_minutes * 60)


@router.get("/me", response_model=UserResponse)
def current_user(user: AuthUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_domain(user)
