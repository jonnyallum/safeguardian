from datetime import datetime
from enum import Enum
import hashlib
from src.models import db, generate_uuid

class ContentType(Enum):
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    FILE = 'file'
    STICKER = 'sticker'
    GIF = 'gif'
    LOCATION = 'location'
    CONTACT = 'contact'
    POLL = 'poll'
    STORY = 'story'

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String(36), db.ForeignKey('monitoring_sessions.id'), nullable=False)
    platform_message_id = db.Column(db.String(255), nullable=True)
    sender_platform_id = db.Column(db.String(255), nullable=False)
    recipient_platform_id = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=True)
    content_type = db.Column(db.Enum(ContentType), default=ContentType.TEXT)
    content_hash = db.Column(db.String(64), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    edited_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False)
    encryption_method = db.Column(db.String(50), nullable=True)
    attachments = db.Column(db.JSON, default=lambda: [])
    mentions = db.Column(db.JSON, default=lambda: [])
    hashtags = db.Column(db.JSON, default=lambda: [])
    urls = db.Column(db.JSON, default=lambda: [])
    location_data = db.Column(db.JSON, nullable=True)
    extra_data = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    session = db.relationship('MonitoringSession', back_populates='messages')
    ai_analyses = db.relationship('AIAnalysis', back_populates='message', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', back_populates='message', cascade='all, delete-orphan')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('session_id', 'platform_message_id', name='unique_session_platform_message'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.content and not self.content_hash:
            self.content_hash = self.generate_content_hash()
    
    def generate_content_hash(self):
        """Generate SHA-256 hash of message content for integrity verification."""
        if self.content:
            return hashlib.sha256(self.content.encode('utf-8')).hexdigest()
        return None
    
    def extract_urls(self):
        """Extract URLs from message content."""
        import re
        if not self.content:
            return []
        
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, self.content)
        self.urls = urls
        return urls
    
    def extract_mentions(self):
        """Extract mentions from message content."""
        import re
        if not self.content:
            return []
        
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, self.content)
        self.mentions = mentions
        return mentions
    
    def extract_hashtags(self):
        """Extract hashtags from message content."""
        import re
        if not self.content:
            return []
        
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, self.content)
        self.hashtags = hashtags
        return hashtags
    
    def process_content(self):
        """Process message content to extract metadata."""
        self.extract_urls()
        self.extract_mentions()
        self.extract_hashtags()
        
        # Update content hash
        self.content_hash = self.generate_content_hash()
        
        db.session.commit()
    
    def get_sender_info(self):
        """Get information about the message sender."""
        from src.models.session_participant import SessionParticipant
        
        participant = SessionParticipant.query.filter_by(
            session_id=self.session_id,
            platform_user_id=self.sender_platform_id
        ).first()
        
        if participant:
            return {
                'username': participant.username,
                'display_name': participant.display_name,
                'risk_level': participant.risk_level.value,
                'is_verified': participant.is_verified
            }
        
        return {
            'username': None,
            'display_name': None,
            'risk_level': 'unknown',
            'is_verified': False
        }
    
    def get_risk_indicators(self):
        """Get risk indicators from AI analysis."""
        risk_indicators = []
        
        for analysis in self.ai_analyses:
            if analysis.risk_score > 5.0:
                risk_indicators.extend(analysis.risk_factors or [])
        
        return risk_indicators
    
    def is_from_child(self):
        """Check if message is from the monitored child."""
        child_user_id = self.session.child.user.id if self.session.child.user else None
        
        # This would need platform-specific logic to map platform_user_id to child
        # For now, we'll use a simple heuristic
        return self.sender_platform_id == str(child_user_id)
    
    def get_content_preview(self, max_length=100):
        """Get a preview of the message content."""
        if not self.content:
            return f"[{self.content_type.value.upper()}]"
        
        if len(self.content) <= max_length:
            return self.content
        
        return self.content[:max_length] + "..."
    
    def verify_integrity(self):
        """Verify message content integrity using stored hash."""
        if not self.content_hash:
            return False
        
        current_hash = self.generate_content_hash()
        return current_hash == self.content_hash
    
    def to_dict(self, include_content=True, include_analysis=False):
        """Convert message to dictionary representation."""
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'platform_message_id': self.platform_message_id,
            'sender_platform_id': self.sender_platform_id,
            'recipient_platform_id': self.recipient_platform_id,
            'content_type': self.content_type.value,
            'content_hash': self.content_hash,
            'timestamp': self.timestamp.isoformat(),
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'is_encrypted': self.is_encrypted,
            'encryption_method': self.encryption_method,
            'attachments': self.attachments,
            'mentions': self.mentions,
            'hashtags': self.hashtags,
            'urls': self.urls,
            'location_data': self.location_data,
            'sender_info': self.get_sender_info(),
            'is_from_child': self.is_from_child(),
            'content_preview': self.get_content_preview(),
            'integrity_verified': self.verify_integrity(),
            'created_at': self.created_at.isoformat()
        }
        
        if include_content:
            data['content'] = self.content
        
        if include_analysis:
            data.update({
                'ai_analyses': [analysis.to_dict() for analysis in self.ai_analyses],
                'risk_indicators': self.get_risk_indicators(),
                'alerts': [alert.to_dict() for alert in self.alerts],
                'extra_data': self.extra_data
            })
        
        return data
    
    def __repr__(self):
        return f'<Message {self.id} ({self.content_type.value})>'

