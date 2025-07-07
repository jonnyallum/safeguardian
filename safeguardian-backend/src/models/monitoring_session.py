from datetime import datetime
from enum import Enum
from src.models import db, generate_uuid

class SessionType(Enum):
    MESSAGING = 'messaging'
    VIDEO_CALL = 'video_call'
    VOICE_CALL = 'voice_call'
    GROUP_CHAT = 'group_chat'
    LIVE_STREAM = 'live_stream'
    GAMING = 'gaming'
    BROWSING = 'browsing'

class SessionStatus(Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    PAUSED = 'paused'
    TERMINATED = 'terminated'
    FLAGGED = 'flagged'
    EMERGENCY = 'emergency'

class MonitoringSession(db.Model):
    __tablename__ = 'monitoring_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    child_id = db.Column(db.String(36), db.ForeignKey('child_profiles.id'), nullable=False)
    platform_connection_id = db.Column(db.String(36), db.ForeignKey('platform_connections.id'), nullable=False)
    session_type = db.Column(db.Enum(SessionType), default=SessionType.MESSAGING)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Enum(SessionStatus), default=SessionStatus.ACTIVE)
    risk_score = db.Column(db.Numeric(3, 2), default=0.00)
    message_count = db.Column(db.Integer, default=0)
    participant_count = db.Column(db.Integer, default=0)
    location_data = db.Column(db.JSON, nullable=True)
    device_info = db.Column(db.JSON, nullable=True)
    app_version = db.Column(db.String(50), nullable=True)
    extra_data = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    child = db.relationship('ChildProfile', back_populates='monitoring_sessions')
    platform_connection = db.relationship('PlatformConnection', back_populates='monitoring_sessions')
    messages = db.relationship('Message', back_populates='session', cascade='all, delete-orphan')
    participants = db.relationship('SessionParticipant', back_populates='session', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', back_populates='session', cascade='all, delete-orphan')
    ai_analyses = db.relationship('AIAnalysis', back_populates='session', cascade='all, delete-orphan')
    evidence = db.relationship('Evidence', back_populates='session', cascade='all, delete-orphan')
    
    def calculate_duration(self):
        """Calculate session duration in seconds."""
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds())
        elif self.start_time:
            return int((datetime.utcnow() - self.start_time).total_seconds())
        return 0
    
    def update_duration(self):
        """Update the duration_seconds field."""
        self.duration_seconds = self.calculate_duration()
        db.session.commit()
    
    def end_session(self):
        """End the monitoring session."""
        if self.status == SessionStatus.ACTIVE:
            self.end_time = datetime.utcnow()
            self.status = SessionStatus.COMPLETED
            self.update_duration()
            self.update_risk_score()
    
    def update_risk_score(self):
        """Update risk score based on AI analysis and alerts."""
        from src.models.ai_analysis import AIAnalysis
        from src.models.alert import Alert
        
        # Calculate average risk score from AI analyses
        ai_analyses = AIAnalysis.query.filter_by(session_id=self.id).all()
        if ai_analyses:
            avg_ai_risk = sum(analysis.risk_score for analysis in ai_analyses) / len(ai_analyses)
        else:
            avg_ai_risk = 0.0
        
        # Factor in alert severity
        alerts = Alert.query.filter_by(session_id=self.id).all()
        alert_risk = 0.0
        if alerts:
            severity_weights = {'low': 1.0, 'medium': 2.5, 'high': 5.0, 'critical': 8.0, 'emergency': 10.0}
            alert_risk = max(severity_weights.get(alert.severity.value, 0.0) for alert in alerts)
        
        # Calculate final risk score (weighted average)
        self.risk_score = round((avg_ai_risk * 0.7) + (alert_risk * 0.3), 2)
        
        # Update session status based on risk score
        if self.risk_score >= 8.0:
            self.status = SessionStatus.EMERGENCY
        elif self.risk_score >= 5.0:
            self.status = SessionStatus.FLAGGED
        
        db.session.commit()
    
    def add_participant(self, platform_user_id, username=None, display_name=None, role='participant'):
        """Add a participant to the session."""
        from src.models.session_participant import SessionParticipant, ParticipantRole
        
        # Check if participant already exists
        existing = SessionParticipant.query.filter_by(
            session_id=self.id,
            platform_user_id=platform_user_id
        ).first()
        
        if not existing:
            participant = SessionParticipant(
                session_id=self.id,
                platform_user_id=platform_user_id,
                username=username,
                display_name=display_name,
                role=ParticipantRole(role)
            )
            db.session.add(participant)
            self.participant_count = len(self.participants) + 1
            db.session.commit()
            return participant
        
        return existing
    
    def get_high_risk_participants(self):
        """Get participants with high or critical risk levels."""
        from src.models.session_participant import RiskLevel
        return [p for p in self.participants if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
    
    def get_recent_messages(self, limit=50):
        """Get recent messages from this session."""
        return self.messages.order_by(Message.timestamp.desc()).limit(limit).all()
    
    def get_session_summary(self):
        """Get a summary of the session."""
        high_risk_participants = self.get_high_risk_participants()
        recent_alerts = [alert for alert in self.alerts if alert.status.value in ['new', 'acknowledged']]
        
        return {
            'duration_minutes': round(self.calculate_duration() / 60, 1),
            'message_count': self.message_count,
            'participant_count': self.participant_count,
            'risk_score': float(self.risk_score),
            'high_risk_participants': len(high_risk_participants),
            'active_alerts': len(recent_alerts),
            'platform': self.platform_connection.platform.value if self.platform_connection else None
        }
    
    def to_dict(self, include_details=False):
        """Convert monitoring session to dictionary representation."""
        data = {
            'id': self.id,
            'child_id': self.child_id,
            'platform_connection_id': self.platform_connection_id,
            'session_type': self.session_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds or self.calculate_duration(),
            'status': self.status.value,
            'risk_score': float(self.risk_score),
            'message_count': self.message_count,
            'participant_count': self.participant_count,
            'app_version': self.app_version,
            'summary': self.get_session_summary(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_details:
            data.update({
                'location_data': self.location_data,
                'device_info': self.device_info,
                'extra_data': self.extra_data,
                'participants': [p.to_dict() for p in self.participants],
                'recent_messages': [m.to_dict() for m in self.get_recent_messages(10)],
                'alerts': [a.to_dict() for a in self.alerts]
            })
        
        return data
    
    def __repr__(self):
        return f'<MonitoringSession {self.id} ({self.status.value})>'

