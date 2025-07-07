"""
SafeGuardian Forensic Logging System
Provides forensic-grade evidence collection and chain of custody tracking
for legal proceedings and law enforcement cooperation
"""

import asyncio
import json
import logging
import hashlib
import hmac
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvidenceType(Enum):
    MESSAGE = "message"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    METADATA = "metadata"
    SYSTEM_LOG = "system_log"
    AI_ANALYSIS = "ai_analysis"
    USER_ACTION = "user_action"

class EvidenceStatus(Enum):
    COLLECTED = "collected"
    VERIFIED = "verified"
    SEALED = "sealed"
    TRANSFERRED = "transferred"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"

class AccessLevel(Enum):
    SYSTEM = "system"
    GUARDIAN = "guardian"
    ADMIN = "admin"
    LAW_ENFORCEMENT = "law_enforcement"
    COURT_ORDER = "court_order"

@dataclass
class ChainOfCustodyEntry:
    timestamp: datetime
    action: str
    user_id: str
    user_role: str
    details: Dict
    signature: str
    previous_hash: str

@dataclass
class EvidenceRecord:
    evidence_id: str
    case_id: str
    evidence_type: EvidenceType
    status: EvidenceStatus
    collected_at: datetime
    collected_by: str
    source_platform: str
    source_session: str
    content_hash: str
    encrypted_content: bytes
    metadata: Dict
    chain_of_custody: List[ChainOfCustodyEntry]
    access_log: List[Dict]
    retention_until: Optional[datetime] = None
    legal_hold: bool = False

class ForensicLogger:
    """
    Forensic-grade logging system for SafeGuardian
    Provides tamper-evident evidence collection with chain of custody
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Encryption setup
        self._setup_encryption()
        
        # Database setup
        self.db_path = self.config.get('db_path', '/tmp/safeguardian_forensics.db')
        self._setup_database()
        
        # Evidence storage
        self.evidence_store: Dict[str, EvidenceRecord] = {}
        self.case_store: Dict[str, Dict] = {}
        
        # Security settings
        self.max_evidence_size = self.config.get('max_evidence_size', 100 * 1024 * 1024)  # 100MB
        self.retention_days = self.config.get('retention_days', 2555)  # 7 years default
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'total_evidence_collected': 0,
            'total_cases': 0,
            'total_access_requests': 0,
            'integrity_violations': 0,
            'start_time': datetime.now(timezone.utc)
        }
        
        logger.info("SafeGuardian Forensic Logger initialized")
    
    def _setup_encryption(self):
        """Setup encryption keys and ciphers"""
        # Generate or load master key
        master_key = self.config.get('master_key')
        if not master_key:
            master_key = Fernet.generate_key()
            logger.warning("Generated new master key - store securely!")
        
        self.cipher = Fernet(master_key)
        
        # Generate RSA key pair for digital signatures
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        logger.info("Encryption system initialized")
    
    def _setup_database(self):
        """Setup SQLite database for forensic records"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create evidence table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    collected_at TEXT NOT NULL,
                    collected_by TEXT NOT NULL,
                    source_platform TEXT,
                    source_session TEXT,
                    content_hash TEXT NOT NULL,
                    encrypted_content BLOB NOT NULL,
                    metadata TEXT,
                    retention_until TEXT,
                    legal_hold INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases (case_id)
                )
            ''')
            
            # Create chain of custody table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chain_of_custody (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    details TEXT,
                    signature TEXT NOT NULL,
                    previous_hash TEXT,
                    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
                )
            ''')
            
            # Create access log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    access_type TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    success INTEGER NOT NULL,
                    reason TEXT,
                    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
                )
            ''')
            
            # Create cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    case_name TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    guardian_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    assigned_to TEXT,
                    metadata TEXT,
                    legal_hold INTEGER DEFAULT 0
                )
            ''')
            
            # Create integrity verification table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS integrity_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id TEXT NOT NULL,
                    check_timestamp TEXT NOT NULL,
                    expected_hash TEXT NOT NULL,
                    actual_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Forensic database initialized")
            
        except Exception as e:
            logger.error(f"Error setting up forensic database: {str(e)}")
            raise
    
    async def create_case(self, case_data: Dict) -> str:
        """
        Create a new forensic case
        
        Args:
            case_data: Case information including child_id, guardian_id, etc.
            
        Returns:
            Case ID
        """
        case_id = str(uuid.uuid4())
        
        case_record = {
            'case_id': case_id,
            'case_name': case_data.get('case_name', f"SafeGuardian Case {case_id[:8]}"),
            'child_id': case_data['child_id'],
            'guardian_id': case_data['guardian_id'],
            'created_at': datetime.now(timezone.utc),
            'status': case_data.get('status', 'active'),
            'priority': case_data.get('priority', 'medium'),
            'assigned_to': case_data.get('assigned_to'),
            'metadata': case_data.get('metadata', {}),
            'legal_hold': case_data.get('legal_hold', False)
        }
        
        with self.lock:
            self.case_store[case_id] = case_record
            self.stats['total_cases'] += 1
        
        # Store in database
        await self._store_case_in_db(case_record)
        
        logger.info(f"Created forensic case: {case_id}")
        return case_id
    
    async def collect_evidence(self, case_id: str, evidence_data: Dict, 
                             collected_by: str) -> str:
        """
        Collect and store evidence with forensic integrity
        
        Args:
            case_id: Associated case ID
            evidence_data: Evidence content and metadata
            collected_by: User ID who collected the evidence
            
        Returns:
            Evidence ID
        """
        evidence_id = str(uuid.uuid4())
        
        # Validate evidence size
        content = evidence_data.get('content', '')
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        if len(content_bytes) > self.max_evidence_size:
            raise ValueError(f"Evidence size exceeds maximum allowed ({self.max_evidence_size} bytes)")
        
        # Calculate content hash
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Encrypt content
        encrypted_content = self.cipher.encrypt(content_bytes)
        
        # Calculate retention date
        retention_until = None
        if not evidence_data.get('legal_hold', False):
            retention_until = datetime.now(timezone.utc) + timedelta(days=self.retention_days)
        
        # Create evidence record
        evidence_record = EvidenceRecord(
            evidence_id=evidence_id,
            case_id=case_id,
            evidence_type=EvidenceType(evidence_data.get('type', EvidenceType.MESSAGE.value)),
            status=EvidenceStatus.COLLECTED,
            collected_at=datetime.now(timezone.utc),
            collected_by=collected_by,
            source_platform=evidence_data.get('source_platform', ''),
            source_session=evidence_data.get('source_session', ''),
            content_hash=content_hash,
            encrypted_content=encrypted_content,
            metadata=evidence_data.get('metadata', {}),
            chain_of_custody=[],
            access_log=[],
            retention_until=retention_until,
            legal_hold=evidence_data.get('legal_hold', False)
        )
        
        # Add initial chain of custody entry
        await self._add_custody_entry(
            evidence_record,
            "COLLECTED",
            collected_by,
            "system",
            {
                'collection_method': evidence_data.get('collection_method', 'automated'),
                'source_ip': evidence_data.get('source_ip'),
                'timestamp': evidence_record.collected_at.isoformat()
            }
        )
        
        with self.lock:
            self.evidence_store[evidence_id] = evidence_record
            self.stats['total_evidence_collected'] += 1
        
        # Store in database
        await self._store_evidence_in_db(evidence_record)
        
        logger.info(f"Collected evidence: {evidence_id} for case: {case_id}")
        return evidence_id
    
    async def access_evidence(self, evidence_id: str, user_id: str, 
                            user_role: str, access_reason: str,
                            request_metadata: Optional[Dict] = None) -> Optional[Dict]:
        """
        Access evidence with proper authorization and logging
        
        Args:
            evidence_id: Evidence identifier
            user_id: User requesting access
            user_role: Role of the user
            access_reason: Reason for access
            request_metadata: Additional request metadata
            
        Returns:
            Decrypted evidence data or None if access denied
        """
        if evidence_id not in self.evidence_store:
            await self._log_access_attempt(
                evidence_id, user_id, user_role, "READ", False, 
                "Evidence not found", request_metadata
            )
            return None
        
        evidence = self.evidence_store[evidence_id]
        
        # Check access authorization
        if not await self._authorize_access(evidence, user_id, user_role, access_reason):
            await self._log_access_attempt(
                evidence_id, user_id, user_role, "READ", False,
                "Access denied - insufficient privileges", request_metadata
            )
            return None
        
        # Log successful access
        await self._log_access_attempt(
            evidence_id, user_id, user_role, "READ", True,
            access_reason, request_metadata
        )
        
        # Add chain of custody entry
        await self._add_custody_entry(
            evidence,
            "ACCESSED",
            user_id,
            user_role,
            {
                'access_reason': access_reason,
                'ip_address': request_metadata.get('ip_address') if request_metadata else None
            }
        )
        
        # Decrypt and return evidence
        try:
            decrypted_content = self.cipher.decrypt(evidence.encrypted_content)
            
            # Verify integrity
            actual_hash = hashlib.sha256(decrypted_content).hexdigest()
            if actual_hash != evidence.content_hash:
                logger.error(f"Integrity violation detected for evidence {evidence_id}")
                self.stats['integrity_violations'] += 1
                await self._record_integrity_violation(evidence_id, evidence.content_hash, actual_hash)
                return None
            
            return {
                'evidence_id': evidence_id,
                'case_id': evidence.case_id,
                'type': evidence.evidence_type.value,
                'collected_at': evidence.collected_at.isoformat(),
                'collected_by': evidence.collected_by,
                'content': decrypted_content.decode('utf-8') if evidence.evidence_type == EvidenceType.MESSAGE else decrypted_content,
                'metadata': evidence.metadata,
                'content_hash': evidence.content_hash,
                'chain_of_custody_entries': len(evidence.chain_of_custody),
                'access_count': len(evidence.access_log)
            }
            
        except Exception as e:
            logger.error(f"Error decrypting evidence {evidence_id}: {str(e)}")
            await self._log_access_attempt(
                evidence_id, user_id, user_role, "READ", False,
                f"Decryption error: {str(e)}", request_metadata
            )
            return None
    
    async def seal_evidence(self, evidence_id: str, sealed_by: str, 
                          seal_reason: str) -> bool:
        """
        Seal evidence to prevent further modifications
        
        Args:
            evidence_id: Evidence identifier
            sealed_by: User sealing the evidence
            seal_reason: Reason for sealing
            
        Returns:
            True if successful
        """
        if evidence_id not in self.evidence_store:
            return False
        
        evidence = self.evidence_store[evidence_id]
        
        if evidence.status == EvidenceStatus.SEALED:
            logger.warning(f"Evidence {evidence_id} is already sealed")
            return False
        
        # Update status
        evidence.status = EvidenceStatus.SEALED
        
        # Add chain of custody entry
        await self._add_custody_entry(
            evidence,
            "SEALED",
            sealed_by,
            "admin",
            {
                'seal_reason': seal_reason,
                'sealed_at': datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Update database
        await self._update_evidence_status(evidence_id, EvidenceStatus.SEALED)
        
        logger.info(f"Evidence {evidence_id} sealed by {sealed_by}: {seal_reason}")
        return True
    
    async def transfer_evidence(self, evidence_id: str, transferred_by: str,
                              recipient: str, transfer_reason: str) -> bool:
        """
        Transfer evidence to another party (e.g., law enforcement)
        
        Args:
            evidence_id: Evidence identifier
            transferred_by: User initiating transfer
            recipient: Recipient of the evidence
            transfer_reason: Reason for transfer
            
        Returns:
            True if successful
        """
        if evidence_id not in self.evidence_store:
            return False
        
        evidence = self.evidence_store[evidence_id]
        
        # Update status
        evidence.status = EvidenceStatus.TRANSFERRED
        
        # Add chain of custody entry
        await self._add_custody_entry(
            evidence,
            "TRANSFERRED",
            transferred_by,
            "admin",
            {
                'recipient': recipient,
                'transfer_reason': transfer_reason,
                'transferred_at': datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Update database
        await self._update_evidence_status(evidence_id, EvidenceStatus.TRANSFERRED)
        
        logger.info(f"Evidence {evidence_id} transferred to {recipient} by {transferred_by}")
        return True
    
    async def verify_evidence_integrity(self, evidence_id: str) -> Dict:
        """
        Verify the integrity of stored evidence
        
        Args:
            evidence_id: Evidence identifier
            
        Returns:
            Verification result
        """
        if evidence_id not in self.evidence_store:
            return {'status': 'error', 'message': 'Evidence not found'}
        
        evidence = self.evidence_store[evidence_id]
        
        try:
            # Decrypt content
            decrypted_content = self.cipher.decrypt(evidence.encrypted_content)
            
            # Calculate current hash
            actual_hash = hashlib.sha256(decrypted_content).hexdigest()
            
            # Compare with stored hash
            integrity_valid = actual_hash == evidence.content_hash
            
            # Verify chain of custody integrity
            custody_valid = await self._verify_custody_chain(evidence)
            
            result = {
                'evidence_id': evidence_id,
                'integrity_valid': integrity_valid,
                'custody_chain_valid': custody_valid,
                'expected_hash': evidence.content_hash,
                'actual_hash': actual_hash,
                'verification_timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'valid' if integrity_valid and custody_valid else 'invalid'
            }
            
            # Record verification in database
            await self._record_integrity_check(evidence_id, result)
            
            if not integrity_valid:
                self.stats['integrity_violations'] += 1
                logger.error(f"Integrity violation detected for evidence {evidence_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error verifying evidence {evidence_id}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'verification_timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def generate_evidence_report(self, case_id: str, 
                                     requested_by: str) -> Dict:
        """
        Generate comprehensive evidence report for a case
        
        Args:
            case_id: Case identifier
            requested_by: User requesting the report
            
        Returns:
            Evidence report
        """
        if case_id not in self.case_store:
            return {'error': 'Case not found'}
        
        case = self.case_store[case_id]
        
        # Get all evidence for the case
        case_evidence = [
            evidence for evidence in self.evidence_store.values()
            if evidence.case_id == case_id
        ]
        
        # Generate report
        report = {
            'report_id': str(uuid.uuid4()),
            'case_id': case_id,
            'case_name': case['case_name'],
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'generated_by': requested_by,
            'evidence_summary': {
                'total_evidence_items': len(case_evidence),
                'evidence_types': {},
                'collection_timespan': {},
                'integrity_status': {}
            },
            'evidence_details': [],
            'chain_of_custody_summary': {},
            'access_summary': {}
        }
        
        # Analyze evidence
        for evidence in case_evidence:
            # Count by type
            evidence_type = evidence.evidence_type.value
            report['evidence_summary']['evidence_types'][evidence_type] = \
                report['evidence_summary']['evidence_types'].get(evidence_type, 0) + 1
            
            # Verify integrity
            verification = await self.verify_evidence_integrity(evidence.evidence_id)
            status = verification.get('status', 'unknown')
            report['evidence_summary']['integrity_status'][status] = \
                report['evidence_summary']['integrity_status'].get(status, 0) + 1
            
            # Add evidence details
            evidence_detail = {
                'evidence_id': evidence.evidence_id,
                'type': evidence_type,
                'collected_at': evidence.collected_at.isoformat(),
                'collected_by': evidence.collected_by,
                'status': evidence.status.value,
                'content_hash': evidence.content_hash,
                'custody_entries': len(evidence.chain_of_custody),
                'access_count': len(evidence.access_log),
                'integrity_verified': verification.get('integrity_valid', False)
            }
            
            report['evidence_details'].append(evidence_detail)
        
        # Calculate timespan
        if case_evidence:
            collection_times = [e.collected_at for e in case_evidence]
            report['evidence_summary']['collection_timespan'] = {
                'earliest': min(collection_times).isoformat(),
                'latest': max(collection_times).isoformat()
            }
        
        logger.info(f"Generated evidence report for case {case_id}")
        return report
    
    async def _add_custody_entry(self, evidence: EvidenceRecord, action: str,
                               user_id: str, user_role: str, details: Dict):
        """Add entry to chain of custody"""
        timestamp = datetime.now(timezone.utc)
        
        # Calculate previous hash
        previous_hash = ""
        if evidence.chain_of_custody:
            last_entry = evidence.chain_of_custody[-1]
            previous_hash = last_entry.signature
        
        # Create entry data
        entry_data = {
            'timestamp': timestamp.isoformat(),
            'action': action,
            'user_id': user_id,
            'user_role': user_role,
            'details': details,
            'previous_hash': previous_hash
        }
        
        # Generate signature
        entry_json = json.dumps(entry_data, sort_keys=True)
        signature = self._sign_data(entry_json.encode('utf-8'))
        
        # Create custody entry
        custody_entry = ChainOfCustodyEntry(
            timestamp=timestamp,
            action=action,
            user_id=user_id,
            user_role=user_role,
            details=details,
            signature=signature,
            previous_hash=previous_hash
        )
        
        evidence.chain_of_custody.append(custody_entry)
        
        # Store in database
        await self._store_custody_entry(evidence.evidence_id, custody_entry)
    
    async def _authorize_access(self, evidence: EvidenceRecord, user_id: str,
                              user_role: str, access_reason: str) -> bool:
        """Check if user is authorized to access evidence"""
        # System access always allowed
        if user_role == AccessLevel.SYSTEM.value:
            return True
        
        # Court order access always allowed
        if user_role == AccessLevel.COURT_ORDER.value:
            return True
        
        # Law enforcement access for sealed evidence
        if (user_role == AccessLevel.LAW_ENFORCEMENT.value and 
            evidence.status == EvidenceStatus.SEALED):
            return True
        
        # Admin access
        if user_role == AccessLevel.ADMIN.value:
            return True
        
        # Guardian access to their own case
        if user_role == AccessLevel.GUARDIAN.value:
            case = self.case_store.get(evidence.case_id)
            if case and case['guardian_id'] == user_id:
                return True
        
        return False
    
    async def _log_access_attempt(self, evidence_id: str, user_id: str,
                                user_role: str, access_type: str, success: bool,
                                reason: str, metadata: Optional[Dict] = None):
        """Log evidence access attempt"""
        access_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_id': user_id,
            'user_role': user_role,
            'access_type': access_type,
            'success': success,
            'reason': reason,
            'ip_address': metadata.get('ip_address') if metadata else None,
            'user_agent': metadata.get('user_agent') if metadata else None
        }
        
        if evidence_id in self.evidence_store:
            self.evidence_store[evidence_id].access_log.append(access_entry)
        
        self.stats['total_access_requests'] += 1
        
        # Store in database
        await self._store_access_log(evidence_id, access_entry)
    
    def _sign_data(self, data: bytes) -> str:
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
    
    def _verify_signature(self, data: bytes, signature: str) -> bool:
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
    
    async def _verify_custody_chain(self, evidence: EvidenceRecord) -> bool:
        """Verify integrity of chain of custody"""
        if not evidence.chain_of_custody:
            return True
        
        previous_hash = ""
        for entry in evidence.chain_of_custody:
            # Verify previous hash linkage
            if entry.previous_hash != previous_hash:
                return False
            
            # Verify signature
            entry_data = {
                'timestamp': entry.timestamp.isoformat(),
                'action': entry.action,
                'user_id': entry.user_id,
                'user_role': entry.user_role,
                'details': entry.details,
                'previous_hash': entry.previous_hash
            }
            entry_json = json.dumps(entry_data, sort_keys=True)
            
            if not self._verify_signature(entry_json.encode('utf-8'), entry.signature):
                return False
            
            previous_hash = entry.signature
        
        return True
    
    # Database operations
    async def _store_case_in_db(self, case_record: Dict):
        """Store case record in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO cases (case_id, case_name, child_id, guardian_id, 
                                 created_at, status, priority, assigned_to, metadata, legal_hold)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_record['case_id'],
                case_record['case_name'],
                case_record['child_id'],
                case_record['guardian_id'],
                case_record['created_at'].isoformat(),
                case_record['status'],
                case_record['priority'],
                case_record.get('assigned_to'),
                json.dumps(case_record['metadata']),
                1 if case_record['legal_hold'] else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing case in database: {str(e)}")
    
    async def _store_evidence_in_db(self, evidence: EvidenceRecord):
        """Store evidence record in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO evidence (evidence_id, case_id, evidence_type, status,
                                    collected_at, collected_by, source_platform, source_session,
                                    content_hash, encrypted_content, metadata, retention_until, legal_hold)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                evidence.evidence_id,
                evidence.case_id,
                evidence.evidence_type.value,
                evidence.status.value,
                evidence.collected_at.isoformat(),
                evidence.collected_by,
                evidence.source_platform,
                evidence.source_session,
                evidence.content_hash,
                evidence.encrypted_content,
                json.dumps(evidence.metadata),
                evidence.retention_until.isoformat() if evidence.retention_until else None,
                1 if evidence.legal_hold else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing evidence in database: {str(e)}")
    
    async def _store_custody_entry(self, evidence_id: str, entry: ChainOfCustodyEntry):
        """Store chain of custody entry in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chain_of_custody (evidence_id, timestamp, action, user_id,
                                            user_role, details, signature, previous_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                evidence_id,
                entry.timestamp.isoformat(),
                entry.action,
                entry.user_id,
                entry.user_role,
                json.dumps(entry.details),
                entry.signature,
                entry.previous_hash
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing custody entry in database: {str(e)}")
    
    async def _store_access_log(self, evidence_id: str, access_entry: Dict):
        """Store access log entry in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_log (evidence_id, timestamp, user_id, user_role,
                                      access_type, ip_address, user_agent, success, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                evidence_id,
                access_entry['timestamp'],
                access_entry['user_id'],
                access_entry['user_role'],
                access_entry['access_type'],
                access_entry.get('ip_address'),
                access_entry.get('user_agent'),
                1 if access_entry['success'] else 0,
                access_entry['reason']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing access log in database: {str(e)}")
    
    async def _update_evidence_status(self, evidence_id: str, status: EvidenceStatus):
        """Update evidence status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE evidence SET status = ? WHERE evidence_id = ?
            ''', (status.value, evidence_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating evidence status in database: {str(e)}")
    
    async def _record_integrity_check(self, evidence_id: str, result: Dict):
        """Record integrity check result in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO integrity_checks (evidence_id, check_timestamp, expected_hash,
                                            actual_hash, status, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                evidence_id,
                result['verification_timestamp'],
                result['expected_hash'],
                result['actual_hash'],
                result['status'],
                json.dumps(result)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error recording integrity check in database: {str(e)}")
    
    async def _record_integrity_violation(self, evidence_id: str, expected_hash: str, actual_hash: str):
        """Record integrity violation"""
        violation_record = {
            'evidence_id': evidence_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'expected_hash': expected_hash,
            'actual_hash': actual_hash,
            'severity': 'critical'
        }
        
        logger.critical(f"INTEGRITY VIOLATION: Evidence {evidence_id} - Expected: {expected_hash}, Actual: {actual_hash}")
        
        # Store violation record
        await self._record_integrity_check(evidence_id, {
            'verification_timestamp': violation_record['timestamp'],
            'expected_hash': expected_hash,
            'actual_hash': actual_hash,
            'status': 'violation',
            'integrity_valid': False,
            'custody_chain_valid': False
        })
    
    # Public API methods
    def get_case_info(self, case_id: str) -> Optional[Dict]:
        """Get case information"""
        return self.case_store.get(case_id)
    
    def get_evidence_info(self, evidence_id: str) -> Optional[Dict]:
        """Get evidence information (without content)"""
        if evidence_id not in self.evidence_store:
            return None
        
        evidence = self.evidence_store[evidence_id]
        return {
            'evidence_id': evidence.evidence_id,
            'case_id': evidence.case_id,
            'type': evidence.evidence_type.value,
            'status': evidence.status.value,
            'collected_at': evidence.collected_at.isoformat(),
            'collected_by': evidence.collected_by,
            'content_hash': evidence.content_hash,
            'custody_entries': len(evidence.chain_of_custody),
            'access_count': len(evidence.access_log),
            'legal_hold': evidence.legal_hold
        }
    
    def get_statistics(self) -> Dict:
        """Get forensic logger statistics"""
        return self.stats.copy()

# Factory function
def create_forensic_logger(config: Optional[Dict] = None) -> ForensicLogger:
    """Create a new forensic logger instance"""
    return ForensicLogger(config)

# Example usage
if __name__ == "__main__":
    async def test_forensic_logger():
        logger_instance = create_forensic_logger()
        
        # Create a case
        case_data = {
            'case_name': 'Test Grooming Case',
            'child_id': 'child_123',
            'guardian_id': 'guardian_456',
            'priority': 'high'
        }
        
        case_id = await logger_instance.create_case(case_data)
        print(f"Created case: {case_id}")
        
        # Collect evidence
        evidence_data = {
            'type': EvidenceType.MESSAGE.value,
            'content': 'You are so mature for your age. Don\'t tell your parents about our chats.',
            'source_platform': 'instagram',
            'metadata': {
                'sender_id': 'user_789',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'risk_level': 'critical'
            }
        }
        
        evidence_id = await logger_instance.collect_evidence(case_id, evidence_data, 'system')
        print(f"Collected evidence: {evidence_id}")
        
        # Verify integrity
        verification = await logger_instance.verify_evidence_integrity(evidence_id)
        print(f"Integrity verification: {verification}")
        
        # Access evidence
        evidence_content = await logger_instance.access_evidence(
            evidence_id, 'guardian_456', 'guardian', 'Review suspicious message'
        )
        print(f"Evidence accessed: {evidence_content is not None}")
        
        # Generate report
        report = await logger_instance.generate_evidence_report(case_id, 'admin_user')
        print(f"Generated report with {len(report.get('evidence_details', []))} evidence items")
        
        # Get statistics
        stats = logger_instance.get_statistics()
        print(f"Forensic Statistics: {json.dumps(stats, indent=2, default=str)}")
    
    # Run test
    asyncio.run(test_forensic_logger())

