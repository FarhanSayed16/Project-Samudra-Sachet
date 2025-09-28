from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    get_current_active_user,
    require_analyst_or_authority,
    require_admin
)
from app.db.session import get_db
from app.crud.crud_media_analysis import crud_media_analysis
from app.crud.crud_report import crud_report
from app.crud.crud_social_media_post import crud_social_media_post
from app.models.user import User
from app.models.media_analysis import AnalysisType
from app.schemas.media_analysis import (
    MediaAnalysis as MediaAnalysisSchema,
    MediaAnalysisCreate,
    MediaAnalysisUpdate
)
import uuid
from datetime import datetime


router = APIRouter()


@router.post("/image", status_code=status.HTTP_200_OK)
async def analyze_image(
    image_file: UploadFile = File(...),
    analysis_type: str = Form(..., regex="^(image_classification|hazard_detection)$"),
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze uploaded image using AI models.
    
    - **image_file**: Image file to analyze
    - **analysis_type**: Type of analysis to perform
    """
    # Validate file type
    if not image_file.content_type or not image_file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # TODO: Implement actual AI image analysis
    # For now, return mock results
    mock_results = {
        "analysis_type": analysis_type,
        "confidence": 0.85,
        "predictions": [
            {
                "class": "tsunami_warning",
                "confidence": 0.85,
                "description": "High confidence tsunami warning detected"
            },
            {
                "class": "high_waves",
                "confidence": 0.72,
                "description": "High waves detected"
            }
        ],
        "processing_time_ms": 1500,
        "model_used": "hazard_classifier_v1"
    }
    
    return {
        "message": "Image analysis completed",
        "results": mock_results,
        "file_name": image_file.filename,
        "analysis_type": analysis_type
    }


@router.post("/text", status_code=status.HTTP_200_OK)
async def analyze_text(
    text_content: str = Form(..., min_length=1, max_length=10000),
    analysis_type: str = Form(..., regex="^(sentiment_analysis|ner_extraction|hazard_detection)$"),
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze text content using AI models.
    
    - **text_content**: Text content to analyze
    - **analysis_type**: Type of analysis to perform
    """
    # TODO: Implement actual AI text analysis
    # For now, return mock results
    mock_results = {
        "analysis_type": analysis_type,
        "text_length": len(text_content),
        "sentiment": {
            "label": "concern",
            "score": -0.3,
            "confidence": 0.78
        },
        "entities": [
            {
                "text": "tsunami",
                "label": "HAZARD",
                "confidence": 0.92
            },
            {
                "text": "Mumbai",
                "label": "LOCATION",
                "confidence": 0.95
            }
        ],
        "hazard_keywords": ["tsunami", "warning", "evacuate"],
        "processing_time_ms": 800,
        "model_used": "sentiment_analyzer_v1"
    }
    
    return {
        "message": "Text analysis completed",
        "results": mock_results,
        "analysis_type": analysis_type
    }


@router.get("/{analysis_id}", response_model=MediaAnalysisSchema)
async def get_analysis_results(
    analysis_id: uuid.UUID,
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    Get analysis results by ID.
    
    - **analysis_id**: Analysis UUID
    """
    analysis = await crud_media_analysis.get_by_id(db, analysis_id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return analysis


@router.get("/jobs")
async def list_analysis_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    List analysis jobs.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **status**: Filter by job status
    """
    analyses, total_count = await crud_media_analysis.get_analysis_jobs(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return {
        "jobs": analyses,
        "total_count": total_count,
        "returned_count": len(analyses)
    }


@router.post("/batch", status_code=status.HTTP_200_OK)
async def batch_analysis_request(
    report_ids: List[uuid.UUID] = Form(...),
    post_ids: List[uuid.UUID] = Form(...),
    analysis_type: str = Form(..., regex="^(image_classification|sentiment_analysis|ner_extraction|hazard_detection)$"),
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    Batch analysis request for multiple reports and posts.
    
    - **report_ids**: List of report UUIDs to analyze
    - **post_ids**: List of post UUIDs to analyze
    - **analysis_type**: Type of analysis to perform
    """
    # Validate that at least one ID is provided
    if not report_ids and not post_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one report_id or post_id must be provided"
        )
    
    # TODO: Implement actual batch analysis processing
    # For now, return mock response
    return {
        "message": "Batch analysis request submitted",
        "analysis_type": analysis_type,
        "report_count": len(report_ids),
        "post_count": len(post_ids),
        "total_items": len(report_ids) + len(post_ids),
        "status": "queued",
        "estimated_completion": "5-10 minutes"
    }


@router.get("/models")
async def list_available_models(
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    List available AI models.
    
    Returns information about all available AI models for analysis.
    """
    models = await crud_media_analysis.get_available_models(db)
    
    return {
        "models": models,
        "total_models": len(models)
    }


@router.post("/models/{model_id}/retrain", status_code=status.HTTP_200_OK)
async def retrain_model(
    model_id: str,
    training_data: Optional[str] = Form(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrain AI model with new data.
    
    - **model_id**: Model identifier
    - **training_data**: Optional training data description
    """
    # Validate model exists
    models = await crud_media_analysis.get_available_models(db)
    model_exists = any(model["model_id"] == model_id for model in models)
    
    if not model_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # TODO: Implement actual model retraining
    # For now, return mock response
    return {
        "message": "Model retraining initiated",
        "model_id": model_id,
        "status": "training_started",
        "estimated_completion": "2-4 hours",
        "training_data": training_data
    }


@router.get("/stats")
async def get_analysis_statistics(
    hours: int = Query(24, ge=1, le=168),
    analysis_type: Optional[AnalysisType] = Query(None),
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    Get analysis statistics.
    
    - **hours**: Time window for statistics (1-168 hours)
    - **analysis_type**: Filter by analysis type
    """
    stats = await crud_media_analysis.get_analysis_stats(
        db=db,
        hours=hours,
        analysis_type=analysis_type
    )
    
    return stats
