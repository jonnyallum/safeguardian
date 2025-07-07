from datetime import datetime
from enum import Enum
from src.models import db, generate_uuid

class ParticipantRole(Enum):
    CHILD = 'child'
    PARTICIPANT = 'participant'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    BOT = 'bot'

class RiskLevel(Enum):
    UNKNOWN = 'unknown'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class SessionParticipant(db.Model):
    __tablename__ = 'session_participants'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String(36), db.ForeignKey('monitoring_sessions.id'), nullable=False)
    platform_user_id = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=True)
    display_name = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum(ParticipantRole), default=ParticipantRole.PARTICIPANT)
    risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.UNKNOWN)
    first_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    message_count = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    age_estimate = db.Column(db.Integer, nullable=True)
    location_estimate = db.Column(db.String(255), nullable=True)
    extra_data = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('MonitoringSession', back_populates='participants')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('session_id', 'platform_user_id', name='unique_session_participant'),
    )
    
    def update_interaction(self):
        """Update last interaction timestamp and increment message count."""
        self.last_interaction = datetime.utcnow()
        self.message_count += 1
        db.session.commit()
    
    def calculate_risk_factors(self):
        """Calculate risk factors for this participant."""
        risk_factors = []
        
        # Age-related risks
        if self.age_estimate:
            if self.age_estimate > 25 and self.session.child.get_age() < 16:
                risk_factors.append({
                    'type': 'age_gap',
                    'description': f'Significant age gap: {self.age_estimate} vs {self.session.child.get_age()}',
                    'severity': 'high'
                })
            elif self.age_estimate > 18 and self.session.child.get_age() < 13:
                risk_factors.append({
                    'type': 'adult_minor_interaction',
                    'description': 'Adult interacting with minor',
                    'severity': 'medium'
                })
        
        # Interaction pattern risks
        interaction_duration = (self.last_interaction - self.first_interaction).total_seconds() / 3600
        if interaction_duration > 2 and self.message_count > 50:
            risk_factors.append({
                'type': 'intensive_interaction',
                'description': f'Intensive interaction: {self.message_count} messages over {interaction_duration:.1f} hours',
                'severity': 'medium'
            })
        
        # Unknown identity risks
        if not self.is_verified and self.message_count > 10:
            risk_factors.append({
                'type': 'unverified_identity',
                'description': 'Unverified user with significant interaction',
                'severity': 'low'
            })
        
        return risk_factors
    
    def update_risk_level(self):
        """Update risk level based on various factors."""
        risk_factors = self.calculate_risk_factors()
        
        # Count risk factors by severity
        critical_count = sum(1 for rf in risk_factors if rf['severity'] == 'critical')
        high_count = sum(1 for rf in risk_factors if rf['severity'] == 'high')
        medium_count = sum(1 for rf in risk_factors if rf['severity'] == 'medium')
        
        # Determine risk level
        if critical_count > 0:
            self.risk_level = RiskLevel.CRITICAL
        elif high_count > 0:
            self.risk_level = RiskLevel.HIGH
        elif medium_count >= 2:
            self.risk_level = RiskLevel.HIGH
        elif medium_count > 0:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
        
        # Store risk factors in metadata
        self.extra_data['risk_factors'] = risk_factors
        self.extra_data['risk_assessment_date'] = datetime.utcnow().isoformat()
        
        db.session.commit()
    
    def get_interaction_summary(self):
        """Get summary of interactions with this participant."""
        total_duration = (self.last_interaction - self.first_interaction).total_seconds()
        
        return {
            'total_messages': self.message_count,
            'interaction_duration_hours': round(total_duration / 3600, 2),
            'messages_per_hour': round(self.message_count / max(total_duration / 3600, 0.1), 1),
            'first_interaction': self.first_interaction.isoformat(),
            'last_interaction': self.last_interaction.isoformat(),
            'is_recent': (datetime.utcnow() - self.last_interaction).total_seconds() < 3600
        }
    
    def to_dict(self, include_risk_details=False):
        """Convert session participant to dictionary representation."""
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'platform_user_id': self.platform_user_id,
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role.value,
            'risk_level': self.risk_level.value,
            'message_count': self.message_count,
            'is_verified': self.is_verified,
            'age_estimate': self.age_estimate,
            'location_estimate': self.location_estimate,
            'interaction_summary': self.get_interaction_summary(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_risk_details:
            data.update({
                'risk_factors': self.calculate_risk_factors(),
                'extra_data': self.extra_data
            })
        
        return data
    
    def __repr__(self):
        return f'<SessionParticipant {self.username or self.platform_user_id} ({self.risk_level.value})>'

