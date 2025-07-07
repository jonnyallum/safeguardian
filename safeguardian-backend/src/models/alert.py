from datetime import datetime
from enum import Enum
from src.models import db, generate_uuid

class AlertType(Enum):
    GROOMING_DETECTED = 'grooming_detected'
    INAPPROPRIATE_CONTENT = 'inappropriate_content'
    STRANGER_CONTACT = 'stranger_contact'
    PERSONAL_INFO_REQUEST = 'personal_info_request'
    MEETING_REQUEST = 'meeting_request'
    SUSPICIOUS_BEHAVIOR = 'suspicious_behavior'
    CYBERBULLYING = 'cyberbullying'
    SELF_HARM_INDICATORS = 'self_harm_indicators'
    EMERGENCY_KEYWORDS = 'emergency_keywords'
    PLATFORM_VIOLATION = 'platform_violation'

class AlertSeverity(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
    EMERGENCY = 'emergency'

class AlertStatus(Enum):
    NEW = 'new'
    ACKNOWLEDGED = 'acknowledged'
    INVESTIGATING = 'investigating'
    RESOLVED = 'resolved'
    ESCALATED = 'escalated'
    FALSE_POSITIVE = 'false_positive'
    DISMISSED = 'dismissed'

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String(36), db.ForeignKey('monitoring_sessions.id'), nullable=False)
    message_id = db.Column(db.String(36), db.ForeignKey('messages.id'), nullable=True)
    child_id = db.Column(db.String(36), db.ForeignKey('child_profiles.id'), nullable=False)
    guardian_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.Enum(AlertType), nullable=False)
    severity = db.Column(db.Enum(AlertSeverity), nullable=False)
    status = db.Column(db.Enum(AlertStatus), default=AlertStatus.NEW)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Numeric(3, 2), nullable=False)
    confidence_score = db.Column(db.Numeric(5, 4), nullable=False)
    triggered_by = db.Column(db.JSON, nullable=False)
    evidence = db.Column(db.JSON, default=lambda: {})
    recommendations = db.Column(db.JSON, default=lambda: [])
    false_positive = db.Column(db.Boolean, nullable=True)
    false_positive_reason = db.Column(db.Text, nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    acknowledged_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    escalated_at = db.Column(db.DateTime, nullable=True)
    escalated_to = db.Column(db.String(255), nullable=True)
    escalation_reference = db.Column(db.String(255), nullable=True)
    actions_taken = db.Column(db.JSON, default=lambda: [])
    extra_data = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('MonitoringSession', back_populates='alerts')
    message = db.relationship('Message', back_populates='alerts')
    child = db.relationship('ChildProfile', back_populates='alerts')
    guardian = db.relationship('User', back_populates='alerts_as_guardian', foreign_keys=[guardian_id])
    acknowledged_by_user = db.relationship('User', foreign_keys=[acknowledged_by])
    resolved_by_user = db.relationship('User', foreign_keys=[resolved_by])
    evidence_files = db.relationship('Evidence', back_populates='alert', cascade='all, delete-orphan')
    
    def acknowledge(self, user_id, notes=None):
        """Acknowledge the alert."""
        if self.status == AlertStatus.NEW:
            self.status = AlertStatus.ACKNOWLEDGED
            self.acknowledged_at = datetime.utcnow()
            self.acknowledged_by = user_id
            
            if notes:
                self.add_action('acknowledged', user_id, notes)
            
            db.session.commit()
    
    def resolve(self, user_id, resolution_notes=None, is_false_positive=False):
        """Resolve the alert."""
        if self.status in [AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.INVESTIGATING]:
            if is_false_positive:
                self.status = AlertStatus.FALSE_POSITIVE
                self.false_positive = True
                self.false_positive_reason = resolution_notes
            else:
                self.status = AlertStatus.RESOLVED
            
            self.resolved_at = datetime.utcnow()
            self.resolved_by = user_id
            
            if resolution_notes:
                action_type = 'marked_false_positive' if is_false_positive else 'resolved'
                self.add_action(action_type, user_id, resolution_notes)
            
            db.session.commit()
    
    def escalate(self, user_id, escalation_target, reference_number=None, notes=None):
        """Escalate the alert to authorities."""
        self.status = AlertStatus.ESCALATED
        self.escalated_at = datetime.utcnow()
        self.escalated_to = escalation_target
        self.escalation_reference = reference_number
        
        self.add_action('escalated', user_id, f"Escalated to {escalation_target}. {notes or ''}")
        
        db.session.commit()
    
    def add_action(self, action_type, user_id, notes=None):
        """Add an action to the alert history."""
        action = {
            'action': action_type,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'notes': notes
        }
        
        if not self.actions_taken:
            self.actions_taken = []
        
        self.actions_taken.append(action)
        db.session.commit()
    
    def get_severity_weight(self):
        """Get numeric weight for severity level."""
        weights = {
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4,
            AlertSeverity.EMERGENCY: 5
        }
        return weights.get(self.severity, 1)
    
    def get_urgency_level(self):
        """Calculate urgency level based on severity and time."""
        base_urgency = self.get_severity_weight()
        
        # Increase urgency based on time since creation
        hours_since_creation = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        
        if self.severity == AlertSeverity.EMERGENCY:
            if hours_since_creation > 1:
                return 'critical'
            return 'immediate'
        elif self.severity == AlertSeverity.CRITICAL:
            if hours_since_creation > 4:
                return 'high'
            return 'urgent'
        elif self.severity == AlertSeverity.HIGH:
            if hours_since_creation > 24:
                return 'medium'
            return 'high'
        else:
            return 'normal'
    
    def get_recommended_actions(self):
        """Get recommended actions based on alert type and severity."""
        recommendations = {
            AlertType.GROOMING_DETECTED: [
                "Review conversation history immediately",
                "Contact child to discuss the interaction",
                "Consider blocking the contact",
                "Document evidence for potential reporting"
            ],
            AlertType.INAPPROPRIATE_CONTENT: [
                "Review the flagged content",
                "Discuss appropriate online behavior with child",
                "Adjust content filtering settings",
                "Monitor for similar incidents"
            ],
            AlertType.STRANGER_CONTACT: [
                "Verify the identity of the contact",
                "Discuss stranger safety with child",
                "Review privacy settings",
                "Monitor ongoing interactions"
            ],
            AlertType.PERSONAL_INFO_REQUEST: [
                "Immediately review the conversation",
                "Educate child about personal information safety",
                "Block the requesting contact",
                "Report to platform if necessary"
            ],
            AlertType.MEETING_REQUEST: [
                "URGENT: Review conversation immediately",
                "Contact child directly",
                "Block the contact making the request",
                "Consider contacting authorities"
            ],
            AlertType.EMERGENCY_KEYWORDS: [
                "IMMEDIATE ACTION REQUIRED",
                "Contact child immediately",
                "Review full conversation context",
                "Contact emergency services if necessary"
            ]
        }
        
        base_recommendations = recommendations.get(self.alert_type, [
            "Review the flagged content",
            "Take appropriate action based on context",
            "Monitor for similar incidents"
        ])
        
        # Add severity-specific recommendations
        if self.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            base_recommendations.insert(0, "URGENT: Immediate attention required")
            base_recommendations.append("Consider escalating to authorities")
        
        return base_recommendations
    
    def generate_evidence_package(self):
        """Generate evidence package for this alert."""
        evidence_package = {
            'alert_id': self.id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'created_at': self.created_at.isoformat(),
            'child_info': {
                'id': self.child.id,
                'age': self.child.get_age(),
                'guardian_id': self.guardian_id
            },
            'session_info': {
                'id': self.session_id,
                'platform': self.session.platform_connection.platform.value,
                'start_time': self.session.start_time.isoformat(),
                'participants': len(self.session.participants)
            },
            'triggered_by': self.triggered_by,
            'evidence': self.evidence,
            'risk_score': float(self.risk_score),
            'confidence_score': float(self.confidence_score)
        }
        
        if self.message:
            evidence_package['message_info'] = {
                'id': self.message.id,
                'content_type': self.message.content_type.value,
                'timestamp': self.message.timestamp.isoformat(),
                'sender': self.message.sender_platform_id,
                'content_hash': self.message.content_hash
            }
        
        return evidence_package
    
    def to_dict(self, include_evidence=False, include_actions=False):
        """Convert alert to dictionary representation."""
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'message_id': self.message_id,
            'child_id': self.child_id,
            'guardian_id': self.guardian_id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'risk_score': float(self.risk_score),
            'confidence_score': float(self.confidence_score),
            'urgency_level': self.get_urgency_level(),
            'recommended_actions': self.get_recommended_actions(),
            'false_positive': self.false_positive,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'escalated_at': self.escalated_at.isoformat() if self.escalated_at else None,
            'escalated_to': self.escalated_to,
            'escalation_reference': self.escalation_reference,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_evidence:
            data.update({
                'triggered_by': self.triggered_by,
                'evidence': self.evidence,
                'evidence_package': self.generate_evidence_package()
            })
        
        if include_actions:
            data.update({
                'actions_taken': self.actions_taken,
                'extra_data': self.extra_data
            })
        
        return data
    
    def __repr__(self):
        return f'<Alert {self.alert_type.value} ({self.severity.value})>'

