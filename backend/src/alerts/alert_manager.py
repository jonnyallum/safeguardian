"""
SafeGuardian Alert Management System
Comprehensive alert handling, notification, and escalation system
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertType(Enum):
    GROOMING_DETECTION = "grooming_detection"
    UNUSUAL_ACTIVITY = "unusual_activity"
    PLATFORM_VIOLATION = "platform_violation"
    EMERGENCY_CONTACT = "emergency_contact"
    SYSTEM_ERROR = "system_error"
    MANUAL_REVIEW = "manual_review"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    DISMISSED = "dismissed"

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push_notification"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"
    EMERGENCY_CALL = "emergency_call"

class EscalationLevel(Enum):
    GUARDIAN = "guardian"
    FAMILY_ADMIN = "family_admin"
    SYSTEM_ADMIN = "system_admin"
    LAW_ENFORCEMENT = "law_enforcement"
    EMERGENCY_SERVICES = "emergency_services"

@dataclass
class AlertRule:
    rule_id: str
    name: str
    alert_type: AlertType
    conditions: Dict
    actions: List[Dict]
    escalation_rules: List[Dict]
    enabled: bool = True
    priority: int = 1

@dataclass
class NotificationTemplate:
    template_id: str
    name: str
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str]

@dataclass
class AlertNotification:
    notification_id: str
    alert_id: str
    channel: NotificationChannel
    recipient: str
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None

class AlertManager:
    """
    Comprehensive alert management system for SafeGuardian
    """
    
    def __init__(self, db_connection=None, config: Optional[Dict] = None):
        self.db = db_connection
        self.config = config or {}
        
        # Alert storage
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
        
        # Alert rules and templates
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_templates: Dict[str, NotificationTemplate] = {}
        
        # Notification tracking
        self.pending_notifications: asyncio.Queue = asyncio.Queue()
        self.notification_history: List[AlertNotification] = []
        
        # Escalation tracking
        self.escalation_timers: Dict[str, asyncio.Task] = {}
        
        # Statistics
        self.stats = {
            'total_alerts': 0,
            'active_alerts': 0,
            'resolved_alerts': 0,
            'escalated_alerts': 0,
            'notifications_sent': 0,
            'response_times': [],
            'start_time': datetime.now()
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
        
        # Initialize default rules and templates
        self._initialize_default_rules()
        self._initialize_default_templates()
    
    async def start(self):
        """Start the alert management system"""
        if self.is_running:
            logger.warning("Alert manager is already running")
            return
        
        self.is_running = True
        logger.info("Starting SafeGuardian Alert Management System...")
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._notification_processor()),
            asyncio.create_task(self._escalation_monitor()),
            asyncio.create_task(self._alert_cleanup()),
            asyncio.create_task(self._statistics_updater())
        ]
        
        logger.info("Alert Management System started successfully")
    
    async def stop(self):
        """Stop the alert management system"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping Alert Management System...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Cancel escalation timers
        for timer in self.escalation_timers.values():
            timer.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        logger.info("Alert Management System stopped")
    
    async def create_alert(self, alert_data: Dict) -> str:
        """
        Create a new alert
        
        Args:
            alert_data: Alert information including type, severity, details, etc.
            
        Returns:
            Alert ID
        """
        alert_id = str(uuid.uuid4())
        
        # Create alert record
        alert = {
            'alert_id': alert_id,
            'type': alert_data.get('type', AlertType.GROOMING_DETECTION.value),
            'severity': alert_data.get('severity', 'medium'),
            'status': AlertStatus.ACTIVE.value,
            'title': alert_data.get('title', 'SafeGuardian Alert'),
            'message': alert_data.get('message', ''),
            'details': alert_data.get('details', {}),
            'child_id': alert_data.get('child_id'),
            'session_id': alert_data.get('session_id'),
            'platform': alert_data.get('platform'),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': alert_data.get('created_by', 'system'),
            'assigned_to': None,
            'escalation_level': EscalationLevel.GUARDIAN.value,
            'response_required': alert_data.get('response_required', True),
            'auto_escalate': alert_data.get('auto_escalate', True),
            'escalation_timeout': alert_data.get('escalation_timeout', 300),  # 5 minutes
            'metadata': alert_data.get('metadata', {})
        }
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.stats['total_alerts'] += 1
        self.stats['active_alerts'] += 1
        
        # Store in database if available
        if self.db:
            await self._store_alert_in_db(alert)
        
        logger.info(f"Created alert {alert_id}: {alert['title']}")
        
        # Process alert rules
        await self._process_alert_rules(alert)
        
        # Start escalation timer if needed
        if alert['auto_escalate'] and alert['response_required']:
            await self._start_escalation_timer(alert_id)
        
        return alert_id
    
    async def update_alert_status(self, alert_id: str, status: AlertStatus, 
                                user_id: str, notes: Optional[str] = None) -> bool:
        """Update alert status"""
        if alert_id not in self.active_alerts:
            logger.warning(f"Alert {alert_id} not found")
            return False
        
        alert = self.active_alerts[alert_id]
        old_status = alert['status']
        
        alert['status'] = status.value
        alert['updated_at'] = datetime.now()
        alert['updated_by'] = user_id
        
        if notes:
            if 'notes' not in alert:
                alert['notes'] = []
            alert['notes'].append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'note': notes
            })
        
        # Update statistics
        if status == AlertStatus.RESOLVED:
            self.stats['resolved_alerts'] += 1
            self.stats['active_alerts'] -= 1
            
            # Calculate response time
            response_time = (alert['updated_at'] - alert['created_at']).total_seconds()
            self.stats['response_times'].append(response_time)
            
            # Cancel escalation timer
            if alert_id in self.escalation_timers:
                self.escalation_timers[alert_id].cancel()
                del self.escalation_timers[alert_id]
        
        elif status == AlertStatus.ESCALATED:
            self.stats['escalated_alerts'] += 1
        
        logger.info(f"Alert {alert_id} status changed from {old_status} to {status.value}")
        
        # Send status update notifications
        await self._send_status_update_notification(alert, old_status, user_id)
        
        return True
    
    async def escalate_alert(self, alert_id: str, escalation_level: EscalationLevel, 
                           reason: str, user_id: str) -> bool:
        """Escalate an alert to a higher level"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        old_level = alert['escalation_level']
        
        alert['escalation_level'] = escalation_level.value
        alert['status'] = AlertStatus.ESCALATED.value
        alert['updated_at'] = datetime.now()
        
        # Add escalation record
        if 'escalations' not in alert:
            alert['escalations'] = []
        
        alert['escalations'].append({
            'timestamp': datetime.now().isoformat(),
            'from_level': old_level,
            'to_level': escalation_level.value,
            'reason': reason,
            'escalated_by': user_id
        })
        
        logger.warning(f"Alert {alert_id} escalated from {old_level} to {escalation_level.value}: {reason}")
        
        # Send escalation notifications
        await self._send_escalation_notifications(alert, escalation_level, reason)
        
        return True
    
    async def _process_alert_rules(self, alert: Dict):
        """Process alert against configured rules"""
        alert_type = AlertType(alert['type'])
        
        for rule in self.alert_rules.values():
            if not rule.enabled or rule.alert_type != alert_type:
                continue
            
            # Check rule conditions
            if await self._evaluate_rule_conditions(alert, rule.conditions):
                # Execute rule actions
                await self._execute_rule_actions(alert, rule.actions)
    
    async def _evaluate_rule_conditions(self, alert: Dict, conditions: Dict) -> bool:
        """Evaluate if alert meets rule conditions"""
        # Simple condition evaluation (can be extended)
        for key, expected_value in conditions.items():
            if key in alert:
                if isinstance(expected_value, list):
                    if alert[key] not in expected_value:
                        return False
                elif alert[key] != expected_value:
                    return False
            elif key in alert.get('details', {}):
                if alert['details'][key] != expected_value:
                    return False
        
        return True
    
    async def _execute_rule_actions(self, alert: Dict, actions: List[Dict]):
        """Execute actions defined in alert rules"""
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'notify':
                await self._send_notification(
                    alert['alert_id'],
                    action.get('channel', NotificationChannel.EMAIL),
                    action.get('recipients', []),
                    action.get('template')
                )
            
            elif action_type == 'escalate':
                escalation_level = EscalationLevel(action.get('level', EscalationLevel.FAMILY_ADMIN.value))
                await self.escalate_alert(
                    alert['alert_id'],
                    escalation_level,
                    action.get('reason', 'Automatic escalation'),
                    'system'
                )
            
            elif action_type == 'assign':
                alert['assigned_to'] = action.get('user_id')
            
            elif action_type == 'webhook':
                await self._send_webhook(action.get('url'), alert)
    
    async def _send_notification(self, alert_id: str, channel: NotificationChannel, 
                               recipients: List[str], template_id: Optional[str] = None):
        """Send notification for an alert"""
        if alert_id not in self.active_alerts:
            return
        
        alert = self.active_alerts[alert_id]
        
        # Get notification template
        template = None
        if template_id and template_id in self.notification_templates:
            template = self.notification_templates[template_id]
        else:
            # Use default template for channel
            template = self._get_default_template(channel, alert['type'])
        
        if not template:
            logger.error(f"No template found for channel {channel.value}")
            return
        
        # Send to each recipient
        for recipient in recipients:
            notification = AlertNotification(
                notification_id=str(uuid.uuid4()),
                alert_id=alert_id,
                channel=channel,
                recipient=recipient,
                status='pending'
            )
            
            # Queue notification for processing
            await self.pending_notifications.put((notification, template, alert))
    
    async def _notification_processor(self):
        """Background task to process notification queue"""
        while self.is_running:
            try:
                # Get notification from queue
                notification, template, alert = await asyncio.wait_for(
                    self.pending_notifications.get(),
                    timeout=1.0
                )
                
                # Process notification
                success = await self._process_notification(notification, template, alert)
                
                if success:
                    notification.status = 'sent'
                    notification.sent_at = datetime.now()
                    self.stats['notifications_sent'] += 1
                else:
                    notification.status = 'failed'
                
                self.notification_history.append(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing notification: {str(e)}")
    
    async def _process_notification(self, notification: AlertNotification, 
                                  template: NotificationTemplate, alert: Dict) -> bool:
        """Process individual notification"""
        try:
            # Render template
            subject = self._render_template(template.subject_template, alert)
            body = self._render_template(template.body_template, alert)
            
            # Send based on channel
            if notification.channel == NotificationChannel.EMAIL:
                return await self._send_email(notification.recipient, subject, body)
            
            elif notification.channel == NotificationChannel.SMS:
                return await self._send_sms(notification.recipient, body)
            
            elif notification.channel == NotificationChannel.PUSH:
                return await self._send_push_notification(notification.recipient, subject, body)
            
            elif notification.channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(notification.recipient, alert)
            
            else:
                logger.warning(f"Unsupported notification channel: {notification.channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            notification.error_message = str(e)
            return False
    
    async def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Send email notification"""
        try:
            # Email configuration from config
            smtp_config = self.config.get('email', {})
            
            if not smtp_config:
                logger.warning("Email configuration not found")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config.get('from_address', 'alerts@safeguardian.com')
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email (placeholder - implement actual SMTP)
            logger.info(f"EMAIL SENT to {recipient}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def _send_sms(self, recipient: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            # SMS configuration from config
            sms_config = self.config.get('sms', {})
            
            if not sms_config:
                logger.warning("SMS configuration not found")
                return False
            
            # Send SMS (placeholder - implement actual SMS service)
            logger.info(f"SMS SENT to {recipient}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    async def _send_push_notification(self, recipient: str, title: str, body: str) -> bool:
        """Send push notification"""
        try:
            # Push notification logic (placeholder)
            logger.info(f"PUSH NOTIFICATION SENT to {recipient}: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    async def _send_webhook(self, url: str, alert: Dict) -> bool:
        """Send webhook notification"""
        try:
            # Prepare webhook payload
            payload = {
                'alert_id': alert['alert_id'],
                'type': alert['type'],
                'severity': alert['severity'],
                'title': alert['title'],
                'message': alert['message'],
                'timestamp': alert['created_at'].isoformat(),
                'details': alert['details']
            }
            
            # Send webhook (placeholder - implement actual HTTP request)
            logger.info(f"WEBHOOK SENT to {url}: {alert['alert_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending webhook: {str(e)}")
            return False
    
    def _render_template(self, template: str, alert: Dict) -> str:
        """Render notification template with alert data"""
        # Simple template rendering (can be enhanced with proper template engine)
        rendered = template
        
        # Replace common variables
        variables = {
            '{alert_id}': alert['alert_id'],
            '{title}': alert['title'],
            '{message}': alert['message'],
            '{severity}': alert['severity'],
            '{platform}': alert.get('platform', 'Unknown'),
            '{child_id}': alert.get('child_id', 'Unknown'),
            '{timestamp}': alert['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            '{details}': json.dumps(alert['details'], indent=2)
        }
        
        for var, value in variables.items():
            rendered = rendered.replace(var, str(value))
        
        return rendered
    
    async def _start_escalation_timer(self, alert_id: str):
        """Start escalation timer for an alert"""
        if alert_id not in self.active_alerts:
            return
        
        alert = self.active_alerts[alert_id]
        timeout = alert.get('escalation_timeout', 300)  # Default 5 minutes
        
        async def escalation_callback():
            await asyncio.sleep(timeout)
            
            # Check if alert is still active and unacknowledged
            if (alert_id in self.active_alerts and 
                self.active_alerts[alert_id]['status'] == AlertStatus.ACTIVE.value):
                
                await self.escalate_alert(
                    alert_id,
                    EscalationLevel.FAMILY_ADMIN,
                    "Automatic escalation due to timeout",
                    "system"
                )
        
        # Create and store escalation task
        task = asyncio.create_task(escalation_callback())
        self.escalation_timers[alert_id] = task
    
    async def _escalation_monitor(self):
        """Background task to monitor escalations"""
        while self.is_running:
            try:
                # Clean up completed escalation timers
                completed_timers = [
                    alert_id for alert_id, task in self.escalation_timers.items()
                    if task.done()
                ]
                
                for alert_id in completed_timers:
                    del self.escalation_timers[alert_id]
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in escalation monitor: {str(e)}")
    
    async def _alert_cleanup(self):
        """Background task to clean up old alerts"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Move resolved alerts older than 24 hours to history
                resolved_alerts = [
                    alert_id for alert_id, alert in self.active_alerts.items()
                    if (alert['status'] == AlertStatus.RESOLVED.value and
                        current_time - alert['updated_at'] > timedelta(hours=24))
                ]
                
                for alert_id in resolved_alerts:
                    alert = self.active_alerts.pop(alert_id)
                    self.alert_history.append(alert)
                
                # Clean up old notification history
                cutoff_time = current_time - timedelta(days=7)
                self.notification_history = [
                    n for n in self.notification_history
                    if n.sent_at and n.sent_at > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in alert cleanup: {str(e)}")
    
    async def _statistics_updater(self):
        """Background task to update statistics"""
        while self.is_running:
            try:
                # Update active alert count
                self.stats['active_alerts'] = len([
                    a for a in self.active_alerts.values()
                    if a['status'] == AlertStatus.ACTIVE.value
                ])
                
                # Calculate average response time
                if self.stats['response_times']:
                    self.stats['avg_response_time'] = sum(self.stats['response_times']) / len(self.stats['response_times'])
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error updating statistics: {str(e)}")
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        # Critical grooming detection rule
        self.alert_rules['critical_grooming'] = AlertRule(
            rule_id='critical_grooming',
            name='Critical Grooming Detection',
            alert_type=AlertType.GROOMING_DETECTION,
            conditions={'severity': ['critical', 'emergency']},
            actions=[
                {'type': 'notify', 'channel': NotificationChannel.EMAIL, 'template': 'critical_alert'},
                {'type': 'notify', 'channel': NotificationChannel.SMS, 'template': 'critical_sms'},
                {'type': 'escalate', 'level': EscalationLevel.LAW_ENFORCEMENT.value, 'reason': 'Critical threat detected'}
            ],
            escalation_rules=[],
            priority=1
        )
        
        # High risk detection rule
        self.alert_rules['high_risk'] = AlertRule(
            rule_id='high_risk',
            name='High Risk Detection',
            alert_type=AlertType.GROOMING_DETECTION,
            conditions={'severity': ['high']},
            actions=[
                {'type': 'notify', 'channel': NotificationChannel.EMAIL, 'template': 'high_risk_alert'},
                {'type': 'notify', 'channel': NotificationChannel.PUSH, 'template': 'high_risk_push'}
            ],
            escalation_rules=[],
            priority=2
        )
    
    def _initialize_default_templates(self):
        """Initialize default notification templates"""
        # Critical alert email template
        self.notification_templates['critical_alert'] = NotificationTemplate(
            template_id='critical_alert',
            name='Critical Alert Email',
            channel=NotificationChannel.EMAIL,
            subject_template='🚨 CRITICAL SAFEGUARDIAN ALERT - Immediate Action Required',
            body_template='''
            <html>
            <body>
                <h2 style="color: #d32f2f;">🚨 CRITICAL SAFEGUARDIAN ALERT</h2>
                <p><strong>Alert ID:</strong> {alert_id}</p>
                <p><strong>Severity:</strong> {severity}</p>
                <p><strong>Platform:</strong> {platform}</p>
                <p><strong>Time:</strong> {timestamp}</p>
                
                <h3>Alert Details:</h3>
                <p>{message}</p>
                
                <div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #d32f2f;">
                    <h4>IMMEDIATE ACTION REQUIRED</h4>
                    <p>This alert indicates a potential serious threat to your child's safety. Please:</p>
                    <ul>
                        <li>Check on your child immediately</li>
                        <li>Review the conversation details in your SafeGuardian dashboard</li>
                        <li>Consider contacting law enforcement if necessary</li>
                    </ul>
                </div>
                
                <p><a href="https://dashboard.safeguardian.com/alerts/{alert_id}" style="background-color: #d32f2f; color: white; padding: 10px 20px; text-decoration: none;">View Alert Details</a></p>
            </body>
            </html>
            ''',
            variables=['alert_id', 'severity', 'platform', 'timestamp', 'message']
        )
        
        # Critical SMS template
        self.notification_templates['critical_sms'] = NotificationTemplate(
            template_id='critical_sms',
            name='Critical Alert SMS',
            channel=NotificationChannel.SMS,
            subject_template='',
            body_template='🚨 SAFEGUARDIAN CRITICAL ALERT: Potential threat detected for your child on {platform}. Check dashboard immediately: https://dashboard.safeguardian.com/alerts/{alert_id}',
            variables=['platform', 'alert_id']
        )
    
    def _get_default_template(self, channel: NotificationChannel, alert_type: str) -> Optional[NotificationTemplate]:
        """Get default template for channel and alert type"""
        # Return appropriate default template
        if channel == NotificationChannel.EMAIL:
            return self.notification_templates.get('critical_alert')
        elif channel == NotificationChannel.SMS:
            return self.notification_templates.get('critical_sms')
        
        return None
    
    # Database operations (placeholders)
    async def _store_alert_in_db(self, alert: Dict):
        """Store alert in database"""
        # Implement database storage
        pass
    
    async def _send_status_update_notification(self, alert: Dict, old_status: str, user_id: str):
        """Send notification about status update"""
        # Implement status update notifications
        pass
    
    async def _send_escalation_notifications(self, alert: Dict, escalation_level: EscalationLevel, reason: str):
        """Send notifications for alert escalation"""
        # Implement escalation notifications
        pass
    
    # Public API methods
    def get_alert(self, alert_id: str) -> Optional[Dict]:
        """Get alert by ID"""
        return self.active_alerts.get(alert_id)
    
    def get_active_alerts(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get active alerts with optional filters"""
        alerts = list(self.active_alerts.values())
        
        if filters:
            # Apply filters
            if 'severity' in filters:
                alerts = [a for a in alerts if a['severity'] == filters['severity']]
            if 'type' in filters:
                alerts = [a for a in alerts if a['type'] == filters['type']]
            if 'child_id' in filters:
                alerts = [a for a in alerts if a['child_id'] == filters['child_id']]
        
        return alerts
    
    def get_statistics(self) -> Dict:
        """Get alert management statistics"""
        return self.stats.copy()

# Factory function
def create_alert_manager(db_connection=None, config: Optional[Dict] = None) -> AlertManager:
    """Create a new alert manager instance"""
    return AlertManager(db_connection, config)

# Example usage
if __name__ == "__main__":
    async def test_alert_manager():
        manager = create_alert_manager()
        
        # Start alert manager
        await manager.start()
        
        # Create test alert
        alert_data = {
            'type': AlertType.GROOMING_DETECTION.value,
            'severity': 'critical',
            'title': 'Potential Grooming Detected',
            'message': 'High-risk communication patterns detected',
            'child_id': 'child_123',
            'platform': 'instagram',
            'details': {
                'risk_level': 'critical',
                'confidence': 0.95,
                'patterns': ['sexual_content', 'meeting_request']
            }
        }
        
        alert_id = await manager.create_alert(alert_data)
        print(f"Created alert: {alert_id}")
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get statistics
        stats = manager.get_statistics()
        print(f"Alert Statistics: {json.dumps(stats, indent=2, default=str)}")
        
        # Stop alert manager
        await manager.stop()
    
    # Run test
    asyncio.run(test_alert_manager())

