from datetime import datetime
from enum import Enum
from src.models import db, generate_uuid

class PlatformType(Enum):
    FACEBOOK = 'facebook'
    INSTAGRAM = 'instagram'
    SNAPCHAT = 'snapchat'
    TIKTOK = 'tiktok'
    DISCORD = 'discord'
    WHATSAPP = 'whatsapp'
    TELEGRAM = 'telegram'
    TWITTER = 'twitter'
    YOUTUBE = 'youtube'

class SyncStatus(Enum):
    PENDING = 'pending'
    SYNCING = 'syncing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PAUSED = 'paused'

class PlatformConnection(db.Model):
    __tablename__ = 'platform_connections'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    child_id = db.Column(db.String(36), db.ForeignKey('child_profiles.id'), nullable=False)
    platform = db.Column(db.Enum(PlatformType), nullable=False)
    platform_user_id = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=True)
    display_name = db.Column(db.String(255), nullable=True)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    permissions = db.Column(db.JSON, default=lambda: [])
    is_active = db.Column(db.Boolean, default=True)
    monitoring_enabled = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime, nullable=True)
    sync_status = db.Column(db.Enum(SyncStatus), default=SyncStatus.PENDING)
    error_message = db.Column(db.Text, nullable=True)
    extra_data = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    child = db.relationship('ChildProfile', back_populates='platform_connections')
    monitoring_sessions = db.relationship('MonitoringSession', back_populates='platform_connection', cascade='all, delete-orphan')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('child_id', 'platform', 'platform_user_id', name='unique_child_platform_user'),
    )
    
    def is_token_valid(self):
        """Check if the access token is still valid."""
        if not self.access_token:
            return False
        if self.token_expires_at and self.token_expires_at < datetime.utcnow():
            return False
        return True
    
    def needs_refresh(self):
        """Check if token needs to be refreshed."""
        if not self.token_expires_at:
            return False
        # Refresh if token expires within 1 hour
        return (self.token_expires_at - datetime.utcnow()).total_seconds() < 3600
    
    def get_platform_config(self):
        """Get platform-specific configuration."""
        configs = {
            PlatformType.FACEBOOK: {
                'api_base_url': 'https://graph.facebook.com/v18.0',
                'oauth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'scopes': ['user_posts', 'user_photos', 'user_videos'],
                'rate_limit': 200  # requests per hour
            },
            PlatformType.INSTAGRAM: {
                'api_base_url': 'https://graph.instagram.com',
                'oauth_url': 'https://api.instagram.com/oauth/authorize',
                'token_url': 'https://api.instagram.com/oauth/access_token',
                'scopes': ['user_profile', 'user_media'],
                'rate_limit': 200
            },
            PlatformType.SNAPCHAT: {
                'api_base_url': 'https://kit.snapchat.com/v1',
                'oauth_url': 'https://accounts.snapchat.com/accounts/oauth2/auth',
                'token_url': 'https://accounts.snapchat.com/accounts/oauth2/token',
                'scopes': ['user.display_name', 'user.bitmoji.avatar'],
                'rate_limit': 1000
            },
            PlatformType.TIKTOK: {
                'api_base_url': 'https://open-api.tiktok.com',
                'oauth_url': 'https://www.tiktok.com/auth/authorize',
                'token_url': 'https://open-api.tiktok.com/oauth/access_token',
                'scopes': ['user.info.basic', 'video.list'],
                'rate_limit': 100
            },
            PlatformType.DISCORD: {
                'api_base_url': 'https://discord.com/api/v10',
                'oauth_url': 'https://discord.com/api/oauth2/authorize',
                'token_url': 'https://discord.com/api/oauth2/token',
                'scopes': ['identify', 'guilds', 'messages.read'],
                'rate_limit': 50
            }
        }
        return configs.get(self.platform, {})
    
    def update_sync_status(self, status, error_message=None):
        """Update sync status and error message."""
        self.sync_status = status
        self.error_message = error_message
        if status == SyncStatus.COMPLETED:
            self.last_sync = datetime.utcnow()
        db.session.commit()
    
    def get_monitoring_stats(self):
        """Get monitoring statistics for this connection."""
        from src.models.monitoring_session import MonitoringSession
        from src.models.alert import Alert
        
        total_sessions = MonitoringSession.query.filter_by(platform_connection_id=self.id).count()
        active_sessions = MonitoringSession.query.filter_by(
            platform_connection_id=self.id,
            status='active'
        ).count()
        total_alerts = Alert.query.join(MonitoringSession).filter(
            MonitoringSession.platform_connection_id == self.id
        ).count()
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_alerts': total_alerts,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }
    
    def to_dict(self, include_tokens=False):
        """Convert platform connection to dictionary representation."""
        data = {
            'id': self.id,
            'child_id': self.child_id,
            'platform': self.platform.value,
            'platform_user_id': self.platform_user_id,
            'username': self.username,
            'display_name': self.display_name,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'monitoring_enabled': self.monitoring_enabled,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_status': self.sync_status.value,
            'error_message': self.error_message,
            'is_token_valid': self.is_token_valid(),
            'needs_refresh': self.needs_refresh(),
            'platform_config': self.get_platform_config(),
            'monitoring_stats': self.get_monitoring_stats(),
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_tokens:
            data.update({
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
            })
        
        return data
    
    def __repr__(self):
        return f'<PlatformConnection {self.platform.value}:{self.username}>'

