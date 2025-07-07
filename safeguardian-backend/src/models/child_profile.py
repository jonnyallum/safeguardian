from datetime import datetime, date
from src.models import db, generate_uuid

class ChildProfile(db.Model):
    __tablename__ = 'child_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    guardian_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    grade_level = db.Column(db.String(20), nullable=True)
    school_name = db.Column(db.String(255), nullable=True)
    medical_conditions = db.Column(db.JSON, default=lambda: [])
    allergies = db.Column(db.JSON, default=lambda: [])
    emergency_contacts = db.Column(db.JSON, default=lambda: [])
    monitoring_settings = db.Column(db.JSON, default=lambda: {})
    risk_profile = db.Column(db.JSON, default=lambda: {})
    parental_controls = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='child_profile', foreign_keys=[user_id])
    guardian = db.relationship('User', back_populates='child_profiles', foreign_keys=[guardian_id])
    platform_connections = db.relationship('PlatformConnection', back_populates='child', cascade='all, delete-orphan')
    monitoring_sessions = db.relationship('MonitoringSession', back_populates='child', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', back_populates='child', cascade='all, delete-orphan')
    
    def get_age(self):
        """Calculate child's current age."""
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def get_active_platforms(self):
        """Get list of active platform connections."""
        return [conn for conn in self.platform_connections if conn.is_active and conn.monitoring_enabled]
    
    def get_recent_sessions(self, limit=10):
        """Get recent monitoring sessions."""
        from src.models.monitoring_session import MonitoringSession
        return MonitoringSession.query.filter_by(child_id=self.id).order_by(MonitoringSession.start_time.desc()).limit(limit).all()
    
    def get_unresolved_alerts(self):
        """Get unresolved alerts for this child."""
        from src.models.alert import Alert, AlertStatus
        return Alert.query.filter_by(child_id=self.id).filter(
            Alert.status.in_([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.INVESTIGATING])
        ).order_by(Alert.created_at.desc()).all()
    
    def get_risk_score(self):
        """Calculate current risk score based on recent activity."""
        recent_sessions = self.get_recent_sessions(5)
        if not recent_sessions:
            return 0.0
        
        total_risk = sum(session.risk_score or 0.0 for session in recent_sessions)
        return round(total_risk / len(recent_sessions), 2)
    
    def update_risk_profile(self):
        """Update risk profile based on recent activity and alerts."""
        risk_score = self.get_risk_score()
        unresolved_alerts = len(self.get_unresolved_alerts())
        
        self.risk_profile.update({
            'current_risk_score': risk_score,
            'unresolved_alerts': unresolved_alerts,
            'last_updated': datetime.utcnow().isoformat(),
            'risk_level': self._calculate_risk_level(risk_score, unresolved_alerts)
        })
        
        db.session.commit()
    
    def _calculate_risk_level(self, risk_score, unresolved_alerts):
        """Calculate risk level based on score and alerts."""
        if risk_score >= 7.0 or unresolved_alerts >= 3:
            return 'critical'
        elif risk_score >= 5.0 or unresolved_alerts >= 2:
            return 'high'
        elif risk_score >= 3.0 or unresolved_alerts >= 1:
            return 'medium'
        else:
            return 'low'
    
    def get_default_monitoring_settings(self):
        """Get default monitoring settings based on age."""
        age = self.get_age()
        
        if age < 10:
            return {
                'monitoring_level': 'strict',
                'alert_threshold': 'low',
                'auto_escalation': True,
                'content_filtering': 'strict',
                'time_restrictions': {
                    'weekdays': {'start': '16:00', 'end': '19:00'},
                    'weekends': {'start': '09:00', 'end': '20:00'}
                }
            }
        elif age < 13:
            return {
                'monitoring_level': 'moderate',
                'alert_threshold': 'medium',
                'auto_escalation': True,
                'content_filtering': 'moderate',
                'time_restrictions': {
                    'weekdays': {'start': '15:00', 'end': '20:00'},
                    'weekends': {'start': '08:00', 'end': '21:00'}
                }
            }
        else:
            return {
                'monitoring_level': 'light',
                'alert_threshold': 'high',
                'auto_escalation': False,
                'content_filtering': 'light',
                'time_restrictions': {
                    'weekdays': {'start': '14:00', 'end': '21:00'},
                    'weekends': {'start': '08:00', 'end': '22:00'}
                }
            }
    
    def to_dict(self, include_sensitive=False):
        """Convert child profile to dictionary representation."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'guardian_id': self.guardian_id,
            'date_of_birth': self.date_of_birth.isoformat(),
            'age': self.get_age(),
            'grade_level': self.grade_level,
            'school_name': self.school_name,
            'emergency_contacts': self.emergency_contacts,
            'monitoring_settings': self.monitoring_settings,
            'risk_profile': self.risk_profile,
            'current_risk_score': self.get_risk_score(),
            'active_platforms': len(self.get_active_platforms()),
            'unresolved_alerts': len(self.get_unresolved_alerts()),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'medical_conditions': self.medical_conditions,
                'allergies': self.allergies,
                'parental_controls': self.parental_controls
            })
        
        return data
    
    def __repr__(self):
        return f'<ChildProfile {self.user.get_full_name() if self.user else self.id}>'

