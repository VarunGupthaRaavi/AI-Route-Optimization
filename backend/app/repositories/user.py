from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Asynchronous Data Repository managing database operations for the User entity.
    Extends generic BaseRepository with user-specific query implementations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initializes UserRepository bound to the User model and current active AsyncSession.
        """
        super().__init__(model=User, session=session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Queries the database for an active, non-deleted user matching the given email address.
        Case-insensitive search supported via lower-case string matching.
        """
        query = select(User).where(
            User.email == email.lower().strip(),
            User.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalars().first()
