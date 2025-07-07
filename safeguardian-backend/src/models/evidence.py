from datetime import datetime, timedelta
from enum import Enum
import hashlib
import os
from src.models import db, generate_uuid

class EvidenceType(Enum):
    MESSAGE_SCREENSHOT = 'message_screenshot'
    CONVERSATION_EXPORT = 'conversation_export'
    MEDIA_FILE = 'media_file'
    SESSION_RECORDING = 'session_recording'
    SYSTEM_LOG = 'system_log'
    AI_ANALYSIS_REPORT = 'ai_analysis_report'
    USER_PROFILE_DATA = 'user_profile_data'
    METADATA_EXPORT = 'metadata_export'

class Evidence(db.Model):
    __tablename__ = 'evidence'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    alert_id = db.Column(db.String(36), db.ForeignKey('alerts.id'), nullable=False)
    session_id = db.Column(db.String(36), db.ForeignKey('monitoring_sessions.id'), nullable=False)
    evidence_type = db.Column(db.Enum(EvidenceType), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.BigInteger, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    hash_algorithm = db.Column(db.String(20), default='SHA-256')
    file_hash = db.Column(db.String(128), nullable=False)
    encryption_key_id = db.Column(db.String(255), nullable=True)
    is_encrypted = db.Column(db.Boolean, default=True)
    chain_of_custody = db.Column(db.JSON, default=lambda: [])
    collection_method = db.Column(db.String(100), nullable=False)
    collection_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    collected_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    integrity_verified = db.Column(db.Boolean, default=False)
    integrity_check_timestamp = db.Column(db.DateTime, nullable=True)
    legal_hold = db.Column(db.Boolean, default=False)
    retention_until = db.Column(db.DateTime, nullable=True)
    access_log = db.Column(db.JSON, default=lambda: [])
    extra_data = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    alert = db.relationship('Alert', back_populates='evidence_files')
    session = db.relationship('MonitoringSession', back_populates='evidence')
    collector = db.relationship('User', foreign_keys=[collected_by])
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('file_size >= 0', name='chk_file_size'),
        db.CheckConstraint('retention_until > created_at', name='chk_retention_date')
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.retention_until:
            self.retention_until = self.calculate_retention_date()
        
        # Initialize chain of custody
        if not self.chain_of_custody:
            self.add_custody_entry('created', self.collected_by, 'Evidence record created')
    
    def calculate_retention_date(self):
        """Calculate retention date based on evidence type and legal requirements."""
        # Default retention periods (in years)
        retention_periods = {
            EvidenceType.MESSAGE_SCREENSHOT: 7,
            EvidenceType.CONVERSATION_EXPORT: 7,
            EvidenceType.MEDIA_FILE: 7,
            EvidenceType.SESSION_RECORDING: 5,
            EvidenceType.SYSTEM_LOG: 3,
            EvidenceType.AI_ANALYSIS_REPORT: 5,
            EvidenceType.USER_PROFILE_DATA: 7,
            EvidenceType.METADATA_EXPORT: 5
        }
        
        years = retention_periods.get(self.evidence_type, 7)
        return datetime.utcnow() + timedelta(days=years * 365)
    
    def calculate_file_hash(self, file_path=None):
        """Calculate hash of the evidence file."""
        if not file_path:
            file_path = self.file_path
        
        if not file_path or not os.path.exists(file_path):
            return None
        
        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def verify_integrity(self):
        """Verify file integrity using stored hash."""
        if not self.file_path or not os.path.exists(self.file_path):
            return False
        
        current_hash = self.calculate_file_hash()
        if current_hash == self.file_hash:
            self.integrity_verified = True
            self.integrity_check_timestamp = datetime.utcnow()
            self.add_custody_entry('integrity_verified', None, 'File integrity verified successfully')
            db.session.commit()
            return True
        else:
            self.integrity_verified = False
            self.add_custody_entry('integrity_failed', None, f'File integrity check failed. Expected: {self.file_hash}, Got: {current_hash}')
            db.session.commit()
            return False
    
    def add_custody_entry(self, action, user_id, notes=None):
        """Add entry to chain of custody."""
        entry = {
            'action': action,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'notes': notes,
            'ip_address': None,  # Would be populated from request context
            'system_info': {
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
                'process_id': os.getpid()
            }
        }
        
        if not self.chain_of_custody:
            self.chain_of_custody = []
        
        self.chain_of_custody.append(entry)
        db.session.commit()
    
    def log_access(self, user_id, access_type, purpose=None):
        """Log access to evidence file."""
        access_entry = {
            'user_id': user_id,
            'access_type': access_type,  # 'view', 'download', 'export', 'copy'
            'timestamp': datetime.utcnow().isoformat(),
            'purpose': purpose,
            'ip_address': None,  # Would be populated from request context
            'user_agent': None   # Would be populated from request context
        }
        
        if not self.access_log:
            self.access_log = []
        
        self.access_log.append(access_entry)
        self.add_custody_entry('accessed', user_id, f'Evidence {access_type} - {purpose or "No purpose specified"}')
    
    def set_legal_hold(self, user_id, reason):
        """Place evidence under legal hold."""
        self.legal_hold = True
        self.add_custody_entry('legal_hold_applied', user_id, f'Legal hold applied: {reason}')
    
    def release_legal_hold(self, user_id, reason):
        """Release evidence from legal hold."""
        self.legal_hold = False
        self.add_custody_entry('legal_hold_released', user_id, f'Legal hold released: {reason}')
    
    def is_retention_expired(self):
        """Check if retention period has expired."""
        if self.legal_hold:
            return False
        return self.retention_until and datetime.utcnow() > self.retention_until
    
    def can_be_deleted(self):
        """Check if evidence can be safely deleted."""
        return (
            self.is_retention_expired() and
            not self.legal_hold and
            self.alert.status.value in ['resolved', 'false_positive', 'dismissed']
        )
    
    def encrypt_file(self, encryption_key_id):
        """Encrypt the evidence file (placeholder for actual encryption)."""
        # This would implement actual file encryption
        self.is_encrypted = True
        self.encryption_key_id = encryption_key_id
        self.add_custody_entry('encrypted', None, f'File encrypted with key ID: {encryption_key_id}')
        db.session.commit()
    
    def get_file_info(self):
        """Get file information and status."""
        file_exists = self.file_path and os.path.exists(self.file_path)
        
        info = {
            'exists': file_exists,
            'size_bytes': self.file_size,
            'size_human': self._format_file_size(self.file_size) if self.file_size else None,
            'mime_type': self.mime_type,
            'is_encrypted': self.is_encrypted,
            'integrity_verified': self.integrity_verified,
            'last_integrity_check': self.integrity_check_timestamp.isoformat() if self.integrity_check_timestamp else None,
            'legal_hold': self.legal_hold,
            'retention_expires': self.retention_until.isoformat() if self.retention_until else None,
            'can_be_deleted': self.can_be_deleted(),
            'access_count': len(self.access_log) if self.access_log else 0
        }
        
        if file_exists and self.file_path:
            try:
                stat = os.stat(self.file_path)
                info.update({
                    'actual_size': stat.st_size,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size_matches': stat.st_size == self.file_size
                })
            except Exception:
                info['file_error'] = 'Unable to access file'
        
        return info
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def generate_custody_report(self):
        """Generate chain of custody report."""
        return {
            'evidence_id': self.id,
            'evidence_type': self.evidence_type.value,
            'collection_info': {
                'method': self.collection_method,
                'timestamp': self.collection_timestamp.isoformat(),
                'collected_by': self.collected_by
            },
            'file_info': {
                'name': self.file_name,
                'size': self.file_size,
                'hash': self.file_hash,
                'hash_algorithm': self.hash_algorithm,
                'is_encrypted': self.is_encrypted
            },
            'custody_chain': self.chain_of_custody,
            'access_history': self.access_log,
            'legal_status': {
                'legal_hold': self.legal_hold,
                'retention_until': self.retention_until.isoformat() if self.retention_until else None,
                'integrity_verified': self.integrity_verified
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def to_dict(self, include_sensitive=False):
        """Convert evidence to dictionary representation."""
        data = {
            'id': self.id,
            'alert_id': self.alert_id,
            'session_id': self.session_id,
            'evidence_type': self.evidence_type.value,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'hash_algorithm': self.hash_algorithm,
            'is_encrypted': self.is_encrypted,
            'collection_method': self.collection_method,
            'collection_timestamp': self.collection_timestamp.isoformat(),
            'collected_by': self.collected_by,
            'integrity_verified': self.integrity_verified,
            'integrity_check_timestamp': self.integrity_check_timestamp.isoformat() if self.integrity_check_timestamp else None,
            'legal_hold': self.legal_hold,
            'retention_until': self.retention_until.isoformat() if self.retention_until else None,
            'file_info': self.get_file_info(),
            'created_at': self.created_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'file_path': self.file_path,
                'file_hash': self.file_hash,
                'encryption_key_id': self.encryption_key_id,
                'chain_of_custody': self.chain_of_custody,
                'access_log': self.access_log,
                'extra_data': self.extra_data,
                'custody_report': self.generate_custody_report()
            })
        
        return data
    
    def __repr__(self):
        return f'<Evidence {self.evidence_type.value} ({self.file_name})>'

