from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.crud.crud_user import crud_user
from app.models.user import User, UserRole
from app.schemas.token import TokenData
import uuid


# Security scheme
security = HTTPBearer()

# Custom security dependency with debugging
async def get_credentials_with_debug(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> HTTPAuthorizationCredentials:
    """Get credentials with debugging information."""
    print(f"[SECURITY] Authorization header received: {credentials.credentials[:20]}...")
    print(f"[SECURITY] Scheme: {credentials.scheme}")
    return credentials

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last 7 days
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify and decode JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"[TOKEN] Verifying token: {token[:20]}... (type: {token_type})")
        print(f"[TOKEN] Secret key: {settings.SECRET_KEY[:10]}...")
        print(f"[TOKEN] Algorithm: {settings.ALGORITHM}")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"[TOKEN] Token payload: {payload}")
        
        # Check token type
        if payload.get("type") != token_type:
            print(f"[TOKEN] Token type mismatch: expected {token_type}, got {payload.get('type')}")
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            print(f"[TOKEN] No user_id in token payload")
            raise credentials_exception
        
        token_data = TokenData(
            user_id=uuid.UUID(user_id),
            email=payload.get("email"),
            user_role=payload.get("user_role")
        )
        
        print(f"[TOKEN] Token verified successfully: {token_data}")
        return token_data
        
    except JWTError as e:
        print(f"[TOKEN] JWT Error: {type(e).__name__}: {e}")
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(get_credentials_with_debug),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        print(f"[AUTH] Token received: {token[:20]}...")
        print(f"[AUTH] Full token length: {len(token)}")
        
        token_data = verify_token(token, "access")
        print(f"[AUTH] Token data: user_id={token_data.user_id}, email={token_data.email}, role={token_data.user_role}")
        
        user = await crud_user.get_by_id(db, user_id=token_data.user_id)
        if user is None:
            print(f"[AUTH] User not found for ID: {token_data.user_id}")
            raise credentials_exception
        
        print(f"[AUTH] User found: {user.email}, role: {user.user_role}, active: {user.is_active}")
        
        if not user.is_active:
            print(f"[AUTH] User inactive: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return user
        
    except HTTPException as e:
        print(f"[AUTH] HTTPException: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        print(f"[AUTH] Exception in get_current_user: {type(e).__name__}: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: UserRole):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        print(f"[ROLE] Role check: user_role={current_user.user_role}, required={required_role}")
        if current_user.user_role != required_role and current_user.user_role != UserRole.ADMIN:
            print(f"[ROLE] Role access denied: {current_user.user_role} != {required_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        print(f"[ROLE] Role access granted: {current_user.user_role}")
        return current_user
    
    return role_checker


def require_any_role(*required_roles: UserRole):
    """Dependency factory for multiple role access control."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        print(f"[ROLE] Multi-role check: user_role={current_user.user_role}, required={[r.value for r in required_roles]}")
        if current_user.user_role not in required_roles and current_user.user_role != UserRole.ADMIN:
            print(f"[ROLE] Multi-role access denied: {current_user.user_role} not in {[r.value for r in required_roles]}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in required_roles]}"
            )
        print(f"[ROLE] Multi-role access granted: {current_user.user_role}")
        return current_user
    
    return role_checker


# Common role dependencies
require_citizen = require_role(UserRole.CITIZEN)
require_coastal_volunteer = require_role(UserRole.COASTAL_VOLUNTEER)
require_coastal_guard = require_role(UserRole.COASTAL_GUARD)
require_disaster_manager = require_role(UserRole.DISASTER_MANAGER)
require_admin = require_role(UserRole.ADMIN)

# Multi-role dependencies
require_volunteer_or_guard = require_any_role(UserRole.COASTAL_VOLUNTEER, UserRole.COASTAL_GUARD)
require_guard_or_manager = require_any_role(UserRole.COASTAL_GUARD, UserRole.DISASTER_MANAGER)
require_official_roles = require_any_role(UserRole.COASTAL_VOLUNTEER, UserRole.COASTAL_GUARD, UserRole.DISASTER_MANAGER)
require_management_roles = require_any_role(UserRole.COASTAL_GUARD, UserRole.DISASTER_MANAGER, UserRole.ADMIN)
