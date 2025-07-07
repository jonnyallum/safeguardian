# SafeGuardian Technical Documentation

## Table of Contents

1. [System Architecture](#system-architecture)
2. [API Documentation](#api-documentation)
3. [Database Schema](#database-schema)
4. [Security Implementation](#security-implementation)
5. [AI/ML Components](#aiml-components)
6. [Real-time Monitoring](#real-time-monitoring)
7. [Alert System](#alert-system)
8. [Evidence Management](#evidence-management)
9. [WebSocket Communication](#websocket-communication)
10. [Development Guidelines](#development-guidelines)
11. [Testing Framework](#testing-framework)
12. [Performance Optimization](#performance-optimization)

## System Architecture

### Overview

SafeGuardian is built using a microservices architecture with the following core components:

- **Backend API Server** (Flask/Python)
- **Mobile Application** (React Native/JavaScript)
- **Web Dashboard** (React/JavaScript)
- **AI Detection Engine** (Python/TensorFlow)
- **Real-time Monitor** (Python/AsyncIO)
- **Alert Management System** (Python/AsyncIO)
- **Evidence Storage System** (Python/Cryptography)
- **WebSocket Server** (Python/SocketIO)

### Component Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │  Web Dashboard  │    │  Admin Panel    │
│   (React)       │    │   (React)       │    │   (React)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     API Gateway           │
                    │     (Nginx/Load Balancer) │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     Backend API Server    │
                    │     (Flask/Python)        │
                    └─────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────┴────────┐    ┌─────────┴─────────┐    ┌─────────┴─────────┐
│ AI Detection   │    │ Real-time Monitor │    │ Alert Management  │
│ Engine         │    │ (AsyncIO)         │    │ System            │
│ (TensorFlow)   │    │                   │    │ (AsyncIO)         │
└───────┬────────┘    └─────────┬─────────┘    └─────────┬─────────┘
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │   Data Layer        │
                    │                     │
                    │ ┌─────────────────┐ │
                    │ │   PostgreSQL    │ │
                    │ │   (Primary DB)  │ │
                    │ └─────────────────┘ │
                    │                     │
                    │ ┌─────────────────┐ │
                    │ │     Redis       │ │
                    │ │   (Cache/Queue) │ │
                    │ └─────────────────┘ │
                    │                     │
                    │ ┌─────────────────┐ │
                    │ │  File Storage   │ │
                    │ │  (Evidence)     │ │
                    │ └─────────────────┘ │
                    └─────────────────────┘
```

### Technology Stack

#### Backend Technologies
- **Framework:** Flask 2.3+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15+
- **Cache:** Redis 7.0+
- **Queue:** Celery with Redis
- **WebSocket:** Flask-SocketIO
- **Authentication:** JWT with Flask-JWT-Extended
- **Encryption:** Cryptography library (Fernet)

#### Frontend Technologies
- **Mobile App:** React Native 0.72+
- **Web Dashboard:** React 18+
- **State Management:** Redux Toolkit
- **UI Framework:** React Native Elements / Material-UI
- **Build Tool:** Vite (Web) / Metro (Mobile)
- **Testing:** Jest + React Testing Library

#### AI/ML Technologies
- **Framework:** TensorFlow 2.13+
- **NLP:** spaCy 3.6+, NLTK 3.8+
- **Text Analysis:** Transformers (Hugging Face)
- **Pattern Recognition:** scikit-learn 1.3+
- **Language Models:** Custom trained models + GPT integration

#### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Kubernetes (production)
- **Load Balancer:** Nginx
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **CI/CD:** GitHub Actions

### Data Flow Architecture

#### Message Processing Pipeline

```
Social Media Platform
         │
         ▼
Mobile App (Wrapper)
         │
         ▼
Real-time Monitor
         │
         ▼
AI Detection Engine
         │
         ▼
Risk Assessment
         │
    ┌────┴────┐
    ▼         ▼
Low Risk   High Risk
    │         │
    ▼         ▼
 Log Only   Generate Alert
              │
              ▼
         Alert Manager
              │
              ▼
         Evidence Collection
              │
              ▼
         Guardian Notification
```

#### Security Data Flow

```
User Request
     │
     ▼
Authentication Layer
     │
     ▼
Authorization Check
     │
     ▼
Rate Limiting
     │
     ▼
Input Validation
     │
     ▼
Business Logic
     │
     ▼
Data Encryption
     │
     ▼
Database Storage
     │
     ▼
Audit Logging
```

## API Documentation

### Authentication Endpoints

#### POST /api/auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "email": "guardian@example.com",
  "password": "securepassword",
  "device_info": {
    "device_type": "web",
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.100"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_123",
      "email": "guardian@example.com",
      "role": "guardian",
      "family_id": "family_456"
    },
    "expires_at": "2025-01-08T10:30:00Z"
  }
}
```

#### POST /api/auth/logout
Invalidate current session.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

#### POST /api/auth/refresh
Refresh JWT token.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2025-01-08T11:30:00Z"
  }
}
```

### User Management Endpoints

#### GET /api/users/profile
Get current user profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "guardian@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "guardian",
    "family_id": "family_456",
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-07T10:00:00Z",
    "preferences": {
      "notifications": {
        "email": true,
        "sms": true,
        "push": true
      },
      "alert_sensitivity": "medium"
    }
  }
}
```

#### PUT /api/users/profile
Update user profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "preferences": {
    "notifications": {
      "email": true,
      "sms": false,
      "push": true
    }
  }
}
```

### Family Management Endpoints

#### GET /api/families/current
Get current family information.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "family_456",
    "name": "The Doe Family",
    "created_at": "2025-01-01T00:00:00Z",
    "guardians": [
      {
        "id": "user_123",
        "name": "John Doe",
        "role": "primary_guardian",
        "email": "john@example.com"
      }
    ],
    "children": [
      {
        "id": "child_789",
        "name": "Jane Doe",
        "age": 14,
        "monitoring_status": "active"
      }
    ]
  }
}
```

#### POST /api/families/children
Add a new child to the family.

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "date_of_birth": "2010-05-15",
  "grade_level": "8th",
  "monitoring_preferences": {
    "sensitivity_level": "high",
    "platforms": ["instagram", "snapchat"],
    "content_filtering": true
  }
}
```

### Monitoring Endpoints

#### GET /api/monitoring/sessions
Get monitoring sessions for family children.

**Query Parameters:**
- `child_id` (optional): Filter by specific child
- `platform` (optional): Filter by platform
- `status` (optional): Filter by session status
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "session_123",
        "child_id": "child_789",
        "platform": "instagram",
        "status": "active",
        "started_at": "2025-01-07T09:00:00Z",
        "last_activity": "2025-01-07T10:30:00Z",
        "message_count": 15,
        "risk_level": "low"
      }
    ],
    "total": 1,
    "has_more": false
  }
}
```

#### POST /api/monitoring/sessions
Start a new monitoring session.

**Request Body:**
```json
{
  "child_id": "child_789",
  "platform": "instagram",
  "session_metadata": {
    "device_type": "mobile",
    "app_version": "1.0.0"
  }
}
```

#### PUT /api/monitoring/sessions/{session_id}/stop
Stop a monitoring session.

**Request Body:**
```json
{
  "reason": "User logged out",
  "final_metadata": {
    "total_messages": 25,
    "session_duration": 3600
  }
}
```

### Alert Management Endpoints

#### GET /api/alerts
Get alerts for the family.

**Query Parameters:**
- `status` (optional): Filter by alert status
- `severity` (optional): Filter by severity level
- `child_id` (optional): Filter by child
- `limit` (optional): Number of results
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": "alert_123",
        "type": "grooming_detection",
        "severity": "high",
        "status": "active",
        "child_id": "child_789",
        "platform": "instagram",
        "title": "Concerning conversation detected",
        "description": "AI detected potential grooming patterns",
        "created_at": "2025-01-07T10:15:00Z",
        "evidence_count": 3,
        "confidence_score": 0.87
      }
    ],
    "total": 1,
    "has_more": false
  }
}
```

#### GET /api/alerts/{alert_id}
Get detailed alert information.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "alert_123",
    "type": "grooming_detection",
    "severity": "high",
    "status": "active",
    "child_id": "child_789",
    "platform": "instagram",
    "title": "Concerning conversation detected",
    "description": "AI detected potential grooming patterns",
    "created_at": "2025-01-07T10:15:00Z",
    "updated_at": "2025-01-07T10:15:00Z",
    "evidence": [
      {
        "id": "evidence_456",
        "type": "message",
        "content_hash": "sha256:abc123...",
        "collected_at": "2025-01-07T10:15:00Z"
      }
    ],
    "ai_analysis": {
      "confidence_score": 0.87,
      "patterns_detected": ["trust_building", "isolation"],
      "risk_factors": [
        "Adult attempting to build trust with child",
        "Requests to keep conversation secret"
      ]
    },
    "actions_taken": []
  }
}
```

#### PUT /api/alerts/{alert_id}/status
Update alert status.

**Request Body:**
```json
{
  "status": "acknowledged",
  "notes": "Reviewed with child, situation resolved",
  "actions_taken": [
    "Spoke with child about online safety",
    "Blocked suspicious user"
  ]
}
```

### Evidence Management Endpoints

#### GET /api/evidence
Get evidence for the family.

**Query Parameters:**
- `case_id` (optional): Filter by case
- `child_id` (optional): Filter by child
- `type` (optional): Filter by evidence type
- `limit` (optional): Number of results
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "evidence": [
      {
        "id": "evidence_456",
        "case_id": "case_789",
        "type": "message",
        "platform": "instagram",
        "collected_at": "2025-01-07T10:15:00Z",
        "integrity_verified": true,
        "access_count": 2,
        "metadata": {
          "message_count": 1,
          "participants": 2,
          "risk_level": "high"
        }
      }
    ],
    "total": 1,
    "has_more": false
  }
}
```

#### GET /api/evidence/{evidence_id}
Get specific evidence details.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "evidence_456",
    "case_id": "case_789",
    "type": "message",
    "platform": "instagram",
    "collected_at": "2025-01-07T10:15:00Z",
    "integrity_verified": true,
    "chain_of_custody": [
      {
        "action": "collected",
        "timestamp": "2025-01-07T10:15:00Z",
        "actor": "system",
        "details": "Automatic collection triggered by AI alert"
      },
      {
        "action": "accessed",
        "timestamp": "2025-01-07T10:20:00Z",
        "actor": "user_123",
        "details": "Guardian reviewed evidence"
      }
    ],
    "content": {
      "encrypted": true,
      "access_url": "/api/evidence/456/content",
      "content_hash": "sha256:abc123...",
      "signature": "digital_signature_here"
    }
  }
}
```

#### GET /api/evidence/{evidence_id}/content
Access evidence content (requires special authorization).

**Headers:**
```
Authorization: Bearer <jwt_token>
X-Evidence-Access-Reason: Guardian review of concerning activity
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content": {
      "messages": [
        {
          "timestamp": "2025-01-07T10:10:00Z",
          "sender": "unknown_user_123",
          "recipient": "child_789",
          "content": "You're so mature for your age",
          "platform_message_id": "msg_456"
        }
      ],
      "metadata": {
        "conversation_id": "conv_789",
        "platform": "instagram",
        "participants": ["unknown_user_123", "child_789"]
      }
    },
    "access_logged": true
  }
}
```

### AI Analysis Endpoints

#### POST /api/ai/analyze/message
Analyze a single message for risk.

**Request Body:**
```json
{
  "message": {
    "content": "Hey, you're really mature for your age",
    "sender_age": 35,
    "recipient_age": 14,
    "platform": "instagram",
    "context": {
      "conversation_length": 5,
      "relationship": "unknown"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "risk_level": "medium",
    "confidence_score": 0.73,
    "patterns_detected": ["trust_building", "age_reference"],
    "risk_factors": [
      "Adult emphasizing child's maturity",
      "Potential trust-building language"
    ],
    "recommendations": [
      "Monitor conversation closely",
      "Consider discussing with child"
    ],
    "analysis_metadata": {
      "model_version": "v2.1.0",
      "processing_time_ms": 150,
      "analysis_id": "analysis_123"
    }
  }
}
```

#### POST /api/ai/analyze/conversation
Analyze a conversation thread.

**Request Body:**
```json
{
  "conversation": {
    "messages": [
      {
        "timestamp": "2025-01-07T10:00:00Z",
        "sender": "adult_user",
        "content": "Hi there!"
      },
      {
        "timestamp": "2025-01-07T10:01:00Z",
        "sender": "child_user",
        "content": "Hello"
      },
      {
        "timestamp": "2025-01-07T10:02:00Z",
        "sender": "adult_user",
        "content": "You're so mature for your age"
      }
    ],
    "participants": {
      "adult_user": {"age": 35, "relationship": "unknown"},
      "child_user": {"age": 14, "relationship": "self"}
    },
    "platform": "instagram"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_risk": "high",
    "confidence_score": 0.89,
    "escalation_detected": true,
    "patterns_detected": ["trust_building", "grooming_progression"],
    "message_analysis": [
      {
        "message_index": 0,
        "risk_level": "low",
        "patterns": []
      },
      {
        "message_index": 2,
        "risk_level": "medium",
        "patterns": ["trust_building"]
      }
    ],
    "recommendations": [
      "Immediate guardian notification required",
      "Consider blocking user",
      "Collect evidence for potential reporting"
    ]
  }
}
```

### WebSocket Events

#### Connection
```javascript
// Client connects to WebSocket
const socket = io('wss://api.safeguardian.com', {
  auth: {
    token: 'jwt_token_here'
  }
});
```

#### Real-time Alert
```javascript
// Server sends real-time alert
socket.emit('alert_created', {
  alert_id: 'alert_123',
  severity: 'high',
  child_id: 'child_789',
  title: 'Concerning conversation detected',
  timestamp: '2025-01-07T10:15:00Z'
});
```

#### Monitoring Status Update
```javascript
// Server sends monitoring status update
socket.emit('monitoring_update', {
  session_id: 'session_123',
  child_id: 'child_789',
  platform: 'instagram',
  status: 'active',
  message_count: 15,
  last_activity: '2025-01-07T10:30:00Z'
});
```

#### System Status
```javascript
// Server sends system status updates
socket.emit('system_status', {
  status: 'operational',
  services: {
    'ai_detection': 'operational',
    'monitoring': 'operational',
    'alerts': 'operational'
  },
  timestamp: '2025-01-07T10:30:00Z'
});
```

## Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role user_role NOT NULL DEFAULT 'guardian',
    status user_status NOT NULL DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    user_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE user_role AS ENUM (
    'child', 'guardian', 'family_admin', 
    'system_admin', 'law_enforcement', 'support'
);

CREATE TYPE user_status AS ENUM (
    'active', 'inactive', 'suspended', 'deleted'
);
```

#### families
```sql
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    primary_guardian_id UUID REFERENCES users(id),
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    subscription_status VARCHAR(50) DEFAULT 'active',
    billing_email VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### family_members
```sql
CREATE TABLE family_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role family_role NOT NULL,
    permissions JSONB DEFAULT '{}',
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMP WITH TIME ZONE,
    joined_at TIMESTAMP WITH TIME ZONE,
    status member_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(family_id, user_id)
);

CREATE TYPE family_role AS ENUM (
    'primary_guardian', 'guardian', 'emergency_contact'
);

CREATE TYPE member_status AS ENUM (
    'invited', 'active', 'inactive', 'removed'
);
```

#### child_profiles
```sql
CREATE TABLE child_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    date_of_birth DATE NOT NULL,
    grade_level VARCHAR(20),
    school_name VARCHAR(255),
    monitoring_status monitoring_status DEFAULT 'active',
    risk_level risk_level DEFAULT 'medium',
    monitoring_preferences JSONB DEFAULT '{}',
    emergency_contacts JSONB DEFAULT '[]',
    medical_info JSONB DEFAULT '{}',
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE monitoring_status AS ENUM (
    'active', 'paused', 'inactive'
);

CREATE TYPE risk_level AS ENUM (
    'low', 'medium', 'high', 'critical'
);
```

### Monitoring Tables

#### platform_connections
```sql
CREATE TABLE platform_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES child_profiles(id) ON DELETE CASCADE,
    platform platform_type NOT NULL,
    platform_user_id VARCHAR(255) NOT NULL,
    platform_username VARCHAR(255),
    connection_status connection_status DEFAULT 'active',
    oauth_token_encrypted TEXT,
    oauth_refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) DEFAULT 'ok',
    permissions JSONB DEFAULT '{}',
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(child_id, platform, platform_user_id)
);

CREATE TYPE platform_type AS ENUM (
    'instagram', 'snapchat', 'facebook', 'whatsapp', 
    'tiktok', 'discord', 'telegram'
);

CREATE TYPE connection_status AS ENUM (
    'active', 'inactive', 'error', 'revoked'
);
```

#### monitoring_sessions
```sql
CREATE TABLE monitoring_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES child_profiles(id) ON DELETE CASCADE,
    platform_connection_id UUID REFERENCES platform_connections(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    status session_status DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    device_info JSONB DEFAULT '{}',
    session_metadata JSONB DEFAULT '{}',
    message_count INTEGER DEFAULT 0,
    alert_count INTEGER DEFAULT 0,
    risk_score DECIMAL(3,2) DEFAULT 0.0,
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE session_status AS ENUM (
    'active', 'paused', 'ended', 'error'
);
```

#### messages
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES monitoring_sessions(id) ON DELETE CASCADE,
    platform_message_id VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255),
    sender_id VARCHAR(255) NOT NULL,
    recipient_id VARCHAR(255) NOT NULL,
    message_type message_type DEFAULT 'text',
    content_encrypted TEXT,
    content_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    platform platform_type NOT NULL,
    is_from_child BOOLEAN NOT NULL,
    risk_score DECIMAL(3,2) DEFAULT 0.0,
    ai_analysis_id UUID,
    flagged BOOLEAN DEFAULT FALSE,
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, platform_message_id)
);

CREATE TYPE message_type AS ENUM (
    'text', 'image', 'video', 'audio', 'file', 'location', 'contact'
);
```

### Alert Tables

#### alerts
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    child_id UUID REFERENCES child_profiles(id) ON DELETE CASCADE,
    session_id UUID REFERENCES monitoring_sessions(id),
    alert_type alert_type NOT NULL,
    severity severity_level NOT NULL,
    status alert_status DEFAULT 'active',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    platform platform_type,
    confidence_score DECIMAL(3,2),
    risk_factors JSONB DEFAULT '[]',
    evidence_ids JSONB DEFAULT '[]',
    ai_analysis JSONB DEFAULT '{}',
    escalation_level INTEGER DEFAULT 0,
    escalated_to JSONB DEFAULT '[]',
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE alert_type AS ENUM (
    'grooming_detection', 'inappropriate_content', 'cyberbullying',
    'self_harm', 'substance_abuse', 'meeting_request', 'location_sharing',
    'financial_request', 'technical_issue', 'system_alert'
);

CREATE TYPE severity_level AS ENUM (
    'low', 'medium', 'high', 'critical'
);

CREATE TYPE alert_status AS ENUM (
    'active', 'acknowledged', 'investigating', 'resolved', 'false_positive'
);
```

#### alert_notifications
```sql
CREATE TABLE alert_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    recipient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    status notification_status DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    response_received_at TIMESTAMP WITH TIME ZONE,
    delivery_attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE notification_type AS ENUM (
    'email', 'sms', 'push', 'webhook', 'phone_call'
);

CREATE TYPE notification_status AS ENUM (
    'pending', 'sent', 'delivered', 'read', 'failed', 'cancelled'
);
```

### Evidence Tables

#### evidence_cases
```sql
CREATE TABLE evidence_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    child_id UUID REFERENCES child_profiles(id) ON DELETE CASCADE,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    case_name VARCHAR(255) NOT NULL,
    case_type case_type DEFAULT 'grooming',
    priority case_priority DEFAULT 'medium',
    status case_status DEFAULT 'open',
    description TEXT,
    created_by UUID REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    law_enforcement_contact JSONB,
    legal_hold BOOLEAN DEFAULT FALSE,
    retention_until TIMESTAMP WITH TIME ZONE,
    case_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE case_type AS ENUM (
    'grooming', 'cyberbullying', 'inappropriate_content',
    'self_harm', 'substance_abuse', 'other'
);

CREATE TYPE case_priority AS ENUM (
    'low', 'medium', 'high', 'critical'
);

CREATE TYPE case_status AS ENUM (
    'open', 'investigating', 'evidence_collection', 
    'legal_review', 'closed', 'archived'
);
```

#### evidence
```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES evidence_cases(id) ON DELETE CASCADE,
    evidence_type evidence_type NOT NULL,
    source_type source_type NOT NULL,
    source_id VARCHAR(255),
    content_encrypted TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    digital_signature TEXT NOT NULL,
    collection_method VARCHAR(100) NOT NULL,
    collected_by VARCHAR(255) NOT NULL,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    integrity_verified BOOLEAN DEFAULT TRUE,
    chain_of_custody JSONB DEFAULT '[]',
    access_log JSONB DEFAULT '[]',
    retention_until TIMESTAMP WITH TIME ZONE,
    legal_hold BOOLEAN DEFAULT FALSE,
    evidence_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE evidence_type AS ENUM (
    'message', 'image', 'video', 'audio', 'file', 
    'conversation_thread', 'user_profile', 'system_log'
);

CREATE TYPE source_type AS ENUM (
    'instagram', 'snapchat', 'facebook', 'whatsapp',
    'tiktok', 'discord', 'system', 'manual'
);
```

### AI Analysis Tables

#### ai_analyses
```sql
CREATE TABLE ai_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_type analysis_type NOT NULL,
    target_type target_type NOT NULL,
    target_id UUID NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    risk_level risk_level NOT NULL,
    patterns_detected JSONB DEFAULT '[]',
    risk_factors JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    processing_time_ms INTEGER,
    analysis_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE analysis_type AS ENUM (
    'message_analysis', 'conversation_analysis', 'behavioral_analysis',
    'pattern_detection', 'risk_assessment'
);

CREATE TYPE target_type AS ENUM (
    'message', 'conversation', 'session', 'user_behavior'
);
```

### Indexes and Performance

#### Primary Indexes
```sql
-- User and family indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_status ON users(role, status);
CREATE INDEX idx_family_members_family_id ON family_members(family_id);
CREATE INDEX idx_child_profiles_family_id ON child_profiles(family_id);

-- Monitoring indexes
CREATE INDEX idx_monitoring_sessions_child_id ON monitoring_sessions(child_id);
CREATE INDEX idx_monitoring_sessions_status ON monitoring_sessions(status);
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_flagged ON messages(flagged) WHERE flagged = TRUE;

-- Alert indexes
CREATE INDEX idx_alerts_family_id ON alerts(family_id);
CREATE INDEX idx_alerts_child_id ON alerts(child_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);

-- Evidence indexes
CREATE INDEX idx_evidence_case_id ON evidence(case_id);
CREATE INDEX idx_evidence_type ON evidence(evidence_type);
CREATE INDEX idx_evidence_collected_at ON evidence(collected_at);

-- AI analysis indexes
CREATE INDEX idx_ai_analyses_target ON ai_analyses(target_type, target_id);
CREATE INDEX idx_ai_analyses_risk_level ON ai_analyses(risk_level);
CREATE INDEX idx_ai_analyses_created_at ON ai_analyses(created_at);
```

#### Composite Indexes
```sql
-- Performance optimization indexes
CREATE INDEX idx_messages_session_timestamp ON messages(session_id, timestamp);
CREATE INDEX idx_alerts_family_status_severity ON alerts(family_id, status, severity);
CREATE INDEX idx_monitoring_sessions_child_status ON monitoring_sessions(child_id, status);
CREATE INDEX idx_evidence_case_type_collected ON evidence(case_id, evidence_type, collected_at);
```

## Security Implementation

### Authentication and Authorization

#### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "user_123",
    "email": "guardian@example.com",
    "role": "guardian",
    "family_id": "family_456",
    "permissions": ["view_children", "manage_alerts"],
    "session_id": "session_789",
    "iat": 1704628800,
    "exp": 1704632400
  }
}
```

#### Role-Based Access Control (RBAC)

**Permission Matrix:**

| Resource | Child | Guardian | Family Admin | System Admin | Law Enforcement |
|----------|-------|----------|--------------|--------------|-----------------|
| Own Profile | Read/Write | Read/Write | Read/Write | Read/Write | Read |
| Child Profiles | Read Own | Read Family | Read/Write Family | Read/Write All | Read Authorized |
| Monitoring Data | None | Read Family | Read/Write Family | Read/Write All | Read Authorized |
| Alerts | None | Read/Ack Family | Read/Ack/Manage Family | Read/Ack/Manage All | Read Authorized |
| Evidence | None | Read Family | Read/Export Family | Read/Export/Manage All | Read/Export Authorized |
| System Settings | None | None | Family Settings | All Settings | None |

#### Security Middleware

```python
from functools import wraps
from flask import request, jsonify, g
import jwt
from datetime import datetime, timezone

def require_auth(required_permissions=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    return jsonify({'error': 'Invalid token format'}), 401
            
            if not token:
                return jsonify({'error': 'Token missing'}), 401
            
            try:
                # Decode JWT token
                payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
                
                # Validate session
                session_valid = security_manager.validate_session(
                    payload['session_id'], 
                    payload['user_id']
                )
                
                if not session_valid:
                    return jsonify({'error': 'Session invalid'}), 401
                
                # Check permissions
                if required_permissions:
                    user_permissions = set(payload.get('permissions', []))
                    required_perms = set(required_permissions)
                    
                    if not required_perms.issubset(user_permissions):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Store user context
                g.current_user = {
                    'user_id': payload['user_id'],
                    'role': payload['role'],
                    'family_id': payload.get('family_id'),
                    'permissions': payload.get('permissions', [])
                }
                
                return f(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
        
        return decorated_function
    return decorator

# Usage example
@app.route('/api/alerts')
@require_auth(['view_alerts'])
def get_alerts():
    family_id = g.current_user['family_id']
    alerts = Alert.query.filter_by(family_id=family_id).all()
    return jsonify([alert.to_dict() for alert in alerts])
```

### Data Encryption

#### Encryption at Rest

```python
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self, master_key=None):
        if master_key:
            self.cipher = Fernet(master_key)
        else:
            # Generate new key (store securely!)
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self.cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode('utf-8')
    
    def encrypt_json(self, data: dict) -> str:
        """Encrypt JSON data"""
        import json
        json_string = json.dumps(data, separators=(',', ':'))
        return self.encrypt_data(json_string)
    
    def decrypt_json(self, encrypted_data: str) -> dict:
        """Decrypt JSON data"""
        import json
        decrypted_string = self.decrypt_data(encrypted_data)
        return json.loads(decrypted_string)

# Database model with encryption
class EncryptedMessage(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    content_encrypted = db.Column(db.Text, nullable=False)
    content_hash = db.Column(db.String(64), nullable=False)
    
    def __init__(self, content: str):
        self.id = str(uuid.uuid4())
        
        # Encrypt content
        encryption = DataEncryption()
        self.content_encrypted = encryption.encrypt_data(content)
        
        # Generate hash for integrity verification
        import hashlib
        self.content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    def get_content(self) -> str:
        """Decrypt and return content"""
        encryption = DataEncryption()
        return encryption.decrypt_data(self.content_encrypted)
    
    def verify_integrity(self) -> bool:
        """Verify content integrity"""
        import hashlib
        current_content = self.get_content()
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()
        return current_hash == self.content_hash
```

#### Encryption in Transit

```nginx
# Nginx SSL Configuration
server {
    listen 443 ssl http2;
    server_name api.safeguardian.com;
    
    # SSL Certificate
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' wss:";
    
    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Security
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
    }
}
```

### Input Validation and Sanitization

```python
from marshmallow import Schema, fields, validate, ValidationError
from flask import request, jsonify

class MessageAnalysisSchema(Schema):
    message = fields.Nested(lambda: MessageSchema(), required=True)

class MessageSchema(Schema):
    content = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=10000),
        error_messages={'required': 'Message content is required'}
    )
    sender_age = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=120),
        error_messages={'required': 'Sender age is required'}
    )
    recipient_age = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=120),
        error_messages={'required': 'Recipient age is required'}
    )
    platform = fields.Str(
        required=True,
        validate=validate.OneOf(['instagram', 'snapchat', 'facebook', 'whatsapp']),
        error_messages={'required': 'Platform is required'}
    )
    context = fields.Nested(lambda: ContextSchema(), missing={})

class ContextSchema(Schema):
    conversation_length = fields.Int(validate=validate.Range(min=0))
    relationship = fields.Str(validate=validate.OneOf(['friend', 'family', 'unknown']))

def validate_input(schema_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            try:
                # Validate JSON input
                validated_data = schema.load(request.json)
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except ValidationError as err:
                return jsonify({
                    'success': False,
                    'error': 'Validation failed',
                    'details': err.messages
                }), 400
        return decorated_function
    return decorator

# Usage
@app.route('/api/ai/analyze/message', methods=['POST'])
@require_auth(['analyze_messages'])
@validate_input(MessageAnalysisSchema)
def analyze_message():
    data = request.validated_data
    # Process validated data
    result = ai_service.analyze_message(data['message'])
    return jsonify({'success': True, 'data': result})
```

### Rate Limiting and DDoS Protection

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Initialize rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["1000 per hour"]
)

# API-specific rate limits
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass

@app.route('/api/ai/analyze/message', methods=['POST'])
@limiter.limit("100 per minute")
@require_auth(['analyze_messages'])
def analyze_message():
    # Analysis logic
    pass

@app.route('/api/alerts', methods=['GET'])
@limiter.limit("200 per minute")
@require_auth(['view_alerts'])
def get_alerts():
    # Alert retrieval logic
    pass

# Custom rate limiting for authenticated users
def get_user_id():
    if hasattr(g, 'current_user'):
        return g.current_user['user_id']
    return get_remote_address()

@app.route('/api/evidence/<evidence_id>/content', methods=['GET'])
@limiter.limit("10 per minute", key_func=get_user_id)
@require_auth(['access_evidence'])
def get_evidence_content(evidence_id):
    # Evidence access logic with strict rate limiting
    pass
```

### Audit Logging

```python
import logging
from datetime import datetime, timezone
from flask import g, request
import json

class SecurityAuditLogger:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        # Configure audit logger
        audit_logger = logging.getLogger('security_audit')
        audit_logger.setLevel(logging.INFO)
        
        # File handler for audit logs
        handler = logging.FileHandler('/var/log/safeguardian/security_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        audit_logger.addHandler(handler)
        
        self.logger = audit_logger
    
    def log_authentication(self, user_id, email, success, ip_address, user_agent):
        """Log authentication attempts"""
        event = {
            'event_type': 'authentication',
            'user_id': user_id,
            'email': email,
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(event))
    
    def log_authorization(self, user_id, resource, action, success, reason=None):
        """Log authorization attempts"""
        event = {
            'event_type': 'authorization',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'success': success,
            'reason': reason,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(event))
    
    def log_data_access(self, user_id, data_type, data_id, action, reason=None):
        """Log sensitive data access"""
        event = {
            'event_type': 'data_access',
            'user_id': user_id,
            'data_type': data_type,
            'data_id': data_id,
            'action': action,
            'reason': reason,
            'ip_address': request.remote_addr if request else None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(json.dumps(event))
    
    def log_security_event(self, event_type, severity, details):
        """Log security events"""
        event = {
            'event_type': 'security_event',
            'security_event_type': event_type,
            'severity': severity,
            'details': details,
            'user_id': getattr(g, 'current_user', {}).get('user_id'),
            'ip_address': request.remote_addr if request else None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(level, json.dumps(event))

# Initialize audit logger
audit_logger = SecurityAuditLogger(app)

# Middleware to log all API requests
@app.before_request
def log_request():
    if request.endpoint and request.endpoint.startswith('api.'):
        audit_logger.log_security_event(
            'api_request',
            'info',
            {
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path,
                'user_agent': request.headers.get('User-Agent')
            }
        )
```

## AI/ML Components

### Grooming Detection Model

#### Model Architecture

The SafeGuardian AI system uses a multi-layered approach for detecting grooming patterns:

1. **Text Preprocessing Layer**
   - Tokenization and normalization
   - Emoji and slang translation
   - Context preservation

2. **Feature Extraction Layer**
   - TF-IDF vectorization
   - Word embeddings (Word2Vec/GloVe)
   - Transformer-based embeddings (BERT)

3. **Pattern Recognition Layer**
   - Predefined grooming pattern matching
   - Behavioral pattern analysis
   - Conversation flow analysis

4. **Risk Assessment Layer**
   - Multi-factor risk scoring
   - Confidence calculation
   - Escalation determination

#### Implementation

```python
import tensorflow as tf
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import List, Dict, Tuple
import re
import spacy

class GroomingDetectionModel:
    def __init__(self, model_path: str = None):
        # Load pre-trained transformer model
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = AutoModel.from_pretrained('bert-base-uncased')
        
        # Load spaCy for NLP processing
        self.nlp = spacy.load('en_core_web_sm')
        
        # Load custom classification model
        if model_path:
            self.classifier = tf.keras.models.load_model(model_path)
        else:
            self.classifier = self._build_classifier()
        
        # Grooming pattern definitions
        self.grooming_patterns = self._load_grooming_patterns()
        
        # Risk factors and weights
        self.risk_factors = {
            'age_gap': 0.3,
            'trust_building': 0.25,
            'isolation': 0.35,
            'sexual_content': 0.4,
            'meeting_request': 0.45,
            'gift_offer': 0.3,
            'secrecy_request': 0.35,
            'compliments_appearance': 0.2,
            'relationship_progression': 0.3
        }
    
    def _build_classifier(self):
        """Build the neural network classifier"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(512, activation='relu', input_shape=(768,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(4, activation='softmax')  # low, medium, high, critical
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _load_grooming_patterns(self) -> Dict[str, List[str]]:
        """Load predefined grooming patterns"""
        return {
            'trust_building': [
                r'\b(?:you\'?re|you are) (?:so )?(?:mature|smart|special|different)',
                r'\bnot like other (?:kids|children|girls|boys)',
                r'\byou understand me',
                r'\bwe have a special (?:connection|bond|relationship)',
                r'\byou\'?re (?:so )?wise for your age'
            ],
            'isolation': [
                r'\bdon\'?t tell (?:your )?(?:parents|mom|dad|family|anyone)',
                r'\bthis is (?:our|between us) (?:secret|little secret)',
                r'\bthey (?:wouldn\'?t|won\'?t) understand',
                r'\bkeep this (?:between us|private|secret)',
                r'\bnobody (?:needs to|has to) know'
            ],
            'sexual_content': [
                r'\b(?:sexy|hot|beautiful|gorgeous)\b',
                r'\bsend (?:me )?(?:a )?(?:pic|picture|photo)',
                r'\bshow me (?:your|yourself)',
                r'\bwhat are you wearing',
                r'\bare you alone'
            ],
            'meeting_request': [
                r'\bwant to meet',
                r'\blet\'?s meet (?:up|in person)',
                r'\bcome (?:over|to my place)',
                r'\bi\'?ll pick you up',
                r'\bmeet me at'
            ],
            'gift_offer': [
                r'\bi\'?ll (?:buy|get) you',
                r'\bwant (?:some )?(?:money|cash|gift)',
                r'\bi have (?:a )?(?:present|gift|surprise)',
                r'\bi\'?ll give you',
                r'\bfree (?:money|stuff|things)'
            ],
            'relationship_progression': [
                r'\bi love you',
                r'\byou\'?re my (?:girlfriend|boyfriend)',
                r'\bwe\'?re (?:dating|together)',
                r'\bi want to be with you',
                r'\byou mean everything to me'
            ]
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Handle common abbreviations and slang
        text = re.sub(r'\bu\b', 'you', text)
        text = re.sub(r'\bur\b', 'your', text)
        text = re.sub(r'\bc\b', 'see', text)
        text = re.sub(r'\br\b', 'are', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '...', text)
        
        return text
    
    def extract_features(self, text: str) -> np.ndarray:
        """Extract features from text using BERT"""
        # Tokenize text
        inputs = self.tokenizer(
            text,
            return_tensors='tf',
            max_length=512,
            truncation=True,
            padding=True
        )
        
        # Get BERT embeddings
        with tf.device('/CPU:0'):  # Use CPU for inference
            outputs = self.bert_model(**inputs)
            embeddings = outputs.last_hidden_state
            
            # Use CLS token embedding as sentence representation
            sentence_embedding = embeddings[:, 0, :].numpy()
        
        return sentence_embedding.flatten()
    
    def detect_patterns(self, text: str) -> Dict[str, List[str]]:
        """Detect grooming patterns in text"""
        detected_patterns = {}
        preprocessed_text = self.preprocess_text(text)
        
        for pattern_type, patterns in self.grooming_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, preprocessed_text, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                detected_patterns[pattern_type] = matches
        
        return detected_patterns
    
    def calculate_risk_score(self, text: str, sender_age: int, 
                           recipient_age: int, context: Dict = None) -> Dict:
        """Calculate comprehensive risk score"""
        # Extract features
        features = self.extract_features(text)
        
        # Get neural network prediction
        prediction = self.classifier.predict(features.reshape(1, -1))[0]
        risk_levels = ['low', 'medium', 'high', 'critical']
        predicted_risk = risk_levels[np.argmax(prediction)]
        confidence = float(np.max(prediction))
        
        # Detect patterns
        detected_patterns = self.detect_patterns(text)
        
        # Calculate age gap factor
        age_gap = abs(sender_age - recipient_age)
        age_gap_factor = min(age_gap / 10, 1.0) if age_gap > 5 else 0
        
        # Calculate pattern-based risk
        pattern_risk = 0
        for pattern_type in detected_patterns:
            if pattern_type in self.risk_factors:
                pattern_risk += self.risk_factors[pattern_type]
        
        # Combine factors
        total_risk = (confidence * 0.6) + (pattern_risk * 0.3) + (age_gap_factor * 0.1)
        total_risk = min(total_risk, 1.0)
        
        # Determine final risk level
        if total_risk >= 0.8:
            final_risk = 'critical'
        elif total_risk >= 0.6:
            final_risk = 'high'
        elif total_risk >= 0.3:
            final_risk = 'medium'
        else:
            final_risk = 'low'
        
        return {
            'risk_level': final_risk,
            'confidence_score': total_risk,
            'neural_network_prediction': predicted_risk,
            'neural_network_confidence': confidence,
            'patterns_detected': list(detected_patterns.keys()),
            'pattern_details': detected_patterns,
            'age_gap_factor': age_gap_factor,
            'risk_factors': {
                'neural_network': confidence * 0.6,
                'pattern_matching': pattern_risk * 0.3,
                'age_gap': age_gap_factor * 0.1
            }
        }
    
    def analyze_conversation_thread(self, messages: List[Dict]) -> Dict:
        """Analyze entire conversation thread for escalation patterns"""
        if not messages:
            return {'overall_risk': 'low', 'confidence_score': 0.0}
        
        message_analyses = []
        risk_progression = []
        
        for i, message in enumerate(messages):
            analysis = self.calculate_risk_score(
                message['content'],
                message.get('sender_age', 25),
                message.get('recipient_age', 14)
            )
            
            message_analyses.append({
                'message_index': i,
                'analysis': analysis
            })
            
            # Track risk progression
            risk_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            risk_progression.append(risk_levels[analysis['risk_level']])
        
        # Detect escalation
        escalation_detected = False
        if len(risk_progression) >= 3:
            # Check if risk is generally increasing
            recent_trend = risk_progression[-3:]
            if recent_trend[-1] > recent_trend[0]:
                escalation_detected = True
        
        # Calculate overall risk
        max_risk = max(risk_progression)
        avg_risk = sum(risk_progression) / len(risk_progression)
        
        # Determine overall risk level
        if max_risk >= 4 or (max_risk >= 3 and escalation_detected):
            overall_risk = 'critical'
        elif max_risk >= 3 or (max_risk >= 2 and escalation_detected):
            overall_risk = 'high'
        elif max_risk >= 2:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        # Calculate confidence
        confidence_score = min((avg_risk / 4) + (0.2 if escalation_detected else 0), 1.0)
        
        return {
            'overall_risk': overall_risk,
            'confidence_score': confidence_score,
            'escalation_detected': escalation_detected,
            'message_count': len(messages),
            'risk_progression': risk_progression,
            'message_analyses': message_analyses,
            'recommendations': self._generate_recommendations(overall_risk, escalation_detected)
        }
    
    def _generate_recommendations(self, risk_level: str, escalation_detected: bool) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                'Immediate guardian notification required',
                'Consider contacting law enforcement',
                'Block suspicious user immediately',
                'Collect and preserve all evidence',
                'Have immediate conversation with child about safety'
            ])
        elif risk_level == 'high':
            recommendations.extend([
                'Urgent guardian notification required',
                'Monitor conversation closely',
                'Consider blocking suspicious user',
                'Document all interactions',
                'Discuss online safety with child'
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                'Guardian notification recommended',
                'Continue monitoring conversation',
                'Review user profile and history',
                'Consider discussing with child'
            ])
        else:
            recommendations.extend([
                'Continue routine monitoring',
                'Log interaction for pattern analysis'
            ])
        
        if escalation_detected:
            recommendations.append('Escalation pattern detected - increase monitoring frequency')
        
        return recommendations

# Model training pipeline
class ModelTrainer:
    def __init__(self, model: GroomingDetectionModel):
        self.model = model
    
    def prepare_training_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from labeled dataset"""
        # Load and preprocess training data
        # This would load a dataset of labeled conversations
        # with risk levels: low=0, medium=1, high=2, critical=3
        pass
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                   validation_split: float = 0.2, epochs: int = 50):
        """Train the classification model"""
        # Convert labels to categorical
        y_train_categorical = tf.keras.utils.to_categorical(y_train, 4)
        
        # Train the model
        history = self.model.classifier.fit(
            X_train, y_train_categorical,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=32,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
                tf.keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5)
            ]
        )
        
        return history
    
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate model performance"""
        y_test_categorical = tf.keras.utils.to_categorical(y_test, 4)
        
        # Get predictions
        predictions = self.model.classifier.predict(X_test)
        predicted_classes = np.argmax(predictions, axis=1)
        
        # Calculate metrics
        from sklearn.metrics import classification_report, confusion_matrix
        
        report = classification_report(y_test, predicted_classes, output_dict=True)
        confusion = confusion_matrix(y_test, predicted_classes)
        
        return {
            'classification_report': report,
            'confusion_matrix': confusion.tolist(),
            'accuracy': report['accuracy'],
            'macro_avg_f1': report['macro avg']['f1-score']
        }
```

### Behavioral Analysis

```python
class BehavioralAnalyzer:
    def __init__(self):
        self.baseline_patterns = {}
        self.anomaly_threshold = 0.7
    
    def analyze_communication_patterns(self, user_id: str, 
                                     messages: List[Dict]) -> Dict:
        """Analyze user's communication patterns for anomalies"""
        if not messages:
            return {'anomaly_score': 0.0, 'patterns': {}}
        
        # Extract temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(messages)
        
        # Extract linguistic patterns
        linguistic_patterns = self._analyze_linguistic_patterns(messages)
        
        # Extract social patterns
        social_patterns = self._analyze_social_patterns(messages)
        
        # Compare with baseline
        baseline = self.baseline_patterns.get(user_id, {})
        anomaly_score = self._calculate_anomaly_score(
            temporal_patterns, linguistic_patterns, social_patterns, baseline
        )
        
        return {
            'anomaly_score': anomaly_score,
            'patterns': {
                'temporal': temporal_patterns,
                'linguistic': linguistic_patterns,
                'social': social_patterns
            },
            'anomalies_detected': anomaly_score > self.anomaly_threshold
        }
    
    def _analyze_temporal_patterns(self, messages: List[Dict]) -> Dict:
        """Analyze temporal communication patterns"""
        from datetime import datetime
        import pandas as pd
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(messages)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        return {
            'messages_per_hour': df['hour'].value_counts().to_dict(),
            'messages_per_day': df['day_of_week'].value_counts().to_dict(),
            'total_messages': len(messages),
            'avg_response_time': self._calculate_avg_response_time(messages),
            'late_night_activity': len(df[(df['hour'] >= 22) | (df['hour'] <= 6)])
        }
    
    def _analyze_linguistic_patterns(self, messages: List[Dict]) -> Dict:
        """Analyze linguistic patterns in messages"""
        all_text = ' '.join([msg['content'] for msg in messages])
        
        # Basic linguistic features
        word_count = len(all_text.split())
        char_count = len(all_text)
        avg_word_length = char_count / word_count if word_count > 0 else 0
        
        # Sentiment analysis
        sentiment_scores = []
        for message in messages:
            # Simple sentiment analysis (could use more sophisticated models)
            sentiment = self._analyze_sentiment(message['content'])
            sentiment_scores.append(sentiment)
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        return {
            'total_words': word_count,
            'avg_word_length': avg_word_length,
            'avg_message_length': word_count / len(messages) if messages else 0,
            'avg_sentiment': avg_sentiment,
            'sentiment_variance': np.var(sentiment_scores) if sentiment_scores else 0
        }
    
    def _analyze_social_patterns(self, messages: List[Dict]) -> Dict:
        """Analyze social interaction patterns"""
        # Count unique contacts
        contacts = set()
        for message in messages:
            if message.get('sender_id'):
                contacts.add(message['sender_id'])
            if message.get('recipient_id'):
                contacts.add(message['recipient_id'])
        
        # Analyze conversation initiations
        initiations = 0
        for i, message in enumerate(messages):
            if i == 0 or messages[i-1]['sender_id'] != message['sender_id']:
                initiations += 1
        
        return {
            'unique_contacts': len(contacts),
            'conversation_initiations': initiations,
            'avg_conversation_length': len(messages) / max(initiations, 1)
        }
    
    def _calculate_anomaly_score(self, temporal: Dict, linguistic: Dict, 
                                social: Dict, baseline: Dict) -> float:
        """Calculate anomaly score based on deviation from baseline"""
        if not baseline:
            return 0.0  # No baseline to compare against
        
        anomaly_factors = []
        
        # Temporal anomalies
        if 'temporal' in baseline:
            late_night_baseline = baseline['temporal'].get('late_night_activity', 0)
            late_night_current = temporal.get('late_night_activity', 0)
            if late_night_baseline > 0:
                late_night_ratio = late_night_current / late_night_baseline
                if late_night_ratio > 2:  # Significant increase in late night activity
                    anomaly_factors.append(0.3)
        
        # Linguistic anomalies
        if 'linguistic' in baseline:
            sentiment_baseline = baseline['linguistic'].get('avg_sentiment', 0)
            sentiment_current = linguistic.get('avg_sentiment', 0)
            sentiment_diff = abs(sentiment_current - sentiment_baseline)
            if sentiment_diff > 0.5:  # Significant sentiment change
                anomaly_factors.append(0.4)
        
        # Social anomalies
        if 'social' in baseline:
            contacts_baseline = baseline['social'].get('unique_contacts', 0)
            contacts_current = social.get('unique_contacts', 0)
            if contacts_baseline > 0:
                contacts_ratio = contacts_current / contacts_baseline
                if contacts_ratio > 1.5:  # Significant increase in contacts
                    anomaly_factors.append(0.3)
        
        return min(sum(anomaly_factors), 1.0)
```

### Model Performance Monitoring

```python
class ModelPerformanceMonitor:
    def __init__(self):
        self.performance_metrics = {}
        self.alert_thresholds = {
            'accuracy': 0.85,
            'precision': 0.80,
            'recall': 0.90,
            'f1_score': 0.85
        }
    
    def track_prediction(self, prediction_id: str, prediction: Dict, 
                        actual_outcome: str = None):
        """Track model predictions for performance monitoring"""
        self.performance_metrics[prediction_id] = {
            'prediction': prediction,
            'actual_outcome': actual_outcome,
            'timestamp': datetime.now(timezone.utc),
            'feedback_received': actual_outcome is not None
        }
    
    def calculate_performance_metrics(self, time_window_days: int = 30) -> Dict:
        """Calculate model performance metrics"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_window_days)
        
        # Filter recent predictions with feedback
        recent_predictions = [
            p for p in self.performance_metrics.values()
            if p['timestamp'] > cutoff_date and p['feedback_received']
        ]
        
        if not recent_predictions:
            return {'error': 'No feedback data available for performance calculation'}
        
        # Extract predictions and actual outcomes
        y_pred = [p['prediction']['risk_level'] for p in recent_predictions]
        y_true = [p['actual_outcome'] for p in recent_predictions]
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted'
        )
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'sample_size': len(recent_predictions),
            'time_window_days': time_window_days
        }
        
        # Check for performance degradation
        alerts = []
        for metric, value in metrics.items():
            if metric in self.alert_thresholds and value < self.alert_thresholds[metric]:
                alerts.append(f"{metric} below threshold: {value:.3f} < {self.alert_thresholds[metric]}")
        
        metrics['performance_alerts'] = alerts
        
        return metrics
    
    def retrain_recommendation(self) -> Dict:
        """Determine if model retraining is recommended"""
        metrics = self.calculate_performance_metrics()
        
        if 'error' in metrics:
            return {'retrain_recommended': False, 'reason': metrics['error']}
        
        # Check if any metric is below threshold
        needs_retraining = len(metrics['performance_alerts']) > 0
        
        # Check if sample size is sufficient for reliable metrics
        if metrics['sample_size'] < 100:
            needs_retraining = False
            reason = 'Insufficient feedback data for reliable assessment'
        else:
            reason = 'Performance metrics below acceptable thresholds' if needs_retraining else 'Performance within acceptable range'
        
        return {
            'retrain_recommended': needs_retraining,
            'reason': reason,
            'current_metrics': metrics
        }
```

## Real-time Monitoring

### Monitoring Architecture

The real-time monitoring system is built using Python's AsyncIO framework to handle concurrent monitoring sessions efficiently.

```python
import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import aioredis
from collections import defaultdict, deque

class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"

@dataclass
class MonitoringSession:
    session_id: str
    child_id: str
    platform: str
    status: SessionStatus
    started_at: datetime
    last_activity: datetime
    device_info: Dict
    message_count: int = 0
    alert_count: int = 0
    risk_score: float = 0.0
    metadata: Dict = None

@dataclass
class MessageEvent:
    message_id: str
    session_id: str
    platform_message_id: str
    sender_id: str
    recipient_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    is_from_child: bool
    metadata: Dict = None

class RealTimeMonitor:
    def __init__(self, ai_service=None, alert_service=None, 
                 evidence_service=None, redis_url="redis://localhost:6379"):
        self.ai_service = ai_service
        self.alert_service = alert_service
        self.evidence_service = evidence_service
        
        # Session management
        self.active_sessions: Dict[str, MonitoringSession] = {}
        self.session_queues: Dict[str, asyncio.Queue] = {}
        self.session_tasks: Dict[str, asyncio.Task] = {}
        
        # Message processing
        self.message_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.processing_stats = {
            'messages_processed': 0,
            'alerts_generated': 0,
            'sessions_active': 0,
            'start_time': datetime.now(timezone.utc)
        }
        
        # Redis for distributed coordination
        self.redis_url = redis_url
        self.redis_client = None
        
        # Configuration
        self.config = {
            'max_concurrent_sessions': 1000,
            'message_batch_size': 10,
            'processing_timeout': 30,
            'session_timeout': 1800,  # 30 minutes
            'risk_threshold_alert': 0.7
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
        
        logger.info("Real-time Monitor initialized")
    
    async def start_monitoring(self):
        """Start the real-time monitoring system"""
        if self.is_running:
            logger.warning("Real-time monitor is already running")
            return
        
        self.is_running = True
        logger.info("Starting real-time monitoring system...")
        
        # Initialize Redis connection
        self.redis_client = await aioredis.from_url(self.redis_url)
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._session_monitor()),
            asyncio.create_task(self._message_processor()),
            asyncio.create_task(self._statistics_updater()),
            asyncio.create_task(self._cleanup_task())
        ]
        
        logger.info("Real-time monitoring system started")
    
    async def stop_monitoring(self):
        """Stop the real-time monitoring system"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping real-time monitoring system...")
        
        # Stop all active sessions
        for session_id in list(self.active_sessions.keys()):
            await self.stop_session(session_id, "System shutdown")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Real-time monitoring system stopped")
    
    async def start_session(self, child_id: str, platform: str, 
                          device_info: Dict = None) -> str:
        """Start a new monitoring session"""
        if len(self.active_sessions) >= self.config['max_concurrent_sessions']:
            raise Exception("Maximum concurrent sessions reached")
        
        session_id = str(uuid.uuid4())
        
        session = MonitoringSession(
            session_id=session_id,
            child_id=child_id,
            platform=platform,
            status=SessionStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            device_info=device_info or {},
            metadata={}
        )
        
        # Store session
        self.active_sessions[session_id] = session
        self.session_queues[session_id] = asyncio.Queue()
        
        # Start session processing task
        self.session_tasks[session_id] = asyncio.create_task(
            self._process_session(session_id)
        )
        
        # Update statistics
        self.processing_stats['sessions_active'] = len(self.active_sessions)
        
        # Store in Redis for distributed coordination
        await self._store_session_in_redis(session)
        
        logger.info(f"Started monitoring session {session_id} for child {child_id} on {platform}")
        
        return session_id
    
    async def stop_session(self, session_id: str, reason: str = "Manual stop"):
        """Stop a monitoring session"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found")
            return
        
        session = self.active_sessions[session_id]
        session.status = SessionStatus.ENDED
        
        # Cancel session processing task
        if session_id in self.session_tasks:
            self.session_tasks[session_id].cancel()
            del self.session_tasks[session_id]
        
        # Clean up session data
        if session_id in self.session_queues:
            del self.session_queues[session_id]
        
        if session_id in self.message_buffer:
            del self.message_buffer[session_id]
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        # Update statistics
        self.processing_stats['sessions_active'] = len(self.active_sessions)
        
        # Remove from Redis
        await self._remove_session_from_redis(session_id)
        
        logger.info(f"Stopped monitoring session {session_id}: {reason}")
    
    async def process_message(self, session_id: str, message_data: Dict):
        """Process a new message from a monitoring session"""
        if session_id not in self.active_sessions:
            logger.warning(f"Message received for inactive session {session_id}")
            return
        
        session = self.active_sessions[session_id]
        
        # Create message event
        message_event = MessageEvent(
            message_id=str(uuid.uuid4()),
            session_id=session_id,
            platform_message_id=message_data.get('platform_message_id', ''),
            sender_id=message_data.get('sender_id', ''),
            recipient_id=message_data.get('recipient_id', ''),
            content=message_data.get('content', ''),
            message_type=MessageType(message_data.get('type', 'text')),
            timestamp=datetime.fromisoformat(message_data.get('timestamp', datetime.now(timezone.utc).isoformat())),
            is_from_child=message_data.get('is_from_child', False),
            metadata=message_data.get('metadata', {})
        )
        
        # Add to session queue for processing
        await self.session_queues[session_id].put(message_event)
        
        # Update session activity
        session.last_activity = datetime.now(timezone.utc)
        session.message_count += 1
        
        # Update statistics
        self.processing_stats['messages_processed'] += 1
    
    async def _process_session(self, session_id: str):
        """Process messages for a specific session"""
        try:
            while session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                if session.status != SessionStatus.ACTIVE:
                    break
                
                try:
                    # Get message from queue with timeout
                    message_event = await asyncio.wait_for(
                        self.session_queues[session_id].get(),
                        timeout=self.config['processing_timeout']
                    )
                    
                    # Process the message
                    await self._process_message_event(message_event)
                    
                except asyncio.TimeoutError:
                    # No messages received, continue monitoring
                    continue
                except Exception as e:
                    logger.error(f"Error processing message in session {session_id}: {str(e)}")
                    continue
        
        except asyncio.CancelledError:
            logger.info(f"Session processing cancelled for {session_id}")
        except Exception as e:
            logger.error(f"Session processing error for {session_id}: {str(e)}")
            # Mark session as error
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = SessionStatus.ERROR
    
    async def _process_message_event(self, message_event: MessageEvent):
        """Process an individual message event"""
        try:
            # Add to message buffer
            self.message_buffer[message_event.session_id].append(message_event)
            
            # Skip processing if message is from child (outgoing)
            if message_event.is_from_child:
                return
            
            # Analyze message with AI service
            if self.ai_service:
                analysis_result = await self._analyze_message_with_ai(message_event)
                
                # Check if alert should be generated
                if analysis_result.get('risk_level') in ['high', 'critical']:
                    await self._generate_alert(message_event, analysis_result)
                
                # Update session risk score
                session = self.active_sessions[message_event.session_id]
                session.risk_score = max(
                    session.risk_score, 
                    analysis_result.get('confidence_score', 0.0)
                )
            
            # Store message for evidence if flagged
            if message_event.content and self.evidence_service:
                await self._store_message_evidence(message_event)
        
        except Exception as e:
            logger.error(f"Error processing message event {message_event.message_id}: {str(e)}")
    
    async def _analyze_message_with_ai(self, message_event: MessageEvent) -> Dict:
        """Analyze message using AI service"""
        try:
            # Get conversation context
            recent_messages = list(self.message_buffer[message_event.session_id])[-10:]
            
            # Prepare analysis request
            analysis_request = {
                'message': {
                    'content': message_event.content,
                    'sender_age': 25,  # Default adult age
                    'recipient_age': 14,  # Default child age
                    'platform': message_event.session_id.split('_')[0] if '_' in message_event.session_id else 'unknown'
                },
                'context': {
                    'conversation_length': len(recent_messages),
                    'recent_messages': [
                        {
                            'content': msg.content,
                            'timestamp': msg.timestamp.isoformat(),
                            'is_from_child': msg.is_from_child
                        }
                        for msg in recent_messages[-5:]  # Last 5 messages for context
                    ]
                }
            }
            
            # Call AI service
            result = await self.ai_service.analyze_message(analysis_request)
            return result
        
        except Exception as e:
            logger.error(f"AI analysis failed for message {message_event.message_id}: {str(e)}")
            return {'risk_level': 'low', 'confidence_score': 0.0}
    
    async def _generate_alert(self, message_event: MessageEvent, analysis_result: Dict):
        """Generate alert for concerning message"""
        try:
            if not self.alert_service:
                return
            
            session = self.active_sessions[message_event.session_id]
            
            alert_data = {
                'type': 'grooming_detection',
                'severity': analysis_result['risk_level'],
                'title': f"Concerning message detected on {session.platform}",
                'description': f"AI detected {analysis_result['risk_level']} risk communication",
                'child_id': session.child_id,
                'session_id': message_event.session_id,
                'platform': session.platform,
                'confidence_score': analysis_result.get('confidence_score', 0.0),
                'patterns_detected': analysis_result.get('patterns_detected', []),
                'message_content_hash': hashlib.sha256(message_event.content.encode()).hexdigest(),
                'evidence_ids': [],
                'ai_analysis': analysis_result
            }
            
            alert_id = await self.alert_service.create_alert(alert_data)
            
            # Update session alert count
            session.alert_count += 1
            
            # Update statistics
            self.processing_stats['alerts_generated'] += 1
            
            logger.info(f"Generated alert {alert_id} for session {message_event.session_id}")
        
        except Exception as e:
            logger.error(f"Failed to generate alert for message {message_event.message_id}: {str(e)}")
    
    async def _store_message_evidence(self, message_event: MessageEvent):
        """Store message as evidence if needed"""
        try:
            if not self.evidence_service:
                return
            
            # Only store concerning messages as evidence
            session = self.active_sessions[message_event.session_id]
            if session.risk_score < self.config['risk_threshold_alert']:
                return
            
            evidence_data = {
                'type': 'message',
                'content': message_event.content,
                'source_platform': session.platform,
                'source_session': message_event.session_id,
                'metadata': {
                    'sender_id': message_event.sender_id,
                    'recipient_id': message_event.recipient_id,
                    'timestamp': message_event.timestamp.isoformat(),
                    'message_type': message_event.message_type.value,
                    'platform_message_id': message_event.platform_message_id
                }
            }
            
            evidence_id = await self.evidence_service.collect_evidence(
                session.child_id, evidence_data, 'system'
            )
            
            logger.info(f"Stored evidence {evidence_id} for message {message_event.message_id}")
        
        except Exception as e:
            logger.error(f"Failed to store evidence for message {message_event.message_id}: {str(e)}")
    
    async def _session_monitor(self):
        """Background task to monitor session health"""
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)
                timeout_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    # Check for session timeout
                    if current_time - session.last_activity > timedelta(seconds=self.config['session_timeout']):
                        timeout_sessions.append(session_id)
                
                # Stop timed out sessions
                for session_id in timeout_sessions:
                    await self.stop_session(session_id, "Session timeout")
                
                await asyncio.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"Error in session monitor: {str(e)}")
    
    async def _message_processor(self):
        """Background task for batch message processing"""
        while self.is_running:
            try:
                # Process any queued messages in batches
                for session_id in list(self.session_queues.keys()):
                    if session_id not in self.active_sessions:
                        continue
                    
                    queue = self.session_queues[session_id]
                    batch = []
                    
                    # Collect batch of messages
                    for _ in range(self.config['message_batch_size']):
                        try:
                            message = queue.get_nowait()
                            batch.append(message)
                        except asyncio.QueueEmpty:
                            break
                    
                    # Process batch if any messages
                    if batch:
                        await self._process_message_batch(batch)
                
                await asyncio.sleep(1)  # Process every second
            
            except Exception as e:
                logger.error(f"Error in message processor: {str(e)}")
    
    async def _process_message_batch(self, messages: List[MessageEvent]):
        """Process a batch of messages for efficiency"""
        try:
            # Group messages by session for context analysis
            session_groups = defaultdict(list)
            for message in messages:
                session_groups[message.session_id].append(message)
            
            # Process each session group
            for session_id, session_messages in session_groups.items():
                if session_id not in self.active_sessions:
                    continue
                
                # Analyze conversation thread if multiple messages
                if len(session_messages) > 1 and self.ai_service:
                    conversation_data = {
                        'messages': [
                            {
                                'content': msg.content,
                                'timestamp': msg.timestamp.isoformat(),
                                'sender': 'adult' if not msg.is_from_child else 'child'
                            }
                            for msg in session_messages
                        ]
                    }
                    
                    thread_analysis = await self.ai_service.analyze_conversation_thread(conversation_data)
                    
                    # Generate alert if thread shows escalation
                    if thread_analysis.get('escalation_detected'):
                        await self._generate_thread_alert(session_id, session_messages, thread_analysis)
        
        except Exception as e:
            logger.error(f"Error processing message batch: {str(e)}")
    
    async def _generate_thread_alert(self, session_id: str, messages: List[MessageEvent], analysis: Dict):
        """Generate alert for concerning conversation thread"""
        try:
            if not self.alert_service:
                return
            
            session = self.active_sessions[session_id]
            
            alert_data = {
                'type': 'grooming_detection',
                'severity': analysis.get('overall_risk', 'medium'),
                'title': f"Conversation escalation detected on {session.platform}",
                'description': f"AI detected escalating risk pattern in conversation thread",
                'child_id': session.child_id,
                'session_id': session_id,
                'platform': session.platform,
                'confidence_score': analysis.get('confidence_score', 0.0),
                'message_count': len(messages),
                'escalation_detected': True,
                'ai_analysis': analysis
            }
            
            alert_id = await self.alert_service.create_alert(alert_data)
            logger.info(f"Generated thread escalation alert {alert_id} for session {session_id}")
        
        except Exception as e:
            logger.error(f"Failed to generate thread alert for session {session_id}: {str(e)}")
    
    async def _statistics_updater(self):
        """Background task to update monitoring statistics"""
        while self.is_running:
            try:
                # Update active session count
                self.processing_stats['sessions_active'] = len(self.active_sessions)
                
                # Store statistics in Redis
                await self._store_statistics_in_redis()
                
                await asyncio.sleep(30)  # Update every 30 seconds
            
            except Exception as e:
                logger.error(f"Error updating statistics: {str(e)}")
    
    async def _cleanup_task(self):
        """Background task for cleanup operations"""
        while self.is_running:
            try:
                # Clean up old message buffers
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
                
                for session_id, messages in self.message_buffer.items():
                    # Remove old messages
                    while messages and messages[0].timestamp < cutoff_time:
                        messages.popleft()
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
            
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
    
    async def _store_session_in_redis(self, session: MonitoringSession):
        """Store session information in Redis for distributed coordination"""
        try:
            if self.redis_client:
                session_data = asdict(session)
                session_data['started_at'] = session.started_at.isoformat()
                session_data['last_activity'] = session.last_activity.isoformat()
                
                await self.redis_client.hset(
                    f"session:{session.session_id}",
                    mapping=session_data
                )
                await self.redis_client.expire(f"session:{session.session_id}", 3600)
        
        except Exception as e:
            logger.error(f"Failed to store session in Redis: {str(e)}")
    
    async def _remove_session_from_redis(self, session_id: str):
        """Remove session from Redis"""
        try:
            if self.redis_client:
                await self.redis_client.delete(f"session:{session_id}")
        
        except Exception as e:
            logger.error(f"Failed to remove session from Redis: {str(e)}")
    
    async def _store_statistics_in_redis(self):
        """Store monitoring statistics in Redis"""
        try:
            if self.redis_client:
                stats = self.processing_stats.copy()
                stats['start_time'] = stats['start_time'].isoformat()
                stats['last_updated'] = datetime.now(timezone.utc).isoformat()
                
                await self.redis_client.hset("monitoring:stats", mapping=stats)
                await self.redis_client.expire("monitoring:stats", 300)
        
        except Exception as e:
            logger.error(f"Failed to store statistics in Redis: {str(e)}")
    
    # Public API methods
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get status of a monitoring session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        return {
            'session_id': session.session_id,
            'child_id': session.child_id,
            'platform': session.platform,
            'status': session.status.value,
            'started_at': session.started_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'message_count': session.message_count,
            'alert_count': session.alert_count,
            'risk_score': session.risk_score
        }
    
    def get_all_sessions(self) -> List[Dict]:
        """Get status of all active sessions"""
        return [
            self.get_session_status(session_id)
            for session_id in self.active_sessions.keys()
        ]
    
    def get_statistics(self) -> Dict:
        """Get monitoring system statistics"""
        stats = self.processing_stats.copy()
        stats['start_time'] = stats['start_time'].isoformat()
        stats['uptime_seconds'] = (datetime.now(timezone.utc) - self.processing_stats['start_time']).total_seconds()
        return stats

# Factory function
def create_real_time_monitor(ai_service=None, alert_service=None, 
                           evidence_service=None, redis_url="redis://localhost:6379"):
    """Create a new real-time monitor instance"""
    return RealTimeMonitor(ai_service, alert_service, evidence_service, redis_url)
```

This comprehensive technical documentation covers all the major components of the SafeGuardian system. The documentation includes detailed API specifications, database schemas, security implementations, AI/ML components, and real-time monitoring architecture. This serves as a complete reference for developers, system administrators, and technical stakeholders working with the SafeGuardian platform.

