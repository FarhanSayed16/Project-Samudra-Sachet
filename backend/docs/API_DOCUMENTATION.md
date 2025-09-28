# API Documentation - Project Samudra Sachet

## 🌊 Ocean Hazard Reporting & Social Media Analytics Platform

Complete API reference for the Project Samudra Sachet backend system.

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Citizen Reports](#citizen-reports)
4. [Report Verification](#report-verification)
5. [Social Media Analytics](#social-media-analytics)
6. [AI & Media Analysis](#ai--media-analysis)
7. [Hotspot Monitoring](#hotspot-monitoring)
8. [Administration](#administration)
9. [Alerts & Notifications](#alerts--notifications)

## 🔐 Authentication

### Register User
```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "user_role": "citizen"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "email": "user@example.com",
  "user_id": "uuid"
}
```

### Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "refresh_token"
}
```

## 👤 User Management

### Get Current User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "user_role": "citizen",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update User Profile
```http
PUT /api/v1/users/me
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "full_name": "John Smith",
  "phone": "+1234567890",
  "address": "123 Main St, City"
}
```

### Change Password
```http
PUT /api/v1/users/me/password
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

## 📝 Citizen Reports

### Create Report
```http
POST /api/v1/reports/
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `hazard_type`: "tsunami" | "high_waves" | "storm" | "flood" | "other"
- `latitude`: float (-90 to 90)
- `longitude`: float (-180 to 180)
- `description`: string (optional)
- `severity_level`: int (1-5)
- `media_file`: file (optional)

**Response:**
```json
{
  "id": "uuid",
  "hazard_type": "tsunami",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "description": "High waves observed",
  "severity_level": 4,
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List Reports
```http
GET /api/v1/reports/
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 20, max: 100)
- `hazard_type`: string (optional)
- `status`: string (optional)
- `severity_min`: int (optional)
- `severity_max`: int (optional)
- `latitude`: float (optional)
- `longitude`: float (optional)
- `radius_km`: float (optional)
- `date_from`: datetime (optional)
- `date_to`: datetime (optional)
- `sort_by`: string (default: "created_at")
- `sort_order`: string (default: "desc")

### Get Report Details
```http
GET /api/v1/reports/{report_id}
Authorization: Bearer <token>
```

### Vote on Report
```http
POST /api/v1/reports/{report_id}/vote
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `vote_type`: "upvote" | "downvote"

## ✅ Report Verification

### Submit Verification
```http
POST /api/v1/reports/{report_id}/verification
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "decision": "verified" | "rejected" | "needs_more_info",
  "comments": "Verification comments",
  "priority_level": 1
}
```

### Get Verification History
```http
GET /api/v1/reports/{report_id}/verifications
Authorization: Bearer <token>
```

### Escalate Verification
```http
POST /api/v1/reports/{report_id}/escalate
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `escalated_to`: uuid
- `comments`: string (optional)

## 📱 Social Media Analytics

### List Social Media Posts
```http
GET /api/v1/social-media/
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 20, max: 100)
- `source`: "twitter" | "facebook" | "instagram" | "youtube"
- `hazard_type`: string (optional)
- `sentiment`: "positive" | "negative" | "neutral"
- `relevance_min`: float (0.0-1.0)
- `latitude`: float (optional)
- `longitude`: float (optional)
- `radius_km`: float (optional)
- `date_from`: datetime (optional)
- `date_to`: datetime (optional)
- `language`: string (optional)

### Get Sentiment Analysis
```http
GET /api/v1/social-media/sentiment
Authorization: Bearer <token>
```

**Query Parameters:**
- `hours`: int (default: 24, max: 168)
- `hazard_type`: string (optional)

**Response:**
```json
{
  "total_posts": 150,
  "posts_with_sentiment": 120,
  "sentiment_counts": {
    "positive": 30,
    "negative": 60,
    "neutral": 30
  },
  "average_sentiment_score": -0.2,
  "time_window_hours": 24
}
```

### Search Social Media
```http
POST /api/v1/social-media/search
Authorization: Bearer <token>
```

**Query Parameters:**
- `search_query`: string (required)
- `skip`: int (default: 0)
- `limit`: int (default: 20, max: 100)

## 🤖 AI & Media Analysis

### Analyze Image
```http
POST /api/v1/analysis/image
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `image_file`: file (required)
- `analysis_type`: "image_classification" | "hazard_detection"

**Response:**
```json
{
  "message": "Image analysis completed",
  "results": {
    "analysis_type": "image_classification",
    "confidence": 0.85,
    "predictions": [
      {
        "class": "tsunami_warning",
        "confidence": 0.85,
        "description": "High confidence tsunami warning detected"
      }
    ],
    "processing_time_ms": 1500,
    "model_used": "hazard_classifier_v1"
  }
}
```

### Analyze Text
```http
POST /api/v1/analysis/text
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `text_content`: string (required)
- `analysis_type`: "sentiment_analysis" | "ner_extraction" | "hazard_detection"

### List Available Models
```http
GET /api/v1/analysis/models
Authorization: Bearer <token>
```

### Batch Analysis Request
```http
POST /api/v1/analysis/batch
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `report_ids`: List[uuid] (optional)
- `post_ids`: List[uuid] (optional)
- `analysis_type`: string (required)

## 🔥 Hotspot Monitoring

### List Hotspots
```http
GET /api/v1/hotspots/
```

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 20, max: 100)
- `event_type`: string (optional)
- `alert_level_min`: int (1-5, optional)
- `latitude`: float (optional)
- `longitude`: float (optional)
- `radius_km`: float (optional)

**Response:**
```json
[
  {
    "id": "uuid",
    "event_type": "tsunami",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "radius_km": 5.0,
    "intensity_score": 0.85,
    "alert_level": 4,
    "status": "active",
    "report_count": 15,
    "social_count": 8,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Hotspot Details
```http
GET /api/v1/hotspots/{hotspot_id}
```

### Get Hotspots for Map
```http
GET /api/v1/hotspots/map-data
```

**Query Parameters:**
- `west`: float (required)
- `south`: float (required)
- `east`: float (required)
- `north`: float (required)
- `event_types`: string (comma-separated, optional)

### Generate Hotspots
```http
POST /api/v1/hotspots/generate
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `hours`: int (default: 6, max: 168)
- `min_reports`: int (default: 3, max: 20)
- `cluster_radius_km`: float (default: 5.0, max: 50)

## 🛠️ Administration

### Get Admin Dashboard
```http
GET /api/v1/admin/dashboard
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "system_health": {
    "total_activity": 1500,
    "successful_actions": 1450,
    "failed_actions": 50,
    "active_users": 25,
    "health_score": 96.7,
    "error_rate": 0.033
  },
  "user_stats": {
    "total_users": 150,
    "active_users": 120,
    "new_users_24h": 5
  },
  "report_stats": {
    "total_reports": 500,
    "reports_24h": 25,
    "pending_verification": 10
  }
}
```

### List All Users
```http
GET /api/v1/admin/users
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 20, max: 100)
- `user_role`: string (optional)
- `is_active`: boolean (optional)

### Change User Role
```http
PATCH /api/v1/admin/users/{user_id}/role
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "new_role": "analyst" | "authority" | "admin"
}
```

### Get System Health
```http
GET /api/v1/admin/system/health
Authorization: Bearer <admin_token>
```

### Get Audit Logs
```http
GET /api/v1/admin/audit-logs
Authorization: Bearer <admin_token>
```

## 🚨 Alerts & Notifications

### Create Alert
```http
POST /api/v1/alerts/
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Tsunami Warning",
  "message": "High tsunami alert for coastal areas",
  "alert_level": 5,
  "alert_type": "emergency",
  "target_audience": "all_citizens",
  "geographic_scope": "coastal_areas"
}
```

### List Alerts
```http
GET /api/v1/alerts/
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 20, max: 100)
- `alert_level`: int (1-5, optional)
- `alert_type`: string (optional)
- `status`: string (optional)
- `date_from`: datetime (optional)
- `date_to`: datetime (optional)

### Get Alert Templates
```http
GET /api/v1/alerts/templates
Authorization: Bearer <token>
```

### Send Test Alert
```http
POST /api/v1/alerts/test
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `test_message`: string (required)
- `alert_level`: int (1-5, default: 3)

## 📊 Response Formats

### Success Response
```json
{
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Paginated Response
```json
{
  "data": [...],
  "total_count": 100,
  "returned_count": 20,
  "skip": 0,
  "limit": 20
}
```

## 🔒 Authentication & Authorization

### User Roles
- **Public**: No authentication required
- **Authenticated**: Valid JWT token required
- **Citizen**: Citizen role required
- **Analyst**: Analyst or higher role required
- **Authority**: Authority or Admin role required
- **Admin**: Admin role required

### JWT Token Format
```
Authorization: Bearer <jwt_token>
```

### Token Expiration
- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

## 📈 Rate Limiting

- **Public Endpoints**: 100 requests/hour
- **Authenticated Endpoints**: 1000 requests/hour
- **Admin Endpoints**: 5000 requests/hour

## 🌐 CORS Configuration

Allowed origins:
- `https://yourdomain.com`
- `https://app.yourdomain.com`
- `http://localhost:3000` (development)

## 📝 Error Codes

| Code | Description |
|------|-------------|
| `INVALID_CREDENTIALS` | Invalid email or password |
| `TOKEN_EXPIRED` | JWT token has expired |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `VALIDATION_ERROR` | Request data validation failed |
| `FILE_TOO_LARGE` | Uploaded file exceeds size limit |
| `INVALID_FILE_TYPE` | Uploaded file type not allowed |

## 🔗 API Base URL

**Production**: `https://api.samudra-sachet.com/api/v1`  
**Development**: `http://localhost:8000/api/v1`

## 📚 Additional Resources

- [OpenAPI Documentation](https://api.samudra-sachet.com/docs)
- [ReDoc Documentation](https://api.samudra-sachet.com/redoc)
- [Postman Collection](https://api.samudra-sachet.com/postman-collection.json)

---

**API Version**: v1  
**Last Updated**: 2024-01-01  
**Status**: ✅ Production Ready
