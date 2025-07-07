"""
SafeGuardian WebSocket Manager
Real-time communication system for live updates and monitoring
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import weakref
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    # Authentication
    AUTH_REQUEST = "auth_request"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILED = "auth_failed"
    
    # Monitoring
    SESSION_UPDATE = "session_update"
    MESSAGE_UPDATE = "message_update"
    MONITORING_STATUS = "monitoring_status"
    
    # Alerts
    ALERT_CREATED = "alert_created"
    ALERT_UPDATED = "alert_updated"
    ALERT_ACKNOWLEDGED = "alert_acknowledged"
    
    # Dashboard
    DASHBOARD_UPDATE = "dashboard_update"
    STATISTICS_UPDATE = "statistics_update"
    
    # System
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    DISCONNECT = "disconnect"

class ClientType(Enum):
    MOBILE_APP = "mobile_app"
    DASHBOARD = "dashboard"
    ADMIN_PANEL = "admin_panel"

@dataclass
class WebSocketClient:
    client_id: str
    websocket: object  # WebSocket connection object
    user_id: str
    client_type: ClientType
    authenticated: bool = False
    connected_at: datetime = None
    last_heartbeat: datetime = None
    subscriptions: Set[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.connected_at is None:
            self.connected_at = datetime.now()
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()
        if self.subscriptions is None:
            self.subscriptions = set()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class WebSocketMessage:
    message_id: str
    type: MessageType
    data: Dict
    timestamp: datetime
    sender_id: Optional[str] = None
    target_clients: Optional[List[str]] = None
    broadcast: bool = False

class WebSocketManager:
    """
    WebSocket manager for real-time communication in SafeGuardian
    """
    
    def __init__(self, auth_service=None):
        self.auth_service = auth_service
        
        # Client management
        self.clients: Dict[str, WebSocketClient] = {}
        self.user_clients: Dict[str, Set[str]] = defaultdict(set)  # user_id -> client_ids
        
        # Subscription management
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # topic -> client_ids
        
        # Message queues
        self.message_queue = asyncio.Queue()
        self.broadcast_queue = asyncio.Queue()
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'authentication_attempts': 0,
            'failed_authentications': 0,
            'start_time': datetime.now()
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
    
    async def start(self):
        """Start the WebSocket manager"""
        if self.is_running:
            logger.warning("WebSocket manager is already running")
            return
        
        self.is_running = True
        logger.info("Starting SafeGuardian WebSocket Manager...")
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._message_processor()),
            asyncio.create_task(self._broadcast_processor()),
            asyncio.create_task(self._heartbeat_monitor()),
            asyncio.create_task(self._statistics_updater())
        ]
        
        logger.info("WebSocket Manager started successfully")
    
    async def stop(self):
        """Stop the WebSocket manager"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping WebSocket Manager...")
        
        # Disconnect all clients
        for client in list(self.clients.values()):
            await self.disconnect_client(client.client_id, "Server shutdown")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        logger.info("WebSocket Manager stopped")
    
    async def connect_client(self, websocket, client_type: ClientType, 
                           metadata: Optional[Dict] = None) -> str:
        """
        Handle new WebSocket client connection
        
        Args:
            websocket: WebSocket connection object
            client_type: Type of client connecting
            metadata: Additional client metadata
            
        Returns:
            Client ID
        """
        client_id = str(uuid.uuid4())
        
        client = WebSocketClient(
            client_id=client_id,
            websocket=websocket,
            user_id="",  # Will be set during authentication
            client_type=client_type,
            metadata=metadata or {}
        )
        
        self.clients[client_id] = client
        self.stats['total_connections'] += 1
        self.stats['active_connections'] += 1
        
        logger.info(f"New WebSocket client connected: {client_id} ({client_type.value})")
        
        # Send connection acknowledgment
        await self._send_to_client(client_id, MessageType.AUTH_REQUEST, {
            'client_id': client_id,
            'message': 'Please authenticate to continue',
            'required_fields': ['token', 'user_id']
        })
        
        return client_id
    
    async def disconnect_client(self, client_id: str, reason: str = "Client disconnect"):
        """Disconnect a WebSocket client"""
        if client_id not in self.clients:
            return
        
        client = self.clients[client_id]
        
        # Remove from user mapping
        if client.user_id:
            self.user_clients[client.user_id].discard(client_id)
            if not self.user_clients[client.user_id]:
                del self.user_clients[client.user_id]
        
        # Remove from subscriptions
        for topic in client.subscriptions:
            self.subscriptions[topic].discard(client_id)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
        
        # Close WebSocket connection
        try:
            await client.websocket.close()
        except:
            pass
        
        # Remove client
        del self.clients[client_id]
        self.stats['active_connections'] -= 1
        
        logger.info(f"Client {client_id} disconnected: {reason}")
    
    async def authenticate_client(self, client_id: str, auth_data: Dict) -> bool:
        """
        Authenticate a WebSocket client
        
        Args:
            client_id: Client identifier
            auth_data: Authentication data (token, user_id, etc.)
            
        Returns:
            True if authentication successful
        """
        if client_id not in self.clients:
            return False
        
        client = self.clients[client_id]
        self.stats['authentication_attempts'] += 1
        
        # Validate authentication
        token = auth_data.get('token')
        user_id = auth_data.get('user_id')
        
        if not token or not user_id:
            await self._send_to_client(client_id, MessageType.AUTH_FAILED, {
                'error': 'Missing token or user_id'
            })
            self.stats['failed_authentications'] += 1
            return False
        
        # Authenticate with auth service
        if self.auth_service:
            is_valid = await self.auth_service.validate_token(token, user_id)
            if not is_valid:
                await self._send_to_client(client_id, MessageType.AUTH_FAILED, {
                    'error': 'Invalid token'
                })
                self.stats['failed_authentications'] += 1
                return False
        
        # Set client as authenticated
        client.authenticated = True
        client.user_id = user_id
        
        # Add to user mapping
        self.user_clients[user_id].add(client_id)
        
        # Send authentication success
        await self._send_to_client(client_id, MessageType.AUTH_SUCCESS, {
            'user_id': user_id,
            'client_id': client_id,
            'message': 'Authentication successful'
        })
        
        logger.info(f"Client {client_id} authenticated as user {user_id}")
        
        # Auto-subscribe to user-specific topics
        await self.subscribe_client(client_id, f"user:{user_id}")
        
        # Subscribe to client-type specific topics
        if client.client_type == ClientType.DASHBOARD:
            await self.subscribe_client(client_id, "dashboard:updates")
            await self.subscribe_client(client_id, "alerts:all")
        elif client.client_type == ClientType.MOBILE_APP:
            await self.subscribe_client(client_id, "mobile:updates")
        
        return True
    
    async def subscribe_client(self, client_id: str, topic: str) -> bool:
        """Subscribe client to a topic"""
        if client_id not in self.clients:
            return False
        
        client = self.clients[client_id]
        
        if not client.authenticated:
            await self._send_to_client(client_id, MessageType.ERROR, {
                'error': 'Authentication required for subscriptions'
            })
            return False
        
        client.subscriptions.add(topic)
        self.subscriptions[topic].add(client_id)
        
        logger.debug(f"Client {client_id} subscribed to topic: {topic}")
        return True
    
    async def unsubscribe_client(self, client_id: str, topic: str) -> bool:
        """Unsubscribe client from a topic"""
        if client_id not in self.clients:
            return False
        
        client = self.clients[client_id]
        client.subscriptions.discard(topic)
        self.subscriptions[topic].discard(client_id)
        
        if not self.subscriptions[topic]:
            del self.subscriptions[topic]
        
        logger.debug(f"Client {client_id} unsubscribed from topic: {topic}")
        return True
    
    async def send_message(self, message: WebSocketMessage):
        """Queue message for sending"""
        await self.message_queue.put(message)
    
    async def broadcast_message(self, message_type: MessageType, data: Dict, 
                              topic: Optional[str] = None):
        """Broadcast message to all clients or topic subscribers"""
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            type=message_type,
            data=data,
            timestamp=datetime.now(),
            broadcast=True
        )
        
        if topic:
            message.target_clients = list(self.subscriptions.get(topic, []))
        
        await self.broadcast_queue.put(message)
    
    async def send_to_user(self, user_id: str, message_type: MessageType, data: Dict):
        """Send message to all clients of a specific user"""
        client_ids = list(self.user_clients.get(user_id, []))
        
        if client_ids:
            message = WebSocketMessage(
                message_id=str(uuid.uuid4()),
                type=message_type,
                data=data,
                timestamp=datetime.now(),
                target_clients=client_ids
            )
            
            await self.message_queue.put(message)
    
    async def send_alert_notification(self, alert_data: Dict):
        """Send alert notification to relevant clients"""
        child_id = alert_data.get('child_id')
        severity = alert_data.get('severity', 'medium')
        
        # Send to dashboard clients
        await self.broadcast_message(
            MessageType.ALERT_CREATED,
            alert_data,
            topic="alerts:all"
        )
        
        # Send to specific user if child_id is available
        if child_id:
            # Get guardian user ID for the child (placeholder logic)
            guardian_user_id = await self._get_guardian_for_child(child_id)
            if guardian_user_id:
                await self.send_to_user(guardian_user_id, MessageType.ALERT_CREATED, alert_data)
        
        # Send to mobile apps for high severity alerts
        if severity in ['high', 'critical', 'emergency']:
            await self.broadcast_message(
                MessageType.ALERT_CREATED,
                alert_data,
                topic="mobile:updates"
            )
    
    async def send_monitoring_update(self, session_data: Dict):
        """Send monitoring session update"""
        child_id = session_data.get('child_id')
        
        # Send to dashboard
        await self.broadcast_message(
            MessageType.SESSION_UPDATE,
            session_data,
            topic="dashboard:updates"
        )
        
        # Send to specific guardian
        if child_id:
            guardian_user_id = await self._get_guardian_for_child(child_id)
            if guardian_user_id:
                await self.send_to_user(guardian_user_id, MessageType.SESSION_UPDATE, session_data)
    
    async def send_statistics_update(self, stats_data: Dict):
        """Send statistics update to dashboard clients"""
        await self.broadcast_message(
            MessageType.STATISTICS_UPDATE,
            stats_data,
            topic="dashboard:updates"
        )
    
    async def _message_processor(self):
        """Background task to process message queue"""
        while self.is_running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                await self._process_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
    
    async def _broadcast_processor(self):
        """Background task to process broadcast queue"""
        while self.is_running:
            try:
                message = await asyncio.wait_for(
                    self.broadcast_queue.get(),
                    timeout=1.0
                )
                
                await self._process_broadcast(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing broadcast: {str(e)}")
    
    async def _process_message(self, message: WebSocketMessage):
        """Process individual message"""
        if message.target_clients:
            # Send to specific clients
            for client_id in message.target_clients:
                await self._send_to_client(client_id, message.type, message.data)
        else:
            # Send to all authenticated clients
            for client in self.clients.values():
                if client.authenticated:
                    await self._send_to_client(client.client_id, message.type, message.data)
    
    async def _process_broadcast(self, message: WebSocketMessage):
        """Process broadcast message"""
        if message.target_clients:
            # Send to specific clients
            for client_id in message.target_clients:
                await self._send_to_client(client_id, message.type, message.data)
        else:
            # Send to all authenticated clients
            for client in self.clients.values():
                if client.authenticated:
                    await self._send_to_client(client.client_id, message.type, message.data)
    
    async def _send_to_client(self, client_id: str, message_type: MessageType, data: Dict):
        """Send message to specific client"""
        if client_id not in self.clients:
            return
        
        client = self.clients[client_id]
        
        try:
            message = {
                'type': message_type.value,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'message_id': str(uuid.uuid4())
            }
            
            await client.websocket.send(json.dumps(message))
            self.stats['messages_sent'] += 1
            
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {str(e)}")
            # Disconnect client on send error
            await self.disconnect_client(client_id, "Send error")
    
    async def _heartbeat_monitor(self):
        """Background task to monitor client heartbeats"""
        while self.is_running:
            try:
                current_time = datetime.now()
                disconnected_clients = []
                
                for client_id, client in self.clients.items():
                    # Check for clients that haven't sent heartbeat in 60 seconds
                    if current_time - client.last_heartbeat > timedelta(seconds=60):
                        disconnected_clients.append(client_id)
                
                # Disconnect inactive clients
                for client_id in disconnected_clients:
                    await self.disconnect_client(client_id, "Heartbeat timeout")
                
                # Send heartbeat to all clients
                for client in self.clients.values():
                    if client.authenticated:
                        await self._send_to_client(client.client_id, MessageType.HEARTBEAT, {
                            'timestamp': current_time.isoformat()
                        })
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {str(e)}")
    
    async def _statistics_updater(self):
        """Background task to update and broadcast statistics"""
        while self.is_running:
            try:
                # Update statistics
                self.stats['active_connections'] = len(self.clients)
                
                # Broadcast statistics to dashboard clients
                await self.send_statistics_update(self.stats)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error updating statistics: {str(e)}")
    
    async def handle_client_message(self, client_id: str, message_data: Dict):
        """Handle incoming message from client"""
        if client_id not in self.clients:
            return
        
        client = self.clients[client_id]
        self.stats['messages_received'] += 1
        
        message_type = message_data.get('type')
        data = message_data.get('data', {})
        
        # Update heartbeat
        client.last_heartbeat = datetime.now()
        
        # Handle different message types
        if message_type == MessageType.AUTH_REQUEST.value:
            await self.authenticate_client(client_id, data)
        
        elif message_type == MessageType.HEARTBEAT.value:
            # Heartbeat received, no action needed
            pass
        
        elif message_type == "subscribe":
            topic = data.get('topic')
            if topic:
                await self.subscribe_client(client_id, topic)
        
        elif message_type == "unsubscribe":
            topic = data.get('topic')
            if topic:
                await self.unsubscribe_client(client_id, topic)
        
        else:
            logger.warning(f"Unknown message type from client {client_id}: {message_type}")
    
    # Helper methods
    async def _get_guardian_for_child(self, child_id: str) -> Optional[str]:
        """Get guardian user ID for a child (placeholder)"""
        # Implement actual database lookup
        return None
    
    # Public API methods
    def get_client_info(self, client_id: str) -> Optional[Dict]:
        """Get client information"""
        if client_id not in self.clients:
            return None
        
        client = self.clients[client_id]
        return {
            'client_id': client.client_id,
            'user_id': client.user_id,
            'client_type': client.client_type.value,
            'authenticated': client.authenticated,
            'connected_at': client.connected_at.isoformat(),
            'last_heartbeat': client.last_heartbeat.isoformat(),
            'subscriptions': list(client.subscriptions),
            'metadata': client.metadata
        }
    
    def get_connected_clients(self) -> List[Dict]:
        """Get all connected clients"""
        return [self.get_client_info(client_id) for client_id in self.clients.keys()]
    
    def get_statistics(self) -> Dict:
        """Get WebSocket manager statistics"""
        return self.stats.copy()
    
    def get_subscription_info(self) -> Dict:
        """Get subscription information"""
        return {
            topic: len(clients) for topic, clients in self.subscriptions.items()
        }

# Factory function
def create_websocket_manager(auth_service=None) -> WebSocketManager:
    """Create a new WebSocket manager instance"""
    return WebSocketManager(auth_service)

# Example usage
if __name__ == "__main__":
    async def test_websocket_manager():
        manager = create_websocket_manager()
        
        # Start manager
        await manager.start()
        
        # Simulate client connection (placeholder)
        print("WebSocket Manager started and ready for connections")
        
        # Wait a bit
        await asyncio.sleep(5)
        
        # Get statistics
        stats = manager.get_statistics()
        print(f"WebSocket Statistics: {json.dumps(stats, indent=2, default=str)}")
        
        # Stop manager
        await manager.stop()
    
    # Run test
    asyncio.run(test_websocket_manager())

