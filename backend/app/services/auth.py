from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import AuthenticationException, ValidationException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.base import BaseService


class AuthService(BaseService[User, UserCreate, Any]):
    """
    Business Logic Service orchestrating User Registration, Authentication,
    JWT Token Lifecycle Management, and Profile Serializations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initializes AuthService with an instantiated UserRepository.
        """
        self.user_repo = UserRepository(session=session)
        super().__init__(repository=self.user_repo)

    async def register_user(self, user_in: UserCreate) -> UserResponse:
        """
        Registers a new user account.
        Validates email uniqueness, hashes the plaintext password, and persists entity.
        """
        # 1. Verify email uniqueness
        existing_user = await self.user_repo.get_by_email(email=user_in.email)
        if existing_user:
            raise ValidationException(
                message=f"Account with email address '{user_in.email}' is already registered.",
                details={"field": "email"}
            )

        # 2. Hash plain text password digest
        hashed_pwd = hash_password(user_in.password)

        # 3. Construct creation payload dictionary
        create_data: Dict[str, Any] = {
            "email": user_in.email.lower().strip(),
            "hashed_password": hashed_pwd,
            "full_name": user_in.full_name.strip(),
            "role": user_in.role,
            "is_active": True,
            "is_verified": False,
        }

        # 4. Persist user entity to database
        new_user = await self.user_repo.create(create_data)
        return UserResponse.model_validate(new_user)

    async def authenticate_user(self, login_in: UserLogin) -> Token:
        """
        Authenticates user credentials and returns signed JWT access & refresh tokens.
        """
        # 1. Fetch user by email
        user = await self.user_repo.get_by_email(email=login_in.email)
        if not user:
            raise AuthenticationException("Invalid email address or password.")

        # 2. Verify password digest matching
        if not verify_password(login_in.password, user.hashed_password):
            raise AuthenticationException("Invalid email address or password.")

        # 3. Ensure account is active
        if not user.is_active:
            raise AuthenticationException("User account has been disabled. Please contact support.")

        # 4. Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        await self.user_repo.update(user, obj_in={})

        # 5. Generate signed JWT tokens
        extra_claims = {"role": user.role.value}
        access_token = create_access_token(subject=str(user.id), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(user.id))

        user_response = UserResponse.model_validate(user)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )

    async def get_user_profile(self, user: User) -> UserResponse:
        """
        Serializes User SQLAlchemy model into a Pydantic UserResponse object.
        """
        return UserResponse.model_validate(user)
