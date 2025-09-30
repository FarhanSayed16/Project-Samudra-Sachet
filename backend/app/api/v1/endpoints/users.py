from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    get_current_active_user,
    require_admin,
    require_management_roles
)
from app.db.session import get_db
from app.crud.crud_user import crud_user
from app.models.user import User, UserRole
from app.schemas.user import (
    User as UserSchema,
    UserUpdate,
    UserPasswordChange,
    UserLogin
)
from app.schemas.token import UserActivation
import uuid


router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile.
    
    Returns the authenticated user's profile information.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile.
    
    - **full_name**: Updated full name
    - **phone**: Updated phone number
    - **language_preference**: Updated language preference
    - **organization**: Updated organization (for authority users)
    """
    updated_user = await crud_user.update(db, current_user, user_update)
    return updated_user


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: UserPasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password
    """
    # Verify current password
    if not crud_user.verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    await crud_user.update_password(db, current_user, password_change.new_password)
    
    return {"message": "Password updated successfully"}


@router.post("/me/avatar", status_code=status.HTTP_200_OK)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload profile picture.
    
    - **file**: Image file (JPEG, PNG, WebP)
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # TODO: Implement file upload to cloud storage (S3, Cloudinary, etc.)
    # For now, we'll just return a placeholder URL
    
    avatar_url = f"https://example.com/avatars/{current_user.id}.jpg"
    
    # Update user profile with avatar URL
    user_update = UserUpdate(profile_picture_url=avatar_url)
    await crud_user.update(db, current_user, user_update)
    
    return {
        "message": "Avatar uploaded successfully",
        "avatar_url": avatar_url
    }


@router.get("/me/reports")
async def get_user_reports(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get user's submitted reports.
    
    Returns paginated list of reports submitted by the current user.
    """
    # TODO: Implement when reports CRUD is ready
    # reports = await crud_report.get_reports_by_user(
    #     db, user_id=current_user.id, skip=skip, limit=limit
    # )
    
    return {
        "message": "Reports functionality will be implemented with reports module",
        "user_id": str(current_user.id),
        "skip": skip,
        "limit": limit
    }


@router.get("/me/alerts")
async def get_user_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get user's alert history.
    
    Returns paginated list of alerts received by the current user.
    """
    # TODO: Implement when alerts module is ready
    return {
        "message": "Alerts functionality will be implemented with alerts module",
        "user_id": str(current_user.id),
        "skip": skip,
        "limit": limit
    }


@router.get("/me/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get user's activity timeline.
    
    Returns paginated list of user activities (reports, votes, etc.).
    """
    # TODO: Implement when audit logs are ready
    return {
        "message": "Activity timeline will be implemented with audit logs",
        "user_id": str(current_user.id),
        "skip": skip,
        "limit": limit
    }


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(require_management_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user details by ID.
    
    Access restricted to Authority and Admin users.
    """
    user = await crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/{user_id}/verify", response_model=UserSchema)
async def verify_user_identity(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user identity (KYC).
    
    Access restricted to Admin users only.
    """
    user = await crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    verified_user = await crud_user.verify_user(db, user)
    return verified_user


@router.patch("/{user_id}/status", response_model=UserSchema)
async def change_user_status(
    user_id: uuid.UUID,
    activation: UserActivation,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Activate/deactivate user account.
    
    Access restricted to Admin users only.
    
    - **is_active**: True to activate, False to deactivate
    """
    user = await crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if activation.is_active:
        updated_user = await crud_user.activate_user(db, user)
    else:
        updated_user = await crud_user.deactivate_user(db, user)
    
    return updated_user


@router.get("/", response_model=List[UserSchema])
async def get_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """
    List all users with optional filters.
    
    Access restricted to Admin users only.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **user_role**: Filter by user role
    - **is_active**: Filter by active status
    """
    users = await crud_user.get_users(
        db, 
        skip=skip, 
        limit=limit,
        user_role=user_role.value if user_role else None,
        is_active=is_active
    )
    
    return users
