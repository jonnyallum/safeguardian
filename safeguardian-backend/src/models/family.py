from datetime import datetime
from enum import Enum
import secrets
import string
from src.models import db, generate_uuid

class SubscriptionTier(Enum):
    FREE = 'free'
    BASIC = 'basic'
    PREMIUM = 'premium'
    ENTERPRISE = 'enterprise'

class SubscriptionStatus(Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'

class Family(db.Model):
    __tablename__ = 'families'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    family_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    primary_guardian_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    subscription_tier = db.Column(db.Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    billing_email = db.Column(db.String(255), nullable=True)
    settings = db.Column(db.JSON, default=lambda: {})
    emergency_contacts = db.Column(db.JSON, default=lambda: [])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    primary_guardian = db.relationship('User', foreign_keys=[primary_guardian_id])
    members = db.relationship('User', back_populates='family', foreign_keys='User.family_id')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.family_code:
            self.family_code = self.generate_family_code()
    
    @staticmethod
    def generate_family_code():
        """Generate a unique family code."""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if not Family.query.filter_by(family_code=code).first():
                return code
    
    def get_children(self):
        """Get all children in the family."""
        from src.models.child_profile import ChildProfile
        return ChildProfile.query.join(User).filter(User.family_id == self.id).all()
    
    def get_guardians(self):
        """Get all guardians in the family."""
        from src.models.user import UserRole
        return [member for member in self.members if member.role == UserRole.GUARDIAN]
    
    def is_subscription_active(self):
        """Check if family subscription is active."""
        if self.subscription_status != SubscriptionStatus.ACTIVE:
            return False
        if self.subscription_expires_at and self.subscription_expires_at < datetime.utcnow():
            return False
        return True
    
    def get_subscription_limits(self):
        """Get subscription limits based on tier."""
        limits = {
            SubscriptionTier.FREE: {
                'max_children': 1,
                'max_platforms': 2,
                'alert_retention_days': 30,
                'evidence_storage_gb': 1
            },
            SubscriptionTier.BASIC: {
                'max_children': 3,
                'max_platforms': 5,
                'alert_retention_days': 90,
                'evidence_storage_gb': 5
            },
            SubscriptionTier.PREMIUM: {
                'max_children': 10,
                'max_platforms': -1,  # unlimited
                'alert_retention_days': 365,
                'evidence_storage_gb': 25
            },
            SubscriptionTier.ENTERPRISE: {
                'max_children': -1,  # unlimited
                'max_platforms': -1,  # unlimited
                'alert_retention_days': -1,  # unlimited
                'evidence_storage_gb': 100
            }
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.FREE])
    
    def to_dict(self):
        """Convert family to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'family_code': self.family_code,
            'primary_guardian_id': self.primary_guardian_id,
            'subscription_tier': self.subscription_tier.value,
            'subscription_status': self.subscription_status.value,
            'subscription_expires_at': self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
            'billing_email': self.billing_email,
            'settings': self.settings,
            'emergency_contacts': self.emergency_contacts,
            'subscription_limits': self.get_subscription_limits(),
            'is_subscription_active': self.is_subscription_active(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Family {self.name} ({self.family_code})>'

