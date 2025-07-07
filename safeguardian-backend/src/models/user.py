from datetime import datetime
from enum import Enum
import bcrypt
from src.models import db, generate_uuid

class UserRole(Enum):
    GUARDIAN = 'guardian'
    CHILD = 'child'
    ADMIN = 'admin'
    LAW_ENFORCEMENT = 'law_enforcement'
    SUPPORT = 'support'
    SYSTEM = 'system'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.GUARDIAN)
    family_id = db.Column(db.String(36), db.ForeignKey('families.id'), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    phone_verified_at = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    backup_codes = db.Column(db.JSON, nullable=True)
    preferences = db.Column(db.JSON, default=lambda: {})
    user_metadata = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    family = db.relationship('Family', back_populates='members', foreign_keys=[family_id])
    child_profiles = db.relationship('ChildProfile', back_populates='guardian', foreign_keys='ChildProfile.guardian_id')
    child_profile = db.relationship('ChildProfile', back_populates='user', foreign_keys='ChildProfile.user_id', uselist=False)
    alerts_as_guardian = db.relationship('Alert', back_populates='guardian', foreign_keys='Alert.guardian_id')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_guardian(self):
        """Check if user is a guardian."""
        return self.role == UserRole.GUARDIAN
    
    def is_child(self):
        """Check if user is a child."""
        return self.role == UserRole.CHILD
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
    
    def get_full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary representation."""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role.value,
            'family_id': self.family_id,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'timezone': self.timezone,
            'language': self.language,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'email_verified_at': self.email_verified_at.isoformat() if self.email_verified_at else None,
            'phone_verified_at': self.phone_verified_at.isoformat() if self.phone_verified_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'two_factor_enabled': self.two_factor_enabled,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None,
                'password_changed_at': self.password_changed_at.isoformat(),
                'user_metadata': self.user_metadata
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.email} ({self.role.value})>'

