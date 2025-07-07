# SafeGuardian Database Schema Design

## Overview

The SafeGuardian database schema is designed to support a comprehensive child protection monitoring system with robust security, audit capabilities, and scalable performance. The schema implements a normalized relational design with appropriate indexing, constraints, and security measures to ensure data integrity and compliance with privacy regulations.

## Database Technology

**Primary Database**: PostgreSQL 14+
- ACID compliance for data integrity
- Advanced indexing capabilities (B-tree, GIN, GIST)
- JSON/JSONB support for flexible metadata storage
- Row-level security for multi-tenant isolation
- Advanced encryption capabilities
- Comprehensive audit logging support

**Caching Layer**: Redis 7+
- Session storage and management
- Real-time data caching
- Rate limiting counters
- Temporary data storage

**Search Engine**: Elasticsearch 8+
- Full-text search capabilities
- Log aggregation and analysis
- Real-time analytics
- Alert correlation

## Core Tables

### Users Table

The users table serves as the central identity management system for all SafeGuardian participants.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role NOT NULL DEFAULT 'guardian',
    family_id UUID REFERENCES families(id) ON DELETE SET NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP,
    phone_verified_at TIMESTAMP,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(32),
    backup_codes TEXT[],
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Custom enum for user roles
CREATE TYPE user_role AS ENUM (
    'guardian',
    'child',
    'admin',
    'law_enforcement',
    'support',
    'system'
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_family_id ON users(family_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at);

-- Partial index for active users
CREATE INDEX idx_users_active_email ON users(email) WHERE is_active = true AND deleted_at IS NULL;
```

### Families Table

The families table groups related users and provides organizational structure for monitoring relationships.

```sql
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    family_code VARCHAR(20) UNIQUE NOT NULL,
    primary_guardian_id UUID REFERENCES users(id) ON DELETE SET NULL,
    subscription_tier subscription_tier DEFAULT 'free',
    subscription_status subscription_status DEFAULT 'active',
    subscription_expires_at TIMESTAMP,
    billing_email VARCHAR(255),
    settings JSONB DEFAULT '{}',
    emergency_contacts JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Custom enums for subscription management
CREATE TYPE subscription_tier AS ENUM (
    'free',
    'basic',
    'premium',
    'enterprise'
);

CREATE TYPE subscription_status AS ENUM (
    'active',
    'suspended',
    'cancelled',
    'expired'
);

-- Indexes
CREATE INDEX idx_families_code ON families(family_code);
CREATE INDEX idx_families_guardian ON families(primary_guardian_id);
CREATE INDEX idx_families_subscription ON families(subscription_tier, subscription_status);
```

### Child Profiles Table

The child_profiles table stores detailed information about children being monitored.

```sql
CREATE TABLE child_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    guardian_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date_of_birth DATE NOT NULL,
    grade_level VARCHAR(20),
    school_name VARCHAR(255),
    medical_conditions TEXT[],
    allergies TEXT[],
    emergency_contacts JSONB DEFAULT '[]',
    monitoring_settings JSONB DEFAULT '{}',
    risk_profile JSONB DEFAULT '{}',
    parental_controls JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_child_age CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '5 years'),
    CONSTRAINT chk_child_future_birth CHECK (date_of_birth >= CURRENT_DATE - INTERVAL '18 years')
);

-- Indexes
CREATE INDEX idx_child_profiles_user_id ON child_profiles(user_id);
CREATE INDEX idx_child_profiles_guardian_id ON child_profiles(guardian_id);
CREATE INDEX idx_child_profiles_age ON child_profiles(date_of_birth);
```

### Platform Connections Table

The platform_connections table manages OAuth connections to social media platforms.

```sql
CREATE TABLE platform_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES child_profiles(id) ON DELETE CASCADE,
    platform platform_type NOT NULL,
    platform_user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    display_name VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    permissions TEXT[],
    is_active BOOLEAN DEFAULT true,
    monitoring_enabled BOOLEAN DEFAULT true,
    last_sync TIMESTAMP,
    sync_status sync_status DEFAULT 'pending',
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint per child per platform
    UNIQUE(child_id, platform, platform_user_id)
);

-- Custom enums
CREATE TYPE platform_type AS ENUM (
    'facebook',
    'instagram',
    'snapchat',
    'tiktok',
    'discord',
    'whatsapp',
    'telegram',
    'twitter',
    'youtube'
);

CREATE TYPE sync_status AS ENUM (
    'pending',
    'syncing',
    'completed',
    'failed',
    'paused'
);

-- Indexes
CREATE INDEX idx_platform_connections_child ON platform_connections(child_id);
CREATE INDEX idx_platform_connections_platform ON platform_connections(platform);
CREATE INDEX idx_platform_connections_active ON platform_connections(is_active, monitoring_enabled);
CREATE INDEX idx_platform_connections_sync ON platform_connections(last_sync, sync_status);
```

### Monitoring Sessions Table

The monitoring_sessions table tracks individual monitoring sessions across platforms.

```sql
CREATE TABLE monitoring_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES child_profiles(id) ON DELETE CASCADE,
    platform_connection_id UUID REFERENCES platform_connections(id) ON DELETE CASCADE,
    session_type session_type DEFAULT 'messaging',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status session_status DEFAULT 'active',
    risk_score DECIMAL(3,2) DEFAULT 0.00,
    message_count INTEGER DEFAULT 0,
    participant_count INTEGER DEFAULT 0,
    location_data JSONB,
    device_info JSONB,
    app_version VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_risk_score CHECK (risk_score >= 0.00 AND risk_score <= 10.00),
    CONSTRAINT chk_session_duration CHECK (end_time IS NULL OR end_time >= start_time)
);

-- Custom enums
CREATE TYPE session_type AS ENUM (
    'messaging',
    'video_call',
    'voice_call',
    'group_chat',
    'live_stream',
    'gaming',
    'browsing'
);

CREATE TYPE session_status AS ENUM (
    'active',
    'completed',
    'paused',
    'terminated',
    'flagged',
    'emergency'
);

-- Indexes
CREATE INDEX idx_sessions_child ON monitoring_sessions(child_id);
CREATE INDEX idx_sessions_platform ON monitoring_sessions(platform_connection_id);
CREATE INDEX idx_sessions_status ON monitoring_sessions(status);
CREATE INDEX idx_sessions_risk_score ON monitoring_sessions(risk_score DESC);
CREATE INDEX idx_sessions_time_range ON monitoring_sessions(start_time, end_time);
CREATE INDEX idx_sessions_active ON monitoring_sessions(status, start_time) WHERE status = 'active';
```

### Session Participants Table

The session_participants table tracks all participants in monitoring sessions.

```sql
CREATE TABLE session_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES monitoring_sessions(id) ON DELETE CASCADE,
    platform_user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    display_name VARCHAR(255),
    role participant_role DEFAULT 'participant',
    risk_level risk_level DEFAULT 'unknown',
    first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    age_estimate INTEGER,
    location_estimate VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint per session per participant
    UNIQUE(session_id, platform_user_id)
);

-- Custom enums
CREATE TYPE participant_role AS ENUM (
    'child',
    'participant',
    'moderator',
    'admin',
    'bot'
);

CREATE TYPE risk_level AS ENUM (
    'unknown',
    'low',
    'medium',
    'high',
    'critical'
);

-- Indexes
CREATE INDEX idx_participants_session ON session_participants(session_id);
CREATE INDEX idx_participants_risk ON session_participants(risk_level);
CREATE INDEX idx_participants_platform_user ON session_participants(platform_user_id);
```

### Messages Table

The messages table stores all monitored communications with comprehensive metadata.

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES monitoring_sessions(id) ON DELETE CASCADE,
    platform_message_id VARCHAR(255),
    sender_platform_id VARCHAR(255) NOT NULL,
    recipient_platform_id VARCHAR(255),
    content TEXT,
    content_type content_type DEFAULT 'text',
    content_hash VARCHAR(64),
    timestamp TIMESTAMP NOT NULL,
    edited_at TIMESTAMP,
    deleted_at TIMESTAMP,
    is_encrypted BOOLEAN DEFAULT false,
    encryption_method VARCHAR(50),
    attachments JSONB DEFAULT '[]',
    mentions JSONB DEFAULT '[]',
    hashtags TEXT[],
    urls TEXT[],
    location_data JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint for platform messages
    UNIQUE(session_id, platform_message_id)
);

-- Custom enum
CREATE TYPE content_type AS ENUM (
    'text',
    'image',
    'video',
    'audio',
    'file',
    'sticker',
    'gif',
    'location',
    'contact',
    'poll',
    'story'
);

-- Indexes
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_sender ON messages(sender_platform_id);
CREATE INDEX idx_messages_content_type ON messages(content_type);
CREATE INDEX idx_messages_content_hash ON messages(content_hash);
CREATE INDEX idx_messages_platform_id ON messages(platform_message_id);

-- Full-text search index
CREATE INDEX idx_messages_content_search ON messages USING gin(to_tsvector('english', content));
```

### AI Analysis Table

The ai_analysis table stores AI-generated analysis results for messages and sessions.

```sql
CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    session_id UUID REFERENCES monitoring_sessions(id) ON DELETE CASCADE,
    analysis_type analysis_type NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    risk_score DECIMAL(3,2) NOT NULL,
    sentiment sentiment_type,
    intent VARCHAR(255),
    entities JSONB DEFAULT '[]',
    topics JSONB DEFAULT '[]',
    language VARCHAR(10),
    toxicity_score DECIMAL(5,4),
    grooming_indicators JSONB DEFAULT '[]',
    risk_factors JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    raw_output JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_confidence_score CHECK (confidence_score >= 0.0000 AND confidence_score <= 1.0000),
    CONSTRAINT chk_risk_score CHECK (risk_score >= 0.00 AND risk_score <= 10.00),
    CONSTRAINT chk_toxicity_score CHECK (toxicity_score >= 0.0000 AND toxicity_score <= 1.0000),
    CONSTRAINT chk_analysis_target CHECK (
        (message_id IS NOT NULL AND session_id IS NULL) OR 
        (message_id IS NULL AND session_id IS NOT NULL)
    )
);

-- Custom enums
CREATE TYPE analysis_type AS ENUM (
    'grooming_detection',
    'sentiment_analysis',
    'intent_classification',
    'entity_extraction',
    'toxicity_detection',
    'age_verification',
    'risk_assessment'
);

CREATE TYPE sentiment_type AS ENUM (
    'positive',
    'negative',
    'neutral',
    'mixed'
);

-- Indexes
CREATE INDEX idx_ai_analysis_message ON ai_analysis(message_id);
CREATE INDEX idx_ai_analysis_session ON ai_analysis(session_id);
CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);
CREATE INDEX idx_ai_analysis_risk_score ON ai_analysis(risk_score DESC);
CREATE INDEX idx_ai_analysis_confidence ON ai_analysis(confidence_score DESC);
CREATE INDEX idx_ai_analysis_model ON ai_analysis(model_name, model_version);
```

### Alerts Table

The alerts table manages all system-generated alerts and notifications.

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES monitoring_sessions(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    child_id UUID REFERENCES child_profiles(id) ON DELETE CASCADE,
    guardian_id UUID REFERENCES users(id) ON DELETE CASCADE,
    alert_type alert_type NOT NULL,
    severity alert_severity NOT NULL,
    status alert_status DEFAULT 'new',
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    risk_score DECIMAL(3,2) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    triggered_by JSONB NOT NULL,
    evidence JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '[]',
    false_positive BOOLEAN,
    false_positive_reason TEXT,
    acknowledged_at TIMESTAMP,
    acknowledged_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    resolved_by UUID REFERENCES users(id),
    escalated_at TIMESTAMP,
    escalated_to VARCHAR(255),
    escalation_reference VARCHAR(255),
    actions_taken JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_alert_risk_score CHECK (risk_score >= 0.00 AND risk_score <= 10.00),
    CONSTRAINT chk_alert_confidence CHECK (confidence_score >= 0.0000 AND confidence_score <= 1.0000)
);

-- Custom enums
CREATE TYPE alert_type AS ENUM (
    'grooming_detected',
    'inappropriate_content',
    'stranger_contact',
    'personal_info_request',
    'meeting_request',
    'suspicious_behavior',
    'cyberbullying',
    'self_harm_indicators',
    'emergency_keywords',
    'platform_violation'
);

CREATE TYPE alert_severity AS ENUM (
    'low',
    'medium',
    'high',
    'critical',
    'emergency'
);

CREATE TYPE alert_status AS ENUM (
    'new',
    'acknowledged',
    'investigating',
    'resolved',
    'escalated',
    'false_positive',
    'dismissed'
);

-- Indexes
CREATE INDEX idx_alerts_session ON alerts(session_id);
CREATE INDEX idx_alerts_child ON alerts(child_id);
CREATE INDEX idx_alerts_guardian ON alerts(guardian_id);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_risk_score ON alerts(risk_score DESC);
CREATE INDEX idx_alerts_unresolved ON alerts(status, created_at) WHERE status IN ('new', 'acknowledged', 'investigating');
```

### Evidence Table

The evidence table provides forensic-grade evidence storage with chain of custody tracking.

```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    session_id UUID REFERENCES monitoring_sessions(id) ON DELETE CASCADE,
    evidence_type evidence_type NOT NULL,
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size BIGINT,
    mime_type VARCHAR(100),
    hash_algorithm VARCHAR(20) DEFAULT 'SHA-256',
    file_hash VARCHAR(128) NOT NULL,
    encryption_key_id VARCHAR(255),
    is_encrypted BOOLEAN DEFAULT true,
    chain_of_custody JSONB DEFAULT '[]',
    collection_method VARCHAR(100) NOT NULL,
    collection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    collected_by UUID REFERENCES users(id),
    integrity_verified BOOLEAN DEFAULT false,
    integrity_check_timestamp TIMESTAMP,
    legal_hold BOOLEAN DEFAULT false,
    retention_until TIMESTAMP,
    access_log JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_file_size CHECK (file_size >= 0),
    CONSTRAINT chk_retention_date CHECK (retention_until > created_at)
);

-- Custom enum
CREATE TYPE evidence_type AS ENUM (
    'message_screenshot',
    'conversation_export',
    'media_file',
    'session_recording',
    'system_log',
    'ai_analysis_report',
    'user_profile_data',
    'metadata_export'
);

-- Indexes
CREATE INDEX idx_evidence_alert ON evidence(alert_id);
CREATE INDEX idx_evidence_session ON evidence(session_id);
CREATE INDEX idx_evidence_type ON evidence(evidence_type);
CREATE INDEX idx_evidence_hash ON evidence(file_hash);
CREATE INDEX idx_evidence_legal_hold ON evidence(legal_hold) WHERE legal_hold = true;
CREATE INDEX idx_evidence_retention ON evidence(retention_until) WHERE retention_until IS NOT NULL;
```

### Audit Log Table

The audit_log table provides comprehensive system activity tracking for compliance and security.

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    action audit_action NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(255),
    success BOOLEAN NOT NULL,
    error_message TEXT,
    risk_level audit_risk_level DEFAULT 'low',
    compliance_flags TEXT[],
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Partitioning key for performance
    created_date DATE GENERATED ALWAYS AS (timestamp::date) STORED
);

-- Custom enums
CREATE TYPE audit_action AS ENUM (
    'login',
    'logout',
    'create',
    'read',
    'update',
    'delete',
    'export',
    'escalate',
    'acknowledge',
    'resolve',
    'access_evidence',
    'change_permissions',
    'system_config'
);

CREATE TYPE audit_risk_level AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Indexes
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_risk ON audit_log(risk_level) WHERE risk_level IN ('high', 'critical');
CREATE INDEX idx_audit_log_ip ON audit_log(ip_address);

-- Partition by date for performance
CREATE TABLE audit_log_y2024m01 PARTITION OF audit_log
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### Notifications Table

The notifications table manages all system notifications and delivery tracking.

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES alerts(id) ON DELETE SET NULL,
    notification_type notification_type NOT NULL,
    channel notification_channel NOT NULL,
    priority notification_priority DEFAULT 'normal',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    scheduled_for TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    status notification_status DEFAULT 'pending',
    delivery_attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    external_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_delivery_attempts CHECK (delivery_attempts >= 0),
    CONSTRAINT chk_max_attempts CHECK (max_attempts > 0)
);

-- Custom enums
CREATE TYPE notification_type AS ENUM (
    'alert',
    'reminder',
    'system_update',
    'security_notice',
    'welcome',
    'verification',
    'report_ready',
    'emergency'
);

CREATE TYPE notification_channel AS ENUM (
    'email',
    'sms',
    'push',
    'in_app',
    'voice_call',
    'webhook'
);

CREATE TYPE notification_priority AS ENUM (
    'low',
    'normal',
    'high',
    'urgent',
    'emergency'
);

CREATE TYPE notification_status AS ENUM (
    'pending',
    'sent',
    'delivered',
    'failed',
    'cancelled'
);

-- Indexes
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_alert ON notifications(alert_id);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_channel ON notifications(channel);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_scheduled ON notifications(scheduled_for) WHERE status = 'pending';
CREATE INDEX idx_notifications_priority ON notifications(priority, scheduled_for);
```

## Security and Encryption

### Row-Level Security (RLS)

PostgreSQL Row-Level Security is implemented to ensure data isolation between families and appropriate access controls.

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE child_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE monitoring_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;

-- Example RLS policy for users table
CREATE POLICY user_isolation ON users
    FOR ALL
    TO application_role
    USING (
        family_id = current_setting('app.current_family_id')::uuid
        OR role = 'admin'
        OR id = current_setting('app.current_user_id')::uuid
    );

-- Example RLS policy for child profiles
CREATE POLICY child_profile_access ON child_profiles
    FOR ALL
    TO application_role
    USING (
        guardian_id = current_setting('app.current_user_id')::uuid
        OR user_id = current_setting('app.current_user_id')::uuid
        OR EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::uuid 
            AND role IN ('admin', 'law_enforcement')
        )
    );
```

### Encryption Configuration

```sql
-- Create extension for encryption functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Function for encrypting sensitive data
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT, key_id VARCHAR)
RETURNS TEXT AS $$
BEGIN
    -- Implementation would use external key management service
    RETURN crypt(data, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql;

-- Function for decrypting sensitive data
CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT, key_id VARCHAR)
RETURNS TEXT AS $$
BEGIN
    -- Implementation would use external key management service
    RETURN encrypted_data; -- Placeholder
END;
$$ LANGUAGE plpgsql;
```

## Triggers and Functions

### Audit Trigger Function

```sql
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (
        user_id,
        action,
        resource_type,
        resource_id,
        old_values,
        new_values,
        ip_address,
        user_agent,
        success
    ) VALUES (
        COALESCE(current_setting('app.current_user_id', true)::uuid, NULL),
        TG_OP::audit_action,
        TG_TABLE_NAME,
        COALESCE(NEW.id::text, OLD.id::text),
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        COALESCE(current_setting('app.client_ip', true)::inet, NULL),
        current_setting('app.user_agent', true),
        true
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_users_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_alerts_trigger
    AFTER INSERT OR UPDATE OR DELETE ON alerts
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

### Updated Timestamp Trigger

```sql
CREATE OR REPLACE FUNCTION update_timestamp_function()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at columns
CREATE TRIGGER update_users_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_function();

CREATE TRIGGER update_families_timestamp
    BEFORE UPDATE ON families
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_function();
```

### Risk Score Calculation Function

```sql
CREATE OR REPLACE FUNCTION calculate_session_risk_score(session_uuid UUID)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    avg_message_risk DECIMAL(3,2);
    participant_risk DECIMAL(3,2);
    final_risk DECIMAL(3,2);
BEGIN
    -- Calculate average message risk score
    SELECT COALESCE(AVG(ai.risk_score), 0.00)
    INTO avg_message_risk
    FROM ai_analysis ai
    JOIN messages m ON ai.message_id = m.id
    WHERE m.session_id = session_uuid;
    
    -- Calculate participant risk factor
    SELECT COALESCE(MAX(
        CASE sp.risk_level
            WHEN 'critical' THEN 5.00
            WHEN 'high' THEN 3.00
            WHEN 'medium' THEN 1.50
            WHEN 'low' THEN 0.50
            ELSE 0.00
        END
    ), 0.00)
    INTO participant_risk
    FROM session_participants sp
    WHERE sp.session_id = session_uuid;
    
    -- Combine scores with weighted average
    final_risk := (avg_message_risk * 0.7) + (participant_risk * 0.3);
    
    -- Ensure score is within bounds
    final_risk := LEAST(GREATEST(final_risk, 0.00), 10.00);
    
    RETURN final_risk;
END;
$$ LANGUAGE plpgsql;
```

## Views and Materialized Views

### Active Sessions View

```sql
CREATE VIEW active_sessions AS
SELECT 
    ms.id,
    ms.child_id,
    cp.user_id,
    u.first_name || ' ' || u.last_name AS child_name,
    ms.platform_connection_id,
    pc.platform,
    pc.username,
    ms.start_time,
    ms.duration_seconds,
    ms.risk_score,
    ms.message_count,
    ms.participant_count,
    COUNT(a.id) AS alert_count,
    MAX(a.severity) AS highest_alert_severity
FROM monitoring_sessions ms
JOIN child_profiles cp ON ms.child_id = cp.id
JOIN users u ON cp.user_id = u.id
JOIN platform_connections pc ON ms.platform_connection_id = pc.id
LEFT JOIN alerts a ON ms.id = a.session_id AND a.status NOT IN ('resolved', 'false_positive')
WHERE ms.status = 'active'
GROUP BY ms.id, cp.id, u.id, pc.id;
```

### Guardian Dashboard Summary View

```sql
CREATE MATERIALIZED VIEW guardian_dashboard_summary AS
SELECT 
    cp.guardian_id,
    COUNT(DISTINCT cp.id) AS total_children,
    COUNT(DISTINCT pc.id) AS total_connections,
    COUNT(DISTINCT ms.id) AS total_sessions,
    COUNT(DISTINCT CASE WHEN ms.status = 'active' THEN ms.id END) AS active_sessions,
    COUNT(DISTINCT a.id) AS total_alerts,
    COUNT(DISTINCT CASE WHEN a.status = 'new' THEN a.id END) AS new_alerts,
    COUNT(DISTINCT CASE WHEN a.severity = 'critical' THEN a.id END) AS critical_alerts,
    AVG(ms.risk_score) AS avg_risk_score,
    MAX(a.created_at) AS last_alert_time,
    CURRENT_TIMESTAMP AS last_updated
FROM child_profiles cp
LEFT JOIN platform_connections pc ON cp.id = pc.child_id
LEFT JOIN monitoring_sessions ms ON cp.id = ms.child_id
LEFT JOIN alerts a ON cp.id = a.child_id
GROUP BY cp.guardian_id;

-- Create unique index for materialized view
CREATE UNIQUE INDEX idx_guardian_dashboard_summary_guardian 
ON guardian_dashboard_summary(guardian_id);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_guardian_dashboard_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY guardian_dashboard_summary;
END;
$$ LANGUAGE plpgsql;
```

## Performance Optimization

### Partitioning Strategy

```sql
-- Partition messages table by date for better performance
CREATE TABLE messages_partitioned (
    LIKE messages INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE messages_y2024m01 PARTITION OF messages_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE messages_y2024m02 PARTITION OF messages_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Function to automatically create new partitions
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name TEXT, start_date DATE)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    partition_name := table_name || '_y' || EXTRACT(YEAR FROM start_date) || 'm' || 
                     LPAD(EXTRACT(MONTH FROM start_date)::TEXT, 2, '0');
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;
```

### Index Optimization

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_messages_session_timestamp ON messages(session_id, timestamp DESC);
CREATE INDEX idx_alerts_child_status_created ON alerts(child_id, status, created_at DESC);
CREATE INDEX idx_sessions_child_platform_time ON monitoring_sessions(child_id, platform_connection_id, start_time DESC);

-- Partial indexes for active data
CREATE INDEX idx_active_platform_connections ON platform_connections(child_id, platform) 
WHERE is_active = true AND monitoring_enabled = true;

CREATE INDEX idx_unresolved_alerts ON alerts(guardian_id, severity, created_at DESC) 
WHERE status IN ('new', 'acknowledged', 'investigating');

-- GIN indexes for JSONB columns
CREATE INDEX idx_messages_metadata_gin ON messages USING gin(metadata);
CREATE INDEX idx_ai_analysis_entities_gin ON ai_analysis USING gin(entities);
CREATE INDEX idx_alerts_evidence_gin ON alerts USING gin(evidence);
```

## Data Retention and Archival

### Retention Policies

```sql
-- Function to archive old data
CREATE OR REPLACE FUNCTION archive_old_data()
RETURNS void AS $$
DECLARE
    cutoff_date DATE;
BEGIN
    -- Archive data older than 7 years (legal requirement)
    cutoff_date := CURRENT_DATE - INTERVAL '7 years';
    
    -- Move old messages to archive table
    INSERT INTO messages_archive 
    SELECT * FROM messages 
    WHERE timestamp < cutoff_date;
    
    DELETE FROM messages 
    WHERE timestamp < cutoff_date;
    
    -- Archive old sessions
    INSERT INTO monitoring_sessions_archive 
    SELECT * FROM monitoring_sessions 
    WHERE start_time < cutoff_date;
    
    DELETE FROM monitoring_sessions 
    WHERE start_time < cutoff_date;
    
    -- Log archival operation
    INSERT INTO audit_log (action, resource_type, success, metadata)
    VALUES ('archive', 'data_retention', true, 
            jsonb_build_object('cutoff_date', cutoff_date, 'archived_at', CURRENT_TIMESTAMP));
END;
$$ LANGUAGE plpgsql;

-- Schedule archival job (would be called by external scheduler)
-- SELECT cron.schedule('archive-old-data', '0 2 1 * *', 'SELECT archive_old_data();');
```

## Backup and Recovery

### Backup Strategy

```sql
-- Function to create logical backup with encryption
CREATE OR REPLACE FUNCTION create_encrypted_backup(backup_name TEXT)
RETURNS void AS $$
BEGIN
    -- This would be implemented with external tools
    -- pg_dump with encryption and secure storage
    PERFORM pg_notify('backup_channel', 
                     jsonb_build_object('action', 'create_backup', 
                                       'name', backup_name, 
                                       'timestamp', CURRENT_TIMESTAMP)::text);
END;
$$ LANGUAGE plpgsql;
```

This comprehensive database schema provides the foundation for a secure, scalable, and compliant child protection monitoring system. The design incorporates best practices for data security, performance optimization, and regulatory compliance while maintaining the flexibility needed for future enhancements and integrations.

