# SafeGuardian API Specification v1.0

## Overview

The SafeGuardian API provides a comprehensive RESTful interface for all system components including mobile applications, web dashboards, and administrative interfaces. The API implements OAuth2 authentication, role-based access control, and comprehensive audit logging to ensure secure and compliant operation.

## Base URL

```
Production: https://api.safeguardian.com/v1
Staging: https://staging-api.safeguardian.com/v1
Development: http://localhost:5000/v1
```

## Authentication

### OAuth2 Flow

SafeGuardian implements OAuth2 with PKCE (Proof Key for Code Exchange) for secure authentication across all client applications.

#### Authorization Endpoint
```
GET /auth/authorize
```

**Parameters:**
- `client_id` (required): Application client identifier
- `response_type` (required): Must be "code"
- `redirect_uri` (required): Registered redirect URI
- `scope` (required): Requested permissions
- `state` (required): CSRF protection token
- `code_challenge` (required): PKCE code challenge
- `code_challenge_method` (required): Must be "S256"

#### Token Exchange
```
POST /auth/token
```

**Request Body:**
```json
{
  "grant_type": "authorization_code",
  "client_id": "string",
  "code": "string",
  "redirect_uri": "string",
  "code_verifier": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "string",
  "scope": "string"
}
```

### JWT Token Structure

```json
{
  "sub": "user_id",
  "iss": "safeguardian",
  "aud": "safeguardian-api",
  "exp": 1234567890,
  "iat": 1234567890,
  "roles": ["guardian", "admin"],
  "permissions": ["read:sessions", "write:alerts"],
  "family_id": "family_uuid"
}
```

## Data Models

### User Model
```json
{
  "id": "uuid",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "guardian|child|admin|law_enforcement",
  "family_id": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime",
  "is_active": "boolean",
  "preferences": {
    "notifications": {
      "email": "boolean",
      "sms": "boolean",
      "push": "boolean"
    },
    "alert_thresholds": {
      "low": "boolean",
      "medium": "boolean",
      "high": "boolean",
      "critical": "boolean"
    }
  }
}
```

### Child Profile Model
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "guardian_id": "uuid",
  "date_of_birth": "date",
  "platforms": [
    {
      "platform": "facebook|instagram|snapchat|tiktok|discord",
      "username": "string",
      "connected": "boolean",
      "last_sync": "datetime",
      "monitoring_enabled": "boolean"
    }
  ],
  "emergency_contacts": [
    {
      "name": "string",
      "relationship": "string",
      "phone": "string",
      "email": "string",
      "priority": "integer"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Session Model
```json
{
  "id": "uuid",
  "child_id": "uuid",
  "platform": "string",
  "start_time": "datetime",
  "end_time": "datetime",
  "duration": "integer",
  "message_count": "integer",
  "risk_score": "float",
  "status": "active|completed|flagged|emergency",
  "participants": [
    {
      "username": "string",
      "user_id": "string",
      "risk_level": "low|medium|high|critical"
    }
  ],
  "metadata": {
    "device_info": "object",
    "location": "object",
    "app_version": "string"
  }
}
```

### Message Model
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "sender": "string",
  "recipient": "string",
  "content": "string",
  "content_type": "text|image|video|audio|file",
  "timestamp": "datetime",
  "platform_message_id": "string",
  "risk_score": "float",
  "risk_factors": [
    {
      "type": "grooming|inappropriate_content|personal_info_request",
      "confidence": "float",
      "description": "string"
    }
  ],
  "ai_analysis": {
    "sentiment": "positive|negative|neutral",
    "intent": "string",
    "entities": ["array"],
    "language": "string"
  }
}
```

### Alert Model
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "message_id": "uuid",
  "child_id": "uuid",
  "guardian_id": "uuid",
  "severity": "low|medium|high|critical",
  "type": "grooming|inappropriate_content|stranger_contact|emergency",
  "title": "string",
  "description": "string",
  "risk_score": "float",
  "status": "new|acknowledged|investigating|resolved|escalated",
  "created_at": "datetime",
  "acknowledged_at": "datetime",
  "resolved_at": "datetime",
  "actions_taken": [
    {
      "action": "string",
      "timestamp": "datetime",
      "user_id": "uuid"
    }
  ],
  "evidence": {
    "messages": ["array"],
    "screenshots": ["array"],
    "metadata": "object"
  }
}
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "guardian|child",
  "family_code": "string"
}
```

**Response (201):**
```json
{
  "user": "User",
  "message": "Registration successful"
}
```

#### POST /auth/login
Authenticate user credentials.

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "mfa_code": "string"
}
```

**Response (200):**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "user": "User",
  "expires_in": 3600
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response (200):**
```json
{
  "access_token": "string",
  "expires_in": 3600
}
```

#### POST /auth/logout
Invalidate user session and tokens.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

### User Management Endpoints

#### GET /users/profile
Get current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "user": "User"
}
```

#### PUT /users/profile
Update user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "preferences": "object"
}
```

**Response (200):**
```json
{
  "user": "User",
  "message": "Profile updated successfully"
}
```

#### GET /users/children
Get list of children for guardian.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response (200):**
```json
{
  "children": ["ChildProfile"],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### POST /users/children
Add a new child profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "date",
  "emergency_contacts": ["array"]
}
```

**Response (201):**
```json
{
  "child": "ChildProfile",
  "message": "Child profile created successfully"
}
```

### Platform Integration Endpoints

#### GET /platforms
Get list of supported platforms.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "platforms": [
    {
      "id": "facebook",
      "name": "Facebook",
      "icon": "string",
      "oauth_url": "string",
      "supported_features": ["messaging", "posts", "stories"]
    }
  ]
}
```

#### POST /platforms/{platform_id}/connect
Connect child account to social media platform.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `platform_id`: Platform identifier

**Request Body:**
```json
{
  "child_id": "uuid",
  "oauth_code": "string",
  "redirect_uri": "string"
}
```

**Response (200):**
```json
{
  "connection": {
    "platform": "string",
    "username": "string",
    "connected": true,
    "permissions": ["array"]
  },
  "message": "Platform connected successfully"
}
```

#### DELETE /platforms/{platform_id}/disconnect
Disconnect child account from platform.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `platform_id`: Platform identifier

**Query Parameters:**
- `child_id`: Child UUID

**Response (200):**
```json
{
  "message": "Platform disconnected successfully"
}
```

### Monitoring Endpoints

#### GET /monitoring/sessions
Get monitoring sessions for child.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `child_id` (optional): Filter by child
- `platform` (optional): Filter by platform
- `status` (optional): Filter by status
- `start_date` (optional): Filter by start date
- `end_date` (optional): Filter by end date
- `page` (optional): Page number
- `limit` (optional): Items per page

**Response (200):**
```json
{
  "sessions": ["Session"],
  "pagination": "object"
}
```

#### GET /monitoring/sessions/{session_id}
Get detailed session information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `session_id`: Session UUID

**Response (200):**
```json
{
  "session": "Session",
  "messages": ["Message"],
  "participants": ["object"],
  "risk_analysis": "object"
}
```

#### POST /monitoring/sessions/{session_id}/actions
Perform action on monitoring session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `session_id`: Session UUID

**Request Body:**
```json
{
  "action": "pause|resume|terminate|escalate",
  "reason": "string",
  "notes": "string"
}
```

**Response (200):**
```json
{
  "message": "Action performed successfully",
  "session": "Session"
}
```

### Alert Management Endpoints

#### GET /alerts
Get alerts for guardian.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `child_id` (optional): Filter by child
- `severity` (optional): Filter by severity
- `status` (optional): Filter by status
- `type` (optional): Filter by alert type
- `start_date` (optional): Filter by date range
- `end_date` (optional): Filter by date range
- `page` (optional): Page number
- `limit` (optional): Items per page

**Response (200):**
```json
{
  "alerts": ["Alert"],
  "pagination": "object",
  "summary": {
    "total": 150,
    "new": 5,
    "acknowledged": 10,
    "resolved": 135
  }
}
```

#### GET /alerts/{alert_id}
Get detailed alert information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `alert_id`: Alert UUID

**Response (200):**
```json
{
  "alert": "Alert",
  "related_messages": ["Message"],
  "evidence": "object",
  "recommendations": ["string"]
}
```

#### PUT /alerts/{alert_id}/status
Update alert status.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `alert_id`: Alert UUID

**Request Body:**
```json
{
  "status": "acknowledged|investigating|resolved|escalated",
  "notes": "string",
  "actions_taken": ["string"]
}
```

**Response (200):**
```json
{
  "alert": "Alert",
  "message": "Alert status updated successfully"
}
```

#### POST /alerts/{alert_id}/escalate
Escalate alert to authorities.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `alert_id`: Alert UUID

**Request Body:**
```json
{
  "escalation_type": "police|emergency|social_services",
  "urgency": "low|medium|high|critical",
  "notes": "string",
  "contact_preference": "phone|email|both"
}
```

**Response (200):**
```json
{
  "escalation_id": "uuid",
  "message": "Alert escalated successfully",
  "estimated_response_time": "string"
}
```

### Evidence Management Endpoints

#### GET /evidence/sessions/{session_id}
Get evidence package for session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `session_id`: Session UUID

**Query Parameters:**
- `format` (optional): Export format (json|pdf|xml)

**Response (200):**
```json
{
  "evidence_package": {
    "session_id": "uuid",
    "collected_at": "datetime",
    "chain_of_custody": ["object"],
    "messages": ["Message"],
    "metadata": "object",
    "integrity_hash": "string"
  }
}
```

#### POST /evidence/export
Export evidence for legal proceedings.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "session_ids": ["uuid"],
  "alert_ids": ["uuid"],
  "format": "pdf|json|xml",
  "include_metadata": "boolean",
  "purpose": "legal|investigation|reporting",
  "requester_info": {
    "name": "string",
    "organization": "string",
    "case_number": "string"
  }
}
```

**Response (200):**
```json
{
  "export_id": "uuid",
  "download_url": "string",
  "expires_at": "datetime",
  "file_size": "integer",
  "integrity_hash": "string"
}
```

### Real-time Communication Endpoints

#### WebSocket /ws/monitoring
Real-time monitoring updates.

**Connection Parameters:**
- `token`: JWT access token
- `child_id`: Child UUID to monitor

**Message Types:**

**Session Update:**
```json
{
  "type": "session_update",
  "data": {
    "session_id": "uuid",
    "status": "string",
    "risk_score": "float",
    "message_count": "integer"
  }
}
```

**New Alert:**
```json
{
  "type": "new_alert",
  "data": {
    "alert": "Alert",
    "requires_immediate_attention": "boolean"
  }
}
```

**Risk Score Update:**
```json
{
  "type": "risk_update",
  "data": {
    "session_id": "uuid",
    "previous_score": "float",
    "current_score": "float",
    "factors": ["string"]
  }
}
```

### Analytics Endpoints

#### GET /analytics/dashboard
Get dashboard analytics data.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period` (optional): Time period (day|week|month|year)
- `child_id` (optional): Filter by child

**Response (200):**
```json
{
  "summary": {
    "total_sessions": 150,
    "total_alerts": 25,
    "average_risk_score": 2.3,
    "platforms_monitored": 4
  },
  "trends": {
    "sessions_over_time": ["object"],
    "alerts_by_severity": ["object"],
    "risk_score_trend": ["object"]
  },
  "top_risks": [
    {
      "type": "string",
      "count": "integer",
      "percentage": "float"
    }
  ]
}
```

#### GET /analytics/reports
Get available reports.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "reports": [
    {
      "id": "monthly_summary",
      "name": "Monthly Safety Summary",
      "description": "string",
      "parameters": ["object"],
      "formats": ["pdf", "excel", "json"]
    }
  ]
}
```

#### POST /analytics/reports/{report_id}/generate
Generate analytics report.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `report_id`: Report identifier

**Request Body:**
```json
{
  "parameters": {
    "start_date": "date",
    "end_date": "date",
    "child_ids": ["uuid"],
    "include_details": "boolean"
  },
  "format": "pdf|excel|json",
  "delivery_method": "download|email"
}
```

**Response (202):**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "estimated_completion": "datetime"
}
```

### Administrative Endpoints

#### GET /admin/users
Get all users (admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `role` (optional): Filter by role
- `status` (optional): Filter by status
- `search` (optional): Search term
- `page` (optional): Page number
- `limit` (optional): Items per page

**Response (200):**
```json
{
  "users": ["User"],
  "pagination": "object"
}
```

#### GET /admin/system/health
Get system health status.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "healthy|degraded|unhealthy",
  "services": [
    {
      "name": "database",
      "status": "healthy",
      "response_time": "5ms",
      "last_check": "datetime"
    }
  ],
  "metrics": {
    "active_sessions": 1250,
    "alerts_last_hour": 15,
    "system_load": 0.65
  }
}
```

#### GET /admin/audit/logs
Get audit logs.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `user_id` (optional): Filter by user
- `action` (optional): Filter by action
- `resource` (optional): Filter by resource
- `start_date` (optional): Date range filter
- `end_date` (optional): Date range filter
- `page` (optional): Page number
- `limit` (optional): Items per page

**Response (200):**
```json
{
  "logs": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "action": "string",
      "resource": "string",
      "timestamp": "datetime",
      "ip_address": "string",
      "user_agent": "string",
      "details": "object"
    }
  ],
  "pagination": "object"
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object",
    "timestamp": "datetime",
    "request_id": "uuid"
  }
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Common Error Codes

- `AUTH_001`: Invalid credentials
- `AUTH_002`: Token expired
- `AUTH_003`: Insufficient permissions
- `VAL_001`: Validation error
- `VAL_002`: Required field missing
- `RES_001`: Resource not found
- `RES_002`: Resource already exists
- `RATE_001`: Rate limit exceeded
- `SYS_001`: Internal server error
- `SYS_002`: Service unavailable

## Rate Limiting

### Rate Limit Headers

All API responses include rate limiting headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
X-RateLimit-Window: 3600
```

### Rate Limit Tiers

- **Free Tier**: 100 requests/hour
- **Guardian Tier**: 1,000 requests/hour
- **Professional Tier**: 10,000 requests/hour
- **Enterprise Tier**: 100,000 requests/hour

## Webhooks

### Webhook Configuration

Webhooks can be configured to receive real-time notifications for critical events.

#### POST /webhooks
Configure webhook endpoint.

**Request Body:**
```json
{
  "url": "string",
  "events": ["alert.created", "session.flagged", "emergency.triggered"],
  "secret": "string",
  "active": "boolean"
}
```

### Webhook Events

#### Alert Created
```json
{
  "event": "alert.created",
  "timestamp": "datetime",
  "data": {
    "alert": "Alert",
    "child": "ChildProfile"
  }
}
```

#### Emergency Triggered
```json
{
  "event": "emergency.triggered",
  "timestamp": "datetime",
  "data": {
    "alert": "Alert",
    "child": "ChildProfile",
    "escalation_level": "critical"
  }
}
```

## SDK and Libraries

### Official SDKs

- **JavaScript/TypeScript**: `@safeguardian/js-sdk`
- **Python**: `safeguardian-python`
- **React Native**: `@safeguardian/react-native`
- **Swift**: `SafeGuardianSDK`
- **Kotlin**: `safeguardian-android`

### Example Usage (JavaScript)

```javascript
import { SafeGuardianClient } from '@safeguardian/js-sdk';

const client = new SafeGuardianClient({
  apiKey: 'your-api-key',
  environment: 'production'
});

// Get alerts
const alerts = await client.alerts.list({
  severity: 'high',
  status: 'new'
});

// Subscribe to real-time updates
client.monitoring.subscribe('child-123', (event) => {
  if (event.type === 'new_alert') {
    console.log('New alert:', event.data.alert);
  }
});
```

This comprehensive API specification provides the foundation for all SafeGuardian integrations and ensures consistent, secure, and reliable communication between all system components.

