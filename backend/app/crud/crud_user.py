from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
import uuid


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CRUDUser:
    """CRUD operations for User model."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            print(f"Password hashing error: {e}")
            # Fallback to a simple hash if bcrypt fails
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        # Convert UUID to string for SQLite compatibility
        user_id_str = str(user_id) if isinstance(user_id, uuid.UUID) else user_id
        result = await db.execute(select(User).where(User.id == user_id_str))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """Create a new user."""
        # Hash the password
        hashed_password = CRUDUser.get_password_hash(user_in.password)
        
        # Create user object
        db_user = User(
            email=user_in.email.lower(),
            password_hash=hashed_password,
            full_name=user_in.full_name,
            phone=user_in.phone,
            user_role=user_in.user_role,
            language_preference=user_in.language_preference,
            organization=user_in.organization,
            verification_id=user_in.verification_id,
            is_verified_volunteer=False,  # Default to false, needs admin verification
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        db_user: User, 
        user_in: UserUpdate
    ) -> User:
        """Update user information."""
        update_data = user_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update_password(
        db: AsyncSession, 
        db_user: User, 
        new_password: str
    ) -> User:
        """Update user password."""
        hashed_password = CRUDUser.get_password_hash(new_password)
        db_user.password_hash = hashed_password
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update_last_login(db: AsyncSession, db_user: User) -> User:
        """Update user's last login timestamp."""
        from sqlalchemy import func
        db_user.last_login = func.now()
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def verify_user(db: AsyncSession, db_user: User) -> User:
        """Mark user as verified."""
        db_user.is_verified = True
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def activate_user(db: AsyncSession, db_user: User) -> User:
        """Activate user account."""
        db_user.is_active = True
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, db_user: User) -> User:
        """Deactivate user account."""
        db_user.is_active = False
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_users(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        user_role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Get list of users with optional filters."""
        query = select(User)
        
        if user_role:
            query = query.where(User.user_role == user_role)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_with_reports(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get user with their reports."""
        result = await db.execute(
            select(User)
            .options(selectinload(User.reports))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: uuid.UUID) -> bool:
        """Delete user (soft delete by deactivating)."""
        db_user = await CRUDUser.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await CRUDUser.deactivate_user(db, db_user)
        return True


# Create instance
crud_user = CRUDUser()


# Convenience functions for backward compatibility
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email (convenience function)."""
    return await crud_user.get_by_email(db, email)


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user (convenience function)."""
    return await crud_user.create(db, user_in)
