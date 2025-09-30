from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_official_roles
from app.db.session import get_db
from app.crud.crud_report import crud_report
from app.crud.crud_user import crud_user
from app.crud.crud_verification_log import crud_verification_log
from app.schemas.verification_log import VerificationLogCreate, VerificationLogUpdate
from app.models.verification_log import VerificationDecision
from app.models.user import User
from app.models.report import ReportStatus
import uuid


router = APIRouter()


@router.post("/{report_id}/verification", status_code=status.HTTP_201_CREATED)
async def submit_verification(
    report_id: uuid.UUID,
    verification_data: VerificationLogCreate,
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit verification decision for a report.
    
    - **report_id**: Report UUID
    - **verification_data**: Verification decision and comments
    """
    # Check if report exists
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Create verification log
    verification_log = await crud_verification_log.create(
        db=db,
        verification_in=verification_data,
        verified_by=current_user.id
    )
    
    # Update report status based on decision
    if verification_data.decision == VerificationDecision.VERIFIED:
        new_status = ReportStatus.VERIFIED
    elif verification_data.decision == VerificationDecision.REJECTED:
        new_status = ReportStatus.REJECTED
    else:  # NEEDS_MORE_INFO
        new_status = ReportStatus.UNDER_REVIEW
    
    await crud_report.update_status(db, report_id, new_status)
    
    return {
        "message": "Verification submitted successfully",
        "verification_id": str(verification_log.id),
        "decision": verification_data.decision.value,
        "new_status": new_status.value
    }


@router.get("/{report_id}/verifications")
async def get_verification_history(
    report_id: uuid.UUID,
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get verification history for a report.
    
    - **report_id**: Report UUID
    """
    # Check if report exists
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    verifications = await crud_verification_log.get_by_report_id(db, report_id)
    return verifications


@router.put("/{report_id}/verification/{verification_id}")
async def update_verification(
    report_id: uuid.UUID,
    verification_id: uuid.UUID,
    verification_update: VerificationLogUpdate,
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Update verification decision.
    
    - **report_id**: Report UUID
    - **verification_id**: Verification log UUID
    - **verification_update**: Updated verification data
    """
    # Check if verification exists and belongs to the report
    verification = await crud_verification_log.get_by_id(db, verification_id)
    if not verification or verification.report_id != report_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found"
        )
    
    # Check if user can update (must be the original verifier or admin)
    if verification.verified_by != current_user.id and current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own verifications"
        )
    
    # Update verification
    updated_verification = await crud_verification_log.update(
        db, verification, verification_update
    )
    
    return updated_verification


@router.post("/{report_id}/escalate", status_code=status.HTTP_200_OK)
async def escalate_verification(
    report_id: uuid.UUID,
    escalated_to: uuid.UUID = Form(...),
    comments: Optional[str] = Form(None),
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Escalate verification to higher authority.
    
    - **report_id**: Report UUID
    - **escalated_to**: User ID to escalate to
    - **comments**: Optional escalation comments
    """
    # Check if report exists
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if escalated user exists and has appropriate role
    escalated_user = await crud_user.get_by_id(db, escalated_to)
    if not escalated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to escalate to not found"
        )
    
    if escalated_user.user_role not in ["authority", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only escalate to authority or admin users"
        )
    
    # Get the latest verification for this report
    verifications = await crud_verification_log.get_by_report_id(db, report_id)
    if not verifications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification found to escalate"
        )
    
    latest_verification = verifications[0]
    
    # Escalate verification
    escalated_verification = await crud_verification_log.escalate_verification(
        db=db,
        verification_id=latest_verification.id,
        escalated_to=escalated_to,
        comments=comments
    )
    
    return {
        "message": "Verification escalated successfully",
        "escalated_to": str(escalated_to),
        "escalated_by": str(current_user.id)
    }


@router.get("/{report_id}/analysis")
async def get_report_analysis(
    report_id: uuid.UUID,
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI analysis results for a report.
    
    - **report_id**: Report UUID
    """
    # Check if report exists
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # TODO: Implement when media analysis module is ready
    return {
        "message": "Analysis functionality will be implemented with AI module",
        "report_id": str(report_id),
        "has_media": bool(report.media_url)
    }


@router.post("/{report_id}/analysis", status_code=status.HTTP_200_OK)
async def run_analysis(
    report_id: uuid.UUID,
    analysis_type: str = Form(..., regex="^(image_classification|sentiment_analysis|ner_extraction|hazard_detection)$"),
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Run new AI analysis on a report.
    
    - **report_id**: Report UUID
    - **analysis_type**: Type of analysis to run
    """
    # Check if report exists
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # TODO: Implement when AI processing service is ready
    return {
        "message": "Analysis processing will be implemented with AI service",
        "report_id": str(report_id),
        "analysis_type": analysis_type,
        "status": "queued"
    }


@router.get("/{report_id}/timeline")
async def get_report_timeline(
    report_id: uuid.UUID,
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get report activity timeline.
    
    - **report_id**: Report UUID
    """
    # Check if report exists
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get verification history
    verifications = await crud_verification_log.get_by_report_id(db, report_id)
    
    # Build timeline
    timeline = [
        {
            "timestamp": report.created_at,
            "event": "report_created",
            "description": f"Report created by {report.user.full_name}",
            "user": report.user.full_name
        }
    ]
    
    for verification in verifications:
        timeline.append({
            "timestamp": verification.created_at,
            "event": "verification",
            "description": f"Verification: {verification.decision.value}",
            "user": verification.verifier.full_name,
            "comments": verification.comments
        })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x["timestamp"])
    
    return {
        "report_id": str(report_id),
        "timeline": timeline
    }
