from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, reports, reports_simple, verification, social_media, analysis, hotspots, admin, alerts

# Create main API router for v1
api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Include user management routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["User Management"]
)

# Include reports routes
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports Management"]
)

# Include simple reports routes
api_router.include_router(
    reports_simple.router,
    prefix="/reports-simple",
    tags=["Simple Reports"]
)

# Include verification routes
api_router.include_router(
    verification.router,
    prefix="/reports",
    tags=["Report Verification"]
)

# Include social media routes
api_router.include_router(
    social_media.router,
    prefix="/social-media",
    tags=["Social Media Analytics"]
)

# Include analysis routes
api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["AI & Media Analysis"]
)

# Include hotspot routes
api_router.include_router(
    hotspots.router,
    prefix="/hotspots",
    tags=["Hotspot Monitoring"]
)

# Include admin routes
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administration"]
)

# Include alert routes
api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Alerts & Notifications"]
)

# TODO: Add other endpoint routers as they are implemented
# api_router.include_router(
#     hotspots.router,
#     prefix="/hotspots",
#     tags=["Hotspot Monitoring"]
# )

# api_router.include_router(
#     social_media.router,
#     prefix="/social-media",
#     tags=["Social Media Analytics"]
# )

# api_router.include_router(
#     analysis.router,
#     prefix="/analysis",
#     tags=["AI & Media Analysis"]
# )

# api_router.include_router(
#     alerts.router,
#     prefix="/alerts",
#     tags=["Alerts & Notifications"]
# )

# api_router.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["Administration"]
# )

# api_router.include_router(
#     system.router,
#     prefix="/system",
#     tags=["System Operations"]
# )

# api_router.include_router(
#     files.router,
#     prefix="/files",
#     tags=["File Management"]
# )
