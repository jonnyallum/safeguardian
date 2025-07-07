"""
SafeGuardian Real-time Monitoring System
Provides real-time monitoring of communications across platforms with AI-powered threat detection
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import threading
import time
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class MonitoringSession:
    session_id: str
    child_id: str
    platform: str
    status: MonitoringStatus
    start_time: datetime
    last_activity: datetime
    message_count: int = 0
    alert_count: int = 0
    risk_score: float = 0.0
    participants: List[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RealTimeAlert:
    alert_id: str
    session_id: str
    child_id: str
    platform: str
    severity: AlertSeverity
    alert_type: str
    message: str
    details: Dict
    timestamp: datetime
    acknowledged: bool = False
    escalated: bool = False
    guardian_notified: bool = False
    
class RealTimeMonitor:
    """
    Real-time monitoring system that tracks communications and triggers alerts
    """
    
    def __init__(self, ai_analysis_service=None, alert_service=None):
        self.ai_service = ai_analysis_service
        self.alert_service = alert_service
        
        # Active monitoring sessions
        self.active_sessions: Dict[str, MonitoringSession] = {}
        
        # Alert management
        self.active_alerts: Dict[str, RealTimeAlert] = {}
        self.alert_queue = asyncio.Queue()
        
        # Real-time data streams
        self.message_stream = asyncio.Queue()
        self.websocket_connections: Set = set()
        
        # Monitoring statistics
        self.stats = {
            'total_sessions': 0,
            'active_sessions': 0,
            'total_messages': 0,
            'alerts_triggered': 0,
            'high_risk_detections': 0,
            'start_time': datetime.now()
        }
        
        # Rate limiting and throttling
        self.rate_limits = defaultdict(lambda: deque(maxlen=100))
        
        # Background tasks
        self.monitoring_tasks = []
        self.is_running = False
        
    async def start_monitoring(self):
        """Start the real-time monitoring system"""
        if self.is_running:
            logger.warning("Monitoring system is already running")
            return
        
        self.is_running = True
        logger.info("Starting SafeGuardian real-time monitoring system...")
        
        # Start background tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._message_processor()),
            asyncio.create_task(self._alert_processor()),
            asyncio.create_task(self._session_monitor()),
            asyncio.create_task(self._statistics_updater()),
            asyncio.create_task(self._cleanup_task())
        ]
        
        logger.info("Real-time monitoring system started successfully")
    
    async def stop_monitoring(self):
        """Stop the real-time monitoring system"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping real-time monitoring system...")
        
        # Cancel all background tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        # Close all sessions
        for session in self.active_sessions.values():
            session.status = MonitoringStatus.STOPPED
        
        logger.info("Real-time monitoring system stopped")
    
    async def start_session(self, child_id: str, platform: str, 
                          metadata: Optional[Dict] = None) -> str:
        """
        Start a new monitoring session for a child on a platform
        
        Args:
            child_id: Unique identifier for the child
            platform: Platform name (e.g., 'instagram', 'facebook')
            metadata: Additional session metadata
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        session = MonitoringSession(
            session_id=session_id,
            child_id=child_id,
            platform=platform,
            status=MonitoringStatus.ACTIVE,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            metadata=metadata or {}
        )
        
        self.active_sessions[session_id] = session
        self.stats['total_sessions'] += 1
        self.stats['active_sessions'] += 1
        
        logger.info(f"Started monitoring session {session_id} for child {child_id} on {platform}")
        
        # Notify connected clients
        await self._broadcast_session_update(session)
        
        return session_id
    
    async def stop_session(self, session_id: str, reason: str = "Manual stop"):
        """Stop a monitoring session"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found")
            return
        
        session = self.active_sessions[session_id]
        session.status = MonitoringStatus.STOPPED
        session.metadata['stop_reason'] = reason
        session.metadata['stop_time'] = datetime.now().isoformat()
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        self.stats['active_sessions'] -= 1
        
        logger.info(f"Stopped monitoring session {session_id}: {reason}")
        
        # Notify connected clients
        await self._broadcast_session_update(session)
    
    async def process_message(self, session_id: str, message_data: Dict):
        """
        Process a new message in real-time
        
        Args:
            session_id: Session identifier
            message_data: Message data including content, sender, timestamp, etc.
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Message received for inactive session: {session_id}")
            return
        
        session = self.active_sessions[session_id]
        session.message_count += 1
        session.last_activity = datetime.now()
        self.stats['total_messages'] += 1
        
        # Add session context to message
        message_data.update({
            'session_id': session_id,
            'child_id': session.child_id,
            'platform': session.platform,
            'processing_timestamp': datetime.now().isoformat()
        })
        
        # Queue message for AI analysis
        await self.message_stream.put(message_data)
        
        # Update session participants
        sender_id = message_data.get('sender_id')
        if sender_id and sender_id not in session.participants:
            session.participants.append(sender_id)
        
        # Check rate limits
        await self._check_rate_limits(session_id, message_data)
        
        # Broadcast real-time update
        await self._broadcast_message_update(session_id, message_data)
    
    async def _message_processor(self):
        """Background task to process messages with AI analysis"""
        while self.is_running:
            try:
                # Get message from queue with timeout
                message_data = await asyncio.wait_for(
                    self.message_stream.get(), 
                    timeout=1.0
                )
                
                # Perform AI analysis if service is available
                if self.ai_service:
                    analysis_result = await self.ai_service.analyze_message_async(message_data)
                    
                    # Check if alert should be triggered
                    risk_level = analysis_result.get('risk_level', 'low')
                    confidence = analysis_result.get('confidence', 0.0)
                    
                    if risk_level in ['high', 'critical'] and confidence > 0.7:
                        await self._trigger_real_time_alert(message_data, analysis_result)
                    
                    # Update session risk score
                    session_id = message_data.get('session_id')
                    if session_id in self.active_sessions:
                        session = self.active_sessions[session_id]
                        # Update running average of risk score
                        current_risk = self._risk_level_to_score(risk_level) * confidence
                        session.risk_score = (session.risk_score * 0.8) + (current_risk * 0.2)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
    
    async def _alert_processor(self):
        """Background task to process and escalate alerts"""
        while self.is_running:
            try:
                # Get alert from queue with timeout
                alert = await asyncio.wait_for(
                    self.alert_queue.get(),
                    timeout=1.0
                )
                
                # Process the alert
                await self._process_alert(alert)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing alert: {str(e)}")
    
    async def _trigger_real_time_alert(self, message_data: Dict, analysis_result: Dict):
        """Trigger a real-time alert based on AI analysis"""
        session_id = message_data.get('session_id')
        child_id = message_data.get('child_id')
        platform = message_data.get('platform')
        
        # Determine alert severity
        risk_level = analysis_result.get('risk_level', 'low')
        confidence = analysis_result.get('confidence', 0.0)
        patterns = analysis_result.get('patterns_detected', [])
        
        severity = self._determine_alert_severity(risk_level, confidence, patterns)
        
        # Create alert
        alert = RealTimeAlert(
            alert_id=str(uuid.uuid4()),
            session_id=session_id,
            child_id=child_id,
            platform=platform,
            severity=severity,
            alert_type='grooming_detection',
            message=analysis_result.get('explanation', 'Potential grooming behavior detected'),
            details={
                'risk_level': risk_level,
                'confidence': confidence,
                'patterns_detected': patterns,
                'risk_factors': analysis_result.get('risk_factors', []),
                'recommendations': analysis_result.get('recommendations', []),
                'message_content': message_data.get('content', ''),
                'sender_id': message_data.get('sender_id'),
                'analysis_id': analysis_result.get('id')
            },
            timestamp=datetime.now()
        )
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        
        # Queue for processing
        await self.alert_queue.put(alert)
        
        # Update statistics
        self.stats['alerts_triggered'] += 1
        if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            self.stats['high_risk_detections'] += 1
        
        # Update session alert count
        if session_id in self.active_sessions:
            self.active_sessions[session_id].alert_count += 1
        
        logger.warning(f"Real-time alert triggered: {alert.alert_id} - {alert.message}")
        
        # Broadcast alert to connected clients
        await self._broadcast_alert(alert)
    
    async def _process_alert(self, alert: RealTimeAlert):
        """Process and escalate an alert"""
        try:
            # Immediate actions for critical alerts
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                # Notify guardians immediately
                await self._notify_guardians(alert)
                alert.guardian_notified = True
                
                # Auto-escalate emergency alerts
                if alert.severity == AlertSeverity.EMERGENCY:
                    await self._escalate_to_authorities(alert)
                    alert.escalated = True
            
            # Store alert in database if service available
            if self.alert_service:
                await self.alert_service.store_alert(alert)
            
            # Send notifications based on severity
            await self._send_alert_notifications(alert)
            
        except Exception as e:
            logger.error(f"Error processing alert {alert.alert_id}: {str(e)}")
    
    async def _session_monitor(self):
        """Background task to monitor session health and activity"""
        while self.is_running:
            try:
                current_time = datetime.now()
                inactive_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    # Check for inactive sessions (no activity for 30 minutes)
                    if current_time - session.last_activity > timedelta(minutes=30):
                        inactive_sessions.append(session_id)
                    
                    # Check for high-risk sessions
                    if session.risk_score > 0.7:
                        logger.warning(f"High-risk session detected: {session_id} (risk: {session.risk_score:.2f})")
                
                # Clean up inactive sessions
                for session_id in inactive_sessions:
                    await self.stop_session(session_id, "Inactive session timeout")
                
                # Sleep for 60 seconds before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in session monitor: {str(e)}")
    
    async def _statistics_updater(self):
        """Background task to update monitoring statistics"""
        while self.is_running:
            try:
                # Update active session count
                self.stats['active_sessions'] = len(self.active_sessions)
                
                # Calculate uptime
                uptime = datetime.now() - self.stats['start_time']
                self.stats['uptime_seconds'] = int(uptime.total_seconds())
                
                # Broadcast statistics update
                await self._broadcast_statistics()
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error updating statistics: {str(e)}")
    
    async def _cleanup_task(self):
        """Background task for cleanup operations"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Clean up old alerts (older than 24 hours)
                old_alerts = [
                    alert_id for alert_id, alert in self.active_alerts.items()
                    if current_time - alert.timestamp > timedelta(hours=24)
                ]
                
                for alert_id in old_alerts:
                    del self.active_alerts[alert_id]
                
                # Clean up rate limit data
                for session_id in list(self.rate_limits.keys()):
                    if session_id not in self.active_sessions:
                        del self.rate_limits[session_id]
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
    
    async def _check_rate_limits(self, session_id: str, message_data: Dict):
        """Check for unusual message rate patterns"""
        current_time = time.time()
        rate_data = self.rate_limits[session_id]
        
        # Add current message timestamp
        rate_data.append(current_time)
        
        # Check for rapid messaging (more than 10 messages per minute)
        recent_messages = [t for t in rate_data if current_time - t < 60]
        
        if len(recent_messages) > 10:
            # Trigger rate limit alert
            await self._trigger_rate_limit_alert(session_id, len(recent_messages))
    
    async def _trigger_rate_limit_alert(self, session_id: str, message_count: int):
        """Trigger alert for unusual messaging patterns"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        alert = RealTimeAlert(
            alert_id=str(uuid.uuid4()),
            session_id=session_id,
            child_id=session.child_id,
            platform=session.platform,
            severity=AlertSeverity.MEDIUM,
            alert_type='unusual_activity',
            message=f"Unusual messaging pattern detected: {message_count} messages in 1 minute",
            details={
                'message_count': message_count,
                'time_window': '1 minute',
                'threshold': 10
            },
            timestamp=datetime.now()
        )
        
        await self.alert_queue.put(alert)
    
    # Utility methods
    def _risk_level_to_score(self, risk_level: str) -> float:
        """Convert risk level to numeric score"""
        risk_scores = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8,
            'critical': 1.0
        }
        return risk_scores.get(risk_level, 0.0)
    
    def _determine_alert_severity(self, risk_level: str, confidence: float, 
                                patterns: List[str]) -> AlertSeverity:
        """Determine alert severity based on analysis results"""
        # Emergency: Critical risk with high confidence and dangerous patterns
        if (risk_level == 'critical' and confidence > 0.9 and 
            any(p in patterns for p in ['meeting_request', 'sexual_content'])):
            return AlertSeverity.EMERGENCY
        
        # Critical: High risk with good confidence
        if risk_level == 'critical' and confidence > 0.7:
            return AlertSeverity.CRITICAL
        
        # High: High risk or multiple concerning patterns
        if risk_level == 'high' or len(patterns) >= 3:
            return AlertSeverity.HIGH
        
        # Medium: Medium risk or some patterns
        if risk_level == 'medium' or len(patterns) >= 1:
            return AlertSeverity.MEDIUM
        
        return AlertSeverity.LOW
    
    # Notification methods (placeholders for actual implementation)
    async def _notify_guardians(self, alert: RealTimeAlert):
        """Send immediate notification to guardians"""
        logger.critical(f"GUARDIAN NOTIFICATION: {alert.message}")
        # Implement actual guardian notification (email, SMS, push notification)
    
    async def _escalate_to_authorities(self, alert: RealTimeAlert):
        """Escalate emergency alerts to authorities"""
        logger.critical(f"AUTHORITY ESCALATION: {alert.message}")
        # Implement actual authority notification system
    
    async def _send_alert_notifications(self, alert: RealTimeAlert):
        """Send notifications based on alert severity"""
        # Implement notification logic based on severity
        pass
    
    # WebSocket broadcasting methods (placeholders)
    async def _broadcast_session_update(self, session: MonitoringSession):
        """Broadcast session update to connected clients"""
        # Implement WebSocket broadcasting
        pass
    
    async def _broadcast_message_update(self, session_id: str, message_data: Dict):
        """Broadcast message update to connected clients"""
        # Implement WebSocket broadcasting
        pass
    
    async def _broadcast_alert(self, alert: RealTimeAlert):
        """Broadcast alert to connected clients"""
        # Implement WebSocket broadcasting
        pass
    
    async def _broadcast_statistics(self):
        """Broadcast statistics update to connected clients"""
        # Implement WebSocket broadcasting
        pass
    
    # Public API methods
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get current status of a monitoring session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        return asdict(session)
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active monitoring sessions"""
        return [asdict(session) for session in self.active_sessions.values()]
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [asdict(alert) for alert in self.active_alerts.values()]
    
    def get_statistics(self) -> Dict:
        """Get monitoring system statistics"""
        return self.stats.copy()
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.acknowledged = True
        alert.details['acknowledged_by'] = user_id
        alert.details['acknowledged_at'] = datetime.now().isoformat()
        
        logger.info(f"Alert {alert_id} acknowledged by {user_id}")
        return True

# Factory function
def create_real_time_monitor(ai_service=None, alert_service=None) -> RealTimeMonitor:
    """Create a new real-time monitor instance"""
    return RealTimeMonitor(ai_service, alert_service)

# Example usage
if __name__ == "__main__":
    async def test_monitor():
        monitor = create_real_time_monitor()
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Start a session
        session_id = await monitor.start_session("child_123", "instagram")
        
        # Simulate message processing
        test_message = {
            'content': "You're so mature for your age. Don't tell your parents about our chats.",
            'sender_id': 'user_456',
            'timestamp': datetime.now().isoformat()
        }
        
        await monitor.process_message(session_id, test_message)
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Get statistics
        stats = monitor.get_statistics()
        print(f"Monitoring Statistics: {json.dumps(stats, indent=2, default=str)}")
        
        # Stop monitoring
        await monitor.stop_monitoring()
    
    # Run test
    asyncio.run(test_monitor())

