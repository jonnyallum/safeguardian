"""
SafeGuardian AI Analysis Service
Integrates AI grooming detection with the SafeGuardian backend system
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
import hashlib
import uuid

from .grooming_detector import GroomingDetector, RiskLevel, GroomingPattern, DetectionResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service class that provides AI analysis capabilities for the SafeGuardian system
    """
    
    def __init__(self, db_connection=None):
        self.detector = GroomingDetector()
        self.db = db_connection
        self.analysis_cache = {}
        self.active_sessions = {}
        
    async def analyze_message_async(self, message_data: Dict) -> Dict:
        """
        Asynchronously analyze a message for grooming indicators
        
        Args:
            message_data: Dictionary containing message information
            
        Returns:
            Analysis result dictionary
        """
        try:
            # Extract message information
            message_text = message_data.get('content', '')
            sender_id = message_data.get('sender_id')
            recipient_id = message_data.get('recipient_id')
            session_id = message_data.get('session_id')
            platform = message_data.get('platform', 'unknown')
            timestamp = message_data.get('timestamp', datetime.now().isoformat())
            
            # Get user ages if available
            sender_age = await self._get_user_age(sender_id) if sender_id else None
            recipient_age = await self._get_user_age(recipient_id) if recipient_id else None
            
            # Perform AI analysis
            result = self.detector.analyze_message(
                message=message_text,
                sender_age=sender_age,
                recipient_age=recipient_age,
                conversation_id=session_id
            )
            
            # Create analysis record
            analysis_record = {
                'id': str(uuid.uuid4()),
                'message_id': message_data.get('id'),
                'session_id': session_id,
                'platform': platform,
                'risk_level': result.risk_level.value,
                'confidence': result.confidence,
                'patterns_detected': [p.value for p in result.patterns_detected],
                'risk_factors': result.risk_factors,
                'explanation': result.explanation,
                'recommendations': result.recommendations,
                'timestamp': timestamp,
                'message_hash': result.message_hash,
                'sender_age': sender_age,
                'recipient_age': recipient_age
            }
            
            # Store analysis in database
            if self.db:
                await self._store_analysis(analysis_record)
            
            # Check if alert should be triggered
            if result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._trigger_alert(analysis_record, message_data)
            
            # Update session context
            await self._update_session_context(session_id, result)
            
            return analysis_record
            
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
            return {
                'error': str(e),
                'risk_level': 'unknown',
                'confidence': 0.0
            }
    
    async def analyze_conversation_thread_async(self, session_id: str, 
                                              limit: int = 50) -> Dict:
        """
        Analyze an entire conversation thread for grooming patterns
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of messages to analyze
            
        Returns:
            Thread analysis results
        """
        try:
            # Retrieve conversation messages
            messages = await self._get_session_messages(session_id, limit)
            
            if not messages:
                return {
                    'error': 'No messages found for session',
                    'session_id': session_id
                }
            
            # Perform thread analysis
            thread_analysis = self.detector.analyze_conversation_thread(messages)
            
            # Create thread analysis record
            thread_record = {
                'id': str(uuid.uuid4()),
                'session_id': session_id,
                'message_count': len(messages),
                'overall_risk': thread_analysis['overall_risk'].value,
                'confidence': thread_analysis['confidence'],
                'escalation_detected': thread_analysis['escalation_detected'],
                'unique_patterns': len(set([
                    p for analysis in thread_analysis['message_analyses'] 
                    for p in analysis['result'].patterns_detected
                ])),
                'recommendations': thread_analysis['recommendations'],
                'summary': thread_analysis['summary'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Store thread analysis
            if self.db:
                await self._store_thread_analysis(thread_record)
            
            # Trigger alerts for high-risk threads
            if thread_analysis['overall_risk'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._trigger_thread_alert(thread_record)
            
            return thread_record
            
        except Exception as e:
            logger.error(f"Error analyzing conversation thread: {str(e)}")
            return {
                'error': str(e),
                'session_id': session_id
            }
    
    async def get_risk_assessment(self, child_id: str, 
                                time_range: timedelta = timedelta(days=7)) -> Dict:
        """
        Get comprehensive risk assessment for a child
        
        Args:
            child_id: Child's unique identifier
            time_range: Time range for analysis
            
        Returns:
            Risk assessment summary
        """
        try:
            # Get recent analyses for the child
            analyses = await self._get_child_analyses(child_id, time_range)
            
            if not analyses:
                return {
                    'child_id': child_id,
                    'overall_risk': 'low',
                    'confidence': 0.0,
                    'total_messages': 0,
                    'alerts_triggered': 0
                }
            
            # Calculate overall risk metrics
            total_messages = len(analyses)
            high_risk_count = len([a for a in analyses if a['risk_level'] in ['high', 'critical']])
            medium_risk_count = len([a for a in analyses if a['risk_level'] == 'medium'])
            alerts_triggered = len([a for a in analyses if a['risk_level'] in ['high', 'critical']])
            
            # Calculate overall risk level
            risk_ratio = (high_risk_count * 2 + medium_risk_count) / total_messages
            
            if risk_ratio >= 0.3 or high_risk_count >= 3:
                overall_risk = 'critical'
                confidence = 0.9
            elif risk_ratio >= 0.2 or high_risk_count >= 1:
                overall_risk = 'high'
                confidence = 0.8
            elif risk_ratio >= 0.1 or medium_risk_count >= 3:
                overall_risk = 'medium'
                confidence = 0.6
            else:
                overall_risk = 'low'
                confidence = 0.4
            
            # Get pattern frequency
            all_patterns = []
            for analysis in analyses:
                all_patterns.extend(analysis.get('patterns_detected', []))
            
            pattern_frequency = {}
            for pattern in all_patterns:
                pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
            
            # Get platform breakdown
            platform_breakdown = {}
            for analysis in analyses:
                platform = analysis.get('platform', 'unknown')
                platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1
            
            return {
                'child_id': child_id,
                'assessment_period': time_range.days,
                'overall_risk': overall_risk,
                'confidence': confidence,
                'total_messages': total_messages,
                'high_risk_messages': high_risk_count,
                'medium_risk_messages': medium_risk_count,
                'alerts_triggered': alerts_triggered,
                'pattern_frequency': pattern_frequency,
                'platform_breakdown': platform_breakdown,
                'risk_trend': await self._calculate_risk_trend(child_id, time_range),
                'recommendations': await self._generate_child_recommendations(
                    overall_risk, pattern_frequency, risk_ratio
                ),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating risk assessment: {str(e)}")
            return {
                'error': str(e),
                'child_id': child_id
            }
    
    async def get_platform_analytics(self, platform: str, 
                                   time_range: timedelta = timedelta(days=30)) -> Dict:
        """
        Get analytics for a specific platform
        
        Args:
            platform: Platform name (e.g., 'instagram', 'facebook')
            time_range: Time range for analysis
            
        Returns:
            Platform analytics
        """
        try:
            # Get platform analyses
            analyses = await self._get_platform_analyses(platform, time_range)
            
            if not analyses:
                return {
                    'platform': platform,
                    'total_messages': 0,
                    'risk_distribution': {},
                    'common_patterns': []
                }
            
            # Calculate risk distribution
            risk_distribution = {
                'low': 0,
                'medium': 0,
                'high': 0,
                'critical': 0
            }
            
            for analysis in analyses:
                risk_level = analysis.get('risk_level', 'low')
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # Get common patterns
            all_patterns = []
            for analysis in analyses:
                all_patterns.extend(analysis.get('patterns_detected', []))
            
            pattern_frequency = {}
            for pattern in all_patterns:
                pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
            
            # Sort patterns by frequency
            common_patterns = sorted(
                pattern_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            # Calculate daily trends
            daily_trends = await self._calculate_daily_trends(platform, time_range)
            
            return {
                'platform': platform,
                'analysis_period': time_range.days,
                'total_messages': len(analyses),
                'risk_distribution': risk_distribution,
                'common_patterns': common_patterns,
                'daily_trends': daily_trends,
                'risk_percentage': (
                    (risk_distribution['high'] + risk_distribution['critical']) / 
                    len(analyses) * 100
                ) if analyses else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating platform analytics: {str(e)}")
            return {
                'error': str(e),
                'platform': platform
            }
    
    # Helper methods for database operations
    async def _get_user_age(self, user_id: str) -> Optional[int]:
        """Get user age from database"""
        # Placeholder - implement database query
        # This would query the child_profiles or users table
        return None
    
    async def _store_analysis(self, analysis_record: Dict):
        """Store analysis result in database"""
        # Placeholder - implement database storage
        # This would insert into ai_analyses table
        logger.info(f"Storing analysis: {analysis_record['id']}")
    
    async def _store_thread_analysis(self, thread_record: Dict):
        """Store thread analysis in database"""
        # Placeholder - implement database storage
        logger.info(f"Storing thread analysis: {thread_record['id']}")
    
    async def _trigger_alert(self, analysis_record: Dict, message_data: Dict):
        """Trigger alert for high-risk message"""
        alert_data = {
            'id': str(uuid.uuid4()),
            'type': 'grooming_detection',
            'severity': analysis_record['risk_level'],
            'child_id': message_data.get('recipient_id'),
            'session_id': analysis_record['session_id'],
            'platform': analysis_record['platform'],
            'description': analysis_record['explanation'],
            'recommendations': analysis_record['recommendations'],
            'evidence_id': analysis_record['id'],
            'timestamp': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Store alert and notify guardians
        logger.warning(f"HIGH RISK ALERT: {alert_data['description']}")
        # Implement alert storage and notification logic
    
    async def _trigger_thread_alert(self, thread_record: Dict):
        """Trigger alert for high-risk conversation thread"""
        logger.warning(f"THREAD ALERT: {thread_record['summary']}")
        # Implement thread alert logic
    
    async def _update_session_context(self, session_id: str, result: DetectionResult):
        """Update session context with latest analysis"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                'message_count': 0,
                'risk_history': [],
                'patterns_detected': set()
            }
        
        session = self.active_sessions[session_id]
        session['message_count'] += 1
        session['risk_history'].append(result.risk_level)
        session['patterns_detected'].update(result.patterns_detected)
    
    async def _get_session_messages(self, session_id: str, limit: int) -> List[Dict]:
        """Get messages for a session"""
        # Placeholder - implement database query
        # This would query the messages table
        return []
    
    async def _get_child_analyses(self, child_id: str, time_range: timedelta) -> List[Dict]:
        """Get analyses for a child within time range"""
        # Placeholder - implement database query
        return []
    
    async def _get_platform_analyses(self, platform: str, time_range: timedelta) -> List[Dict]:
        """Get analyses for a platform within time range"""
        # Placeholder - implement database query
        return []
    
    async def _calculate_risk_trend(self, child_id: str, time_range: timedelta) -> str:
        """Calculate risk trend for a child"""
        # Placeholder - implement trend calculation
        return "stable"
    
    async def _calculate_daily_trends(self, platform: str, time_range: timedelta) -> List[Dict]:
        """Calculate daily risk trends for a platform"""
        # Placeholder - implement daily trend calculation
        return []
    
    async def _generate_child_recommendations(self, overall_risk: str, 
                                            pattern_frequency: Dict, 
                                            risk_ratio: float) -> List[str]:
        """Generate recommendations for child protection"""
        recommendations = []
        
        if overall_risk in ['high', 'critical']:
            recommendations.extend([
                "Immediate guardian notification required",
                "Consider restricting platform access",
                "Schedule safety discussion with child",
                "Review and update privacy settings"
            ])
        
        # Pattern-specific recommendations
        if 'meeting_request' in pattern_frequency:
            recommendations.append("Meeting requests detected - ensure child safety protocols")
        
        if 'sexual_content' in pattern_frequency:
            recommendations.append("Sexual content detected - consider professional counseling")
        
        if risk_ratio > 0.2:
            recommendations.append("High risk ratio - increase monitoring frequency")
        
        return recommendations

# Utility functions for integration
def create_analysis_service(db_connection=None) -> AnalysisService:
    """Factory function to create analysis service"""
    return AnalysisService(db_connection)

async def quick_message_analysis(message_text: str, 
                               sender_age: Optional[int] = None,
                               recipient_age: Optional[int] = None) -> Dict:
    """Quick analysis function for testing"""
    service = AnalysisService()
    
    message_data = {
        'content': message_text,
        'sender_age': sender_age,
        'recipient_age': recipient_age,
        'timestamp': datetime.now().isoformat()
    }
    
    return await service.analyze_message_async(message_data)

# Example usage
if __name__ == "__main__":
    async def test_analysis_service():
        service = AnalysisService()
        
        # Test message analysis
        test_message = {
            'content': "You're so mature for your age. Don't tell your parents about our chats.",
            'sender_id': 'user_123',
            'recipient_id': 'child_456',
            'session_id': 'session_789',
            'platform': 'instagram',
            'timestamp': datetime.now().isoformat()
        }
        
        result = await service.analyze_message_async(test_message)
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
    
    # Run test
    asyncio.run(test_analysis_service())

