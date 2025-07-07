"""
SafeGuardian Security Manager
Comprehensive security system providing encryption, authentication, authorization,
and security monitoring for the entire SafeGuardian platform
"""

import asyncio
import json
import logging
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import ipaddress
from collections import defaultdict, deque
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserRole(Enum):
    CHILD = "child"
    GUARDIAN = "guardian"
    FAMILY_ADMIN = "family_admin"
    SYSTEM_ADMIN = "system_admin"
    LAW_ENFORCEMENT = "law_enforcement"
    SUPPORT = "support"

class SecurityEvent(Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ACCOUNT_LOCKOUT = "account_lockout"
    PASSWORD_CHANGE = "password_change"
    ENCRYPTION_ERROR = "encryption_error"
    INTEGRITY_VIOLATION = "integrity_violation"

@dataclass
class SecurityAlert:
    alert_id: str
    event_type: SecurityEvent
    severity: SecurityLevel
    user_id: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime
    details: Dict
    resolved: bool = False

@dataclass
class AuthToken:
    token_id: str
    user_id: str
    user_role: UserRole
    issued_at: datetime
    expires_at: datetime
    permissions: Set[str]
    metadata: Dict

@dataclass
class SecuritySession:
    session_id: str
    user_id: str
    user_role: UserRole
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    security_level: SecurityLevel
    permissions: Set[str]
    metadata: Dict

class SecurityManager:
    """
    Comprehensive security manager for SafeGuardian
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Security configuration
        self.jwt_secret = self.config.get('jwt_secret', secrets.token_urlsafe(32))
        self.session_timeout = self.config.get('session_timeout', 3600)  # 1 hour
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.lockout_duration = self.config.get('lockout_duration', 900)  # 15 minutes
        
        # Encryption setup
        self._setup_encryption()
        
        # Session management
        self.active_sessions: Dict[str, SecuritySession] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
        
        # Authentication tracking
        self.login_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.locked_accounts: Dict[str, datetime] = {}
        
        # Security monitoring
        self.security_alerts: List[SecurityAlert] = []
        self.suspicious_ips: Set[str] = set()
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Permissions system
        self.role_permissions = self._initialize_role_permissions()
        
        # Security statistics
        self.stats = {
            'total_logins': 0,
            'failed_logins': 0,
            'active_sessions': 0,
            'security_alerts': 0,
            'blocked_attempts': 0,
            'start_time': datetime.now(timezone.utc)
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info("SafeGuardian Security Manager initialized")
    
    def _setup_encryption(self):
        """Setup encryption systems"""
        # Generate or load encryption keys
        master_key = self.config.get('master_key')
        if not master_key:
            master_key = Fernet.generate_key()
            logger.warning("Generated new master encryption key - store securely!")
        
        self.cipher = Fernet(master_key)
        
        # Generate RSA key pair for digital signatures
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        logger.info("Encryption systems initialized")
    
    def _initialize_role_permissions(self) -> Dict[UserRole, Set[str]]:
        """Initialize role-based permissions"""
        return {
            UserRole.CHILD: {
                'view_own_profile',
                'use_mobile_app'
            },
            UserRole.GUARDIAN: {
                'view_own_profile',
                'view_children_profiles',
                'view_monitoring_data',
                'view_alerts',
                'acknowledge_alerts',
                'manage_children',
                'access_dashboard'
            },
            UserRole.FAMILY_ADMIN: {
                'view_own_profile',
                'view_children_profiles',
                'view_monitoring_data',
                'view_alerts',
                'acknowledge_alerts',
                'manage_children',
                'access_dashboard',
                'manage_family_settings',
                'invite_guardians',
                'view_evidence'
            },
            UserRole.SYSTEM_ADMIN: {
                'view_all_profiles',
                'view_all_monitoring_data',
                'view_all_alerts',
                'manage_all_alerts',
                'access_admin_panel',
                'manage_system_settings',
                'view_evidence',
                'manage_evidence',
                'view_security_logs',
                'manage_users'
            },
            UserRole.LAW_ENFORCEMENT: {
                'view_evidence',
                'access_sealed_evidence',
                'request_evidence_transfer',
                'view_case_reports'
            },
            UserRole.SUPPORT: {
                'view_support_tickets',
                'manage_support_tickets',
                'view_basic_user_info'
            }
        }
    
    async def start(self):
        """Start the security manager"""
        if self.is_running:
            logger.warning("Security manager is already running")
            return
        
        self.is_running = True
        logger.info("Starting SafeGuardian Security Manager...")
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._session_monitor()),
            asyncio.create_task(self._security_monitor()),
            asyncio.create_task(self._cleanup_task()),
            asyncio.create_task(self._statistics_updater())
        ]
        
        logger.info("Security Manager started successfully")
    
    async def stop(self):
        """Stop the security manager"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping Security Manager...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        logger.info("Security Manager stopped")
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str, user_agent: str) -> Optional[Dict]:
        """
        Authenticate user credentials
        
        Args:
            username: User's username/email
            password: User's password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Authentication result with token or None if failed
        """
        with self.lock:
            # Check if account is locked
            if username in self.locked_accounts:
                lockout_time = self.locked_accounts[username]
                if datetime.now(timezone.utc) < lockout_time:
                    await self._create_security_alert(
                        SecurityEvent.ACCOUNT_LOCKOUT,
                        SecurityLevel.MEDIUM,
                        None,
                        ip_address,
                        {'username': username, 'reason': 'Account locked'}
                    )
                    return None
                else:
                    # Lockout expired
                    del self.locked_accounts[username]
            
            # Check rate limiting
            if not await self._check_rate_limit(ip_address, 'login', 10, 300):  # 10 attempts per 5 minutes
                await self._create_security_alert(
                    SecurityEvent.SUSPICIOUS_ACTIVITY,
                    SecurityLevel.HIGH,
                    None,
                    ip_address,
                    {'reason': 'Rate limit exceeded for login attempts'}
                )
                return None
            
            # Validate credentials (placeholder - implement actual user lookup)
            user_data = await self._validate_credentials(username, password)
            
            if not user_data:
                # Record failed login attempt
                self.login_attempts[username].append(datetime.now(timezone.utc))
                self.stats['failed_logins'] += 1
                
                # Check for too many failed attempts
                recent_attempts = [
                    attempt for attempt in self.login_attempts[username]
                    if datetime.now(timezone.utc) - attempt < timedelta(minutes=15)
                ]
                
                if len(recent_attempts) >= self.max_login_attempts:
                    # Lock account
                    self.locked_accounts[username] = datetime.now(timezone.utc) + timedelta(seconds=self.lockout_duration)
                    
                    await self._create_security_alert(
                        SecurityEvent.ACCOUNT_LOCKOUT,
                        SecurityLevel.HIGH,
                        user_data.get('user_id') if user_data else None,
                        ip_address,
                        {'username': username, 'failed_attempts': len(recent_attempts)}
                    )
                
                await self._create_security_alert(
                    SecurityEvent.LOGIN_FAILURE,
                    SecurityLevel.MEDIUM,
                    user_data.get('user_id') if user_data else None,
                    ip_address,
                    {'username': username}
                )
                
                return None
            
            # Successful authentication
            user_id = user_data['user_id']
            user_role = UserRole(user_data['role'])
            
            # Clear failed login attempts
            if username in self.login_attempts:
                self.login_attempts[username].clear()
            
            # Create session
            session = await self._create_session(user_id, user_role, ip_address, user_agent)
            
            # Generate JWT token
            token = await self._generate_jwt_token(user_id, user_role, session.session_id)
            
            self.stats['total_logins'] += 1
            
            await self._create_security_alert(
                SecurityEvent.LOGIN_SUCCESS,
                SecurityLevel.LOW,
                user_id,
                ip_address,
                {'username': username, 'session_id': session.session_id}
            )
            
            logger.info(f"User {user_id} authenticated successfully from {ip_address}")
            
            return {
                'token': token,
                'session_id': session.session_id,
                'user_id': user_id,
                'role': user_role.value,
                'permissions': list(session.permissions),
                'expires_at': session.last_activity + timedelta(seconds=self.session_timeout)
            }
    
    async def validate_token(self, token: str, required_permissions: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Validate JWT token and check permissions
        
        Args:
            token: JWT token to validate
            required_permissions: List of required permissions
            
        Returns:
            Token data if valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            user_id = payload.get('user_id')
            session_id = payload.get('session_id')
            
            # Check if session exists and is valid
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # Check session timeout
            if datetime.now(timezone.utc) - session.last_activity > timedelta(seconds=self.session_timeout):
                await self._terminate_session(session_id, "Session timeout")
                return None
            
            # Update last activity
            session.last_activity = datetime.now(timezone.utc)
            
            # Check permissions
            if required_permissions:
                if not all(perm in session.permissions for perm in required_permissions):
                    await self._create_security_alert(
                        SecurityEvent.UNAUTHORIZED_ACCESS,
                        SecurityLevel.HIGH,
                        user_id,
                        session.ip_address,
                        {'required_permissions': required_permissions, 'user_permissions': list(session.permissions)}
                    )
                    return None
            
            return {
                'user_id': user_id,
                'session_id': session_id,
                'role': session.user_role.value,
                'permissions': list(session.permissions),
                'security_level': session.security_level.value
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return None
    
    async def authorize_action(self, user_id: str, action: str, 
                             resource_id: Optional[str] = None,
                             context: Optional[Dict] = None) -> bool:
        """
        Authorize user action on a resource
        
        Args:
            user_id: User identifier
            action: Action to authorize
            resource_id: Resource identifier
            context: Additional context for authorization
            
        Returns:
            True if authorized
        """
        # Find user session
        user_sessions = self.user_sessions.get(user_id, set())
        if not user_sessions:
            return False
        
        # Get most recent session
        session_id = max(user_sessions, key=lambda s: self.active_sessions[s].last_activity)
        session = self.active_sessions[session_id]
        
        # Check basic permission
        if action not in session.permissions:
            await self._create_security_alert(
                SecurityEvent.UNAUTHORIZED_ACCESS,
                SecurityLevel.MEDIUM,
                user_id,
                session.ip_address,
                {'action': action, 'resource_id': resource_id}
            )
            return False
        
        # Resource-specific authorization
        if resource_id and not await self._authorize_resource_access(session, action, resource_id, context):
            await self._create_security_alert(
                SecurityEvent.UNAUTHORIZED_ACCESS,
                SecurityLevel.HIGH,
                user_id,
                session.ip_address,
                {'action': action, 'resource_id': resource_id, 'context': context}
            )
            return False
        
        return True
    
    async def encrypt_data(self, data: bytes) -> str:
        """Encrypt data using Fernet encryption"""
        try:
            encrypted_data = self.cipher.encrypt(data)
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            await self._create_security_alert(
                SecurityEvent.ENCRYPTION_ERROR,
                SecurityLevel.HIGH,
                None,
                None,
                {'error': str(e), 'operation': 'encrypt'}
            )
            raise
    
    async def decrypt_data(self, encrypted_data: str) -> bytes:
        """Decrypt data using Fernet encryption"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            return self.cipher.decrypt(encrypted_bytes)
        except Exception as e:
            await self._create_security_alert(
                SecurityEvent.ENCRYPTION_ERROR,
                SecurityLevel.HIGH,
                None,
                None,
                {'error': str(e), 'operation': 'decrypt'}
            )
            raise
    
    async def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    async def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    async def sign_data(self, data: bytes) -> str:
        """Generate digital signature for data"""
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    async def verify_signature(self, data: bytes, signature: str) -> bool:
        """Verify digital signature"""
        try:
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            self.public_key.verify(
                signature_bytes,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    async def logout_user(self, session_id: str) -> bool:
        """Logout user and terminate session"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        await self._terminate_session(session_id, "User logout")
        
        logger.info(f"User {session.user_id} logged out")
        return True
    
    async def change_password(self, user_id: str, old_password: str, 
                            new_password: str) -> bool:
        """Change user password with validation"""
        # Validate old password (placeholder)
        if not await self._validate_user_password(user_id, old_password):
            return False
        
        # Validate new password strength
        if not await self._validate_password_strength(new_password):
            return False
        
        # Hash new password
        new_hash = await self.hash_password(new_password)
        
        # Update password (placeholder - implement actual database update)
        success = await self._update_user_password(user_id, new_hash)
        
        if success:
            await self._create_security_alert(
                SecurityEvent.PASSWORD_CHANGE,
                SecurityLevel.LOW,
                user_id,
                None,
                {'timestamp': datetime.now(timezone.utc).isoformat()}
            )
        
        return success
    
    async def _create_session(self, user_id: str, user_role: UserRole,
                            ip_address: str, user_agent: str) -> SecuritySession:
        """Create new security session"""
        session_id = str(uuid.uuid4())
        
        # Determine security level based on role and context
        security_level = await self._determine_security_level(user_role, ip_address)
        
        # Get permissions for role
        permissions = self.role_permissions.get(user_role, set()).copy()
        
        session = SecuritySession(
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            security_level=security_level,
            permissions=permissions,
            metadata={}
        )
        
        with self.lock:
            self.active_sessions[session_id] = session
            self.user_sessions[user_id].add(session_id)
            self.stats['active_sessions'] += 1
        
        return session
    
    async def _terminate_session(self, session_id: str, reason: str):
        """Terminate security session"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        with self.lock:
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            # Remove from user sessions
            self.user_sessions[session.user_id].discard(session_id)
            if not self.user_sessions[session.user_id]:
                del self.user_sessions[session.user_id]
            
            self.stats['active_sessions'] -= 1
        
        logger.info(f"Session {session_id} terminated: {reason}")
    
    async def _generate_jwt_token(self, user_id: str, user_role: UserRole, 
                                session_id: str) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'role': user_role.value,
            'session_id': session_id,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(seconds=self.session_timeout)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    async def _determine_security_level(self, user_role: UserRole, 
                                      ip_address: str) -> SecurityLevel:
        """Determine security level based on role and context"""
        # High security for admin roles
        if user_role in [UserRole.SYSTEM_ADMIN, UserRole.LAW_ENFORCEMENT]:
            return SecurityLevel.CRITICAL
        
        # Medium security for family admins
        if user_role == UserRole.FAMILY_ADMIN:
            return SecurityLevel.HIGH
        
        # Check for suspicious IP
        if ip_address in self.suspicious_ips:
            return SecurityLevel.HIGH
        
        return SecurityLevel.MEDIUM
    
    async def _check_rate_limit(self, identifier: str, action: str, 
                              limit: int, window: int) -> bool:
        """Check rate limiting for identifier and action"""
        key = f"{identifier}:{action}"
        current_time = time.time()
        
        # Clean old entries
        self.rate_limits[key] = deque([
            timestamp for timestamp in self.rate_limits[key]
            if current_time - timestamp < window
        ], maxlen=100)
        
        # Check limit
        if len(self.rate_limits[key]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[key].append(current_time)
        return True
    
    async def _authorize_resource_access(self, session: SecuritySession, 
                                       action: str, resource_id: str,
                                       context: Optional[Dict] = None) -> bool:
        """Authorize access to specific resource"""
        # Guardian can only access their own children's data
        if session.user_role == UserRole.GUARDIAN:
            if action.startswith('view_child') or action.startswith('manage_child'):
                # Check if resource belongs to guardian (placeholder)
                return await self._check_guardian_child_relationship(session.user_id, resource_id)
        
        # System admin has access to everything
        if session.user_role == UserRole.SYSTEM_ADMIN:
            return True
        
        # Law enforcement needs special authorization for evidence
        if session.user_role == UserRole.LAW_ENFORCEMENT:
            if action.startswith('view_evidence'):
                return await self._check_law_enforcement_authorization(session.user_id, resource_id)
        
        return True
    
    async def _create_security_alert(self, event_type: SecurityEvent, 
                                   severity: SecurityLevel, user_id: Optional[str],
                                   ip_address: Optional[str], details: Dict):
        """Create security alert"""
        alert = SecurityAlert(
            alert_id=str(uuid.uuid4()),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc),
            details=details
        )
        
        self.security_alerts.append(alert)
        self.stats['security_alerts'] += 1
        
        # Log high severity alerts
        if severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            logger.warning(f"Security Alert [{severity.value.upper()}]: {event_type.value} - {details}")
        
        # Add to suspicious IPs if needed
        if (event_type in [SecurityEvent.UNAUTHORIZED_ACCESS, SecurityEvent.DATA_BREACH_ATTEMPT] 
            and ip_address):
            self.suspicious_ips.add(ip_address)
    
    async def _session_monitor(self):
        """Background task to monitor sessions"""
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    # Check for expired sessions
                    if current_time - session.last_activity > timedelta(seconds=self.session_timeout):
                        expired_sessions.append(session_id)
                
                # Terminate expired sessions
                for session_id in expired_sessions:
                    await self._terminate_session(session_id, "Session timeout")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in session monitor: {str(e)}")
    
    async def _security_monitor(self):
        """Background task to monitor security events"""
        while self.is_running:
            try:
                # Monitor for suspicious patterns
                await self._detect_suspicious_patterns()
                
                # Clean up old alerts
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
                self.security_alerts = [
                    alert for alert in self.security_alerts
                    if alert.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in security monitor: {str(e)}")
    
    async def _detect_suspicious_patterns(self):
        """Detect suspicious activity patterns"""
        # Analyze recent alerts for patterns
        recent_alerts = [
            alert for alert in self.security_alerts
            if datetime.now(timezone.utc) - alert.timestamp < timedelta(hours=1)
        ]
        
        # Group by IP address
        ip_alerts = defaultdict(list)
        for alert in recent_alerts:
            if alert.ip_address:
                ip_alerts[alert.ip_address].append(alert)
        
        # Check for suspicious IPs
        for ip_address, alerts in ip_alerts.items():
            if len(alerts) > 10:  # More than 10 alerts in 1 hour
                if ip_address not in self.suspicious_ips:
                    self.suspicious_ips.add(ip_address)
                    await self._create_security_alert(
                        SecurityEvent.SUSPICIOUS_ACTIVITY,
                        SecurityLevel.HIGH,
                        None,
                        ip_address,
                        {'reason': 'High alert frequency', 'alert_count': len(alerts)}
                    )
    
    async def _cleanup_task(self):
        """Background cleanup task"""
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Clean up old login attempts
                for username in list(self.login_attempts.keys()):
                    self.login_attempts[username] = deque([
                        attempt for attempt in self.login_attempts[username]
                        if current_time - attempt < timedelta(hours=24)
                    ], maxlen=10)
                    
                    if not self.login_attempts[username]:
                        del self.login_attempts[username]
                
                # Clean up expired account lockouts
                expired_lockouts = [
                    username for username, lockout_time in self.locked_accounts.items()
                    if current_time > lockout_time
                ]
                
                for username in expired_lockouts:
                    del self.locked_accounts[username]
                
                # Clean up old rate limit data
                for key in list(self.rate_limits.keys()):
                    self.rate_limits[key] = deque([
                        timestamp for timestamp in self.rate_limits[key]
                        if current_time.timestamp() - timestamp < 3600  # 1 hour
                    ], maxlen=100)
                    
                    if not self.rate_limits[key]:
                        del self.rate_limits[key]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
    
    async def _statistics_updater(self):
        """Background task to update statistics"""
        while self.is_running:
            try:
                # Update active session count
                self.stats['active_sessions'] = len(self.active_sessions)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error updating statistics: {str(e)}")
    
    # Placeholder methods for external integrations
    async def _validate_credentials(self, username: str, password: str) -> Optional[Dict]:
        """Validate user credentials (placeholder)"""
        # Implement actual user lookup and password verification
        # This is a placeholder that simulates successful authentication
        if username == "guardian@safeguardian.com" and password == "guardian123":
            return {
                'user_id': 'guardian_123',
                'username': username,
                'role': UserRole.GUARDIAN.value,
                'email': username
            }
        return None
    
    async def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        # Implement password strength validation
        return len(password) >= 8
    
    async def _update_user_password(self, user_id: str, password_hash: str) -> bool:
        """Update user password in database"""
        # Implement actual database update
        return True
    
    async def _validate_user_password(self, user_id: str, password: str) -> bool:
        """Validate user's current password"""
        # Implement actual password validation
        return True
    
    async def _check_guardian_child_relationship(self, guardian_id: str, child_id: str) -> bool:
        """Check if guardian has access to child"""
        # Implement actual relationship check
        return True
    
    async def _check_law_enforcement_authorization(self, user_id: str, evidence_id: str) -> bool:
        """Check law enforcement authorization for evidence"""
        # Implement actual authorization check
        return True
    
    # Public API methods
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'role': session.user_role.value,
            'ip_address': session.ip_address,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'security_level': session.security_level.value,
            'permissions': list(session.permissions)
        }
    
    def get_security_alerts(self, severity: Optional[SecurityLevel] = None,
                          limit: int = 100) -> List[Dict]:
        """Get security alerts"""
        alerts = self.security_alerts
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        # Sort by timestamp (newest first) and limit
        alerts = sorted(alerts, key=lambda a: a.timestamp, reverse=True)[:limit]
        
        return [asdict(alert) for alert in alerts]
    
    def get_statistics(self) -> Dict:
        """Get security statistics"""
        return self.stats.copy()
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        return [self.get_session_info(session_id) for session_id in self.active_sessions.keys()]

# Factory function
def create_security_manager(config: Optional[Dict] = None) -> SecurityManager:
    """Create a new security manager instance"""
    return SecurityManager(config)

# Example usage
if __name__ == "__main__":
    async def test_security_manager():
        manager = create_security_manager()
        
        # Start security manager
        await manager.start()
        
        # Test authentication
        auth_result = await manager.authenticate_user(
            "guardian@safeguardian.com",
            "guardian123",
            "192.168.1.100",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        if auth_result:
            print(f"Authentication successful: {auth_result['user_id']}")
            
            # Test token validation
            token_data = await manager.validate_token(auth_result['token'])
            print(f"Token validation: {token_data is not None}")
            
            # Test authorization
            authorized = await manager.authorize_action(
                auth_result['user_id'],
                'view_children_profiles'
            )
            print(f"Authorization check: {authorized}")
        
        # Get statistics
        stats = manager.get_statistics()
        print(f"Security Statistics: {json.dumps(stats, indent=2, default=str)}")
        
        # Stop security manager
        await manager.stop()
    
    # Run test
    asyncio.run(test_security_manager())

