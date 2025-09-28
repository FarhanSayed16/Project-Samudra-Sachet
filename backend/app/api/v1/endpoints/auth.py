from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_token,
    security,
    get_current_user
)
from app.db.session import get_db
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token, RefreshToken, PasswordReset, PasswordResetConfirm, EmailVerification
from app.core.security import security


router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new citizen user.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (min 8 characters)
    - **full_name**: User's full name
    - **phone**: Optional phone number
    - **language_preference**: Preferred language (default: en)
    """
    # Check if user already exists
    existing_user = await crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await crud_user.create(db, user_in=user_in)
    
    # TODO: Send email verification
    # await send_verification_email(user.email)
    
    return {
        "message": "User registered successfully",
        "user_id": str(user.id),
        "email": user.email,
        "verification_required": True
    }


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user and return JWT tokens.
    
    - **email**: User's email address
    - **password**: User's password
    """
    # Authenticate user
    user = await crud_user.get_by_email(db, email=user_credentials.email)
    
    if not user or not crud_user.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    await crud_user.update_last_login(db, user)
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "user_role": user.user_role.value
        },
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "user_role": user.user_role.value
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh expired access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    try:
        token_data = verify_token(refresh_data.refresh_token, "refresh")
        
        # Get user to ensure they still exist and are active
        user = await crud_user.get_by_id(db, user_id=token_data.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "user_role": user.user_role.value
            },
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (invalidate current session).
    
    Note: In a stateless JWT system, this endpoint mainly serves for logging purposes.
    The actual token invalidation would require a token blacklist or shorter token expiry.
    """
    # TODO: Implement token blacklist or session invalidation
    # For now, we'll just log the logout event
    
    return {"message": "Logged out successfully"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    password_reset: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Send password reset email.
    
    - **email**: User's email address
    """
    user = await crud_user.get_by_email(db, email=password_reset.email)
    
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # TODO: Generate password reset token and send email
    # reset_token = create_password_reset_token(user.email)
    # await send_password_reset_email(user.email, reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    password_reset: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password with token.
    
    - **token**: Password reset token from email
    - **new_password**: New password
    """
    # TODO: Verify password reset token
    # user_email = verify_password_reset_token(password_reset.token)
    # if not user_email:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid or expired reset token"
    #     )
    
    # user = await crud_user.get_by_email(db, email=user_email)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not found"
    #     )
    
    # await crud_user.update_password(db, user, password_reset.new_password)
    
    # TODO: Implement actual password reset logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset functionality not yet implemented"
    )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    email_verification: EmailVerification,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email address with token.
    
    - **token**: Email verification token from email
    """
    # TODO: Verify email verification token
    # user_id = verify_email_verification_token(email_verification.token)
    # if not user_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid or expired verification token"
    #     )
    
    # user = await crud_user.get_by_id(db, user_id=user_id)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not found"
    #     )
    
    # await crud_user.verify_user(db, user)
    
    # TODO: Implement actual email verification logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email verification functionality not yet implemented"
    )
