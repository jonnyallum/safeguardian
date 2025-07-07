"""
SafeGuardian AI Analysis API Routes
Provides endpoints for AI-powered grooming detection and analysis
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import asyncio
import json
import logging

# Import AI services
from ..ai.analysis_service import AnalysisService, create_analysis_service
from ..ai.grooming_detector import RiskLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
ai_bp = Blueprint('ai_analysis', __name__, url_prefix='/api/ai')

# Initialize analysis service
analysis_service = create_analysis_service()

@ai_bp.route('/analyze/message', methods=['POST'])
@jwt_required()
def analyze_message():
    """
    Analyze a single message for grooming indicators
    
    Expected JSON payload:
    {
        "message": "text content",
        "sender_id": "user_id",
        "recipient_id": "child_id",
        "session_id": "session_id",
        "platform": "platform_name",
        "metadata": {}
    }
    """
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message content is required',
                'status': 'error'
            }), 400
        
        # Prepare message data for analysis
        message_data = {
            'content': data['message'],
            'sender_id': data.get('sender_id'),
            'recipient_id': data.get('recipient_id'),
            'session_id': data.get('session_id'),
            'platform': data.get('platform', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'metadata': data.get('metadata', {})
        }
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            analysis_service.analyze_message_async(message_data)
        )
        loop.close()
        
        # Log high-risk detections
        if result.get('risk_level') in ['high', 'critical']:
            logger.warning(f"High-risk message detected: {result.get('explanation')}")
        
        return jsonify({
            'status': 'success',
            'analysis': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in message analysis: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e),
            'status': 'error'
        }), 500

@ai_bp.route('/analyze/conversation/<session_id>', methods=['GET'])
@jwt_required()
def analyze_conversation(session_id):
    """
    Analyze an entire conversation thread for grooming patterns
    """
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        
        # Run async thread analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            analysis_service.analyze_conversation_thread_async(session_id, limit)
        )
        loop.close()
        
        return jsonify({
            'status': 'success',
            'thread_analysis': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in conversation analysis: {str(e)}")
        return jsonify({
            'error': 'Thread analysis failed',
            'message': str(e),
            'status': 'error'
        }), 500

@ai_bp.route('/risk-assessment/<child_id>', methods=['GET'])
@jwt_required()
def get_risk_assessment(child_id):
    """
    Get comprehensive risk assessment for a child
    """
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        days = request.args.get('days', 7, type=int)
        time_range = timedelta(days=days)
        
        # Run async risk assessment
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            analysis_service.get_risk_assessment(child_id, time_range)
        )
        loop.close()
        
        return jsonify({
            'status': 'success',
            'risk_assessment': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        return jsonify({
            'error': 'Risk assessment failed',
            'message': str(e),
            'status': 'error'
        }), 500

@ai_bp.route('/analytics/platform/<platform>', methods=['GET'])
@jwt_required()
def get_platform_analytics(platform):
    """
    Get analytics for a specific platform
    """
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        time_range = timedelta(days=days)
        
        # Run async platform analytics
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            analysis_service.get_platform_analytics(platform, time_range)
        )
        loop.close()
        
        return jsonify({
            'status': 'success',
            'platform_analytics': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in platform analytics: {str(e)}")
        return jsonify({
            'error': 'Platform analytics failed',
            'message': str(e),
            'status': 'error'
        }), 500

@ai_bp.route('/patterns', methods=['GET'])
@jwt_required()
def get_grooming_patterns():
    """
    Get information about grooming patterns that the AI can detect
    """
    try:
        patterns_info = {
            'trust_building': {
                'name': 'Trust Building',
                'description': 'Attempts to build trust and emotional connection',
                'examples': ['You can trust me', 'I understand you', 'You\'re so mature'],
                'risk_level': 'medium'
            },
            'isolation': {
                'name': 'Isolation',
                'description': 'Attempts to isolate the child from support systems',
                'examples': ['Don\'t tell anyone', 'Your parents wouldn\'t understand'],
                'risk_level': 'high'
            },
            'sexual_content': {
                'name': 'Sexual Content',
                'description': 'Introduction of sexual topics or content',
                'examples': ['You\'re so sexy', 'Curious about your body'],
                'risk_level': 'critical'
            },
            'meeting_request': {
                'name': 'Meeting Request',
                'description': 'Requests to meet in person',
                'examples': ['Want to meet up?', 'Come to my place'],
                'risk_level': 'critical'
            },
            'secrecy': {
                'name': 'Secrecy',
                'description': 'Requests to keep communications secret',
                'examples': ['Keep this between us', 'Our little secret'],
                'risk_level': 'high'
            },
            'gift_offering': {
                'name': 'Gift Offering',
                'description': 'Offers of gifts, money, or special treatment',
                'examples': ['I have a gift for you', 'Want to buy you something'],
                'risk_level': 'medium'
            }
        }
        
        return jsonify({
            'status': 'success',
            'patterns': patterns_info,
            'total_patterns': len(patterns_info),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting patterns: {str(e)}")
        return jsonify({
            'error': 'Failed to get patterns',
            'message': str(e),
            'status': 'error'
        }), 500

@ai_bp.route('/test/analyze', methods=['POST'])
@jwt_required()
def test_analysis():
    """
    Test endpoint for quick message analysis (development/testing only)
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message content is required',
                'status': 'error'
            }), 400
        
        # Quick analysis without database storage
        from ..ai.grooming_detector import GroomingDetector
        
        detector = GroomingDetector()
        result = detector.analyze_message(
            message=data['message'],
            sender_age=data.get('sender_age'),
            recipient_age=data.get('recipient_age')
        )
        
        # Convert result to dictionary
        analysis_result = {
            'risk_level': result.risk_level.value,
            'confidence': result.confidence,
            'patterns_detected': [p.value for p in result.patterns_detected],
            'risk_factors': result.risk_factors,
            'explanation': result.explanation,
            'recommendations': result.recommendations,
            'message_hash': result.message_hash
        }
        
        return jsonify({
            'status': 'success',
            'test_analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test analysis: {str(e)}")
        return jsonify({
            'error': 'Test analysis failed',
            'message': str(e),
            'status': 'error'
        }), 500

@ai_bp.route('/stats/overview', methods=['GET'])
@jwt_required()
def get_ai_stats():
    """
    Get overview statistics for AI analysis system
    """
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        days = request.args.get('days', 7, type=int)
        
        # Mock statistics (replace with actual database queries)
        stats = {
            'total_analyses': 1247,
            'high_risk_detections': 23,
            'patterns_detected': {
                'trust_building': 45,
                'isolation': 12,
                'sexual_content': 8,
                'meeting_request': 5,
                'secrecy': 18,
                'gift_offering': 15
            },
            'platform_breakdown': {
                'instagram': 456,
                'facebook': 321,
                'snapchat': 234,
                'tiktok': 156,
                'discord': 80
            },
            'risk_distribution': {
                'low': 1089,
                'medium': 135,
                'high': 18,
                'critical': 5
            },
            'accuracy_metrics': {
                'precision': 0.94,
                'recall': 0.89,
                'f1_score': 0.91
            },
            'processing_time': {
                'average_ms': 245,
                'max_ms': 1200,
                'min_ms': 89
            }
        }
        
        return jsonify({
            'status': 'success',
            'ai_statistics': stats,
            'period_days': days,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting AI stats: {str(e)}")
        return jsonify({
            'error': 'Failed to get AI statistics',
            'message': str(e),
            'status': 'error'
        }), 500

@ai_bp.route('/health', methods=['GET'])
def ai_health_check():
    """
    Health check endpoint for AI analysis system
    """
    try:
        # Test AI system components
        from ..ai.grooming_detector import GroomingDetector
        
        detector = GroomingDetector()
        
        # Quick test analysis
        test_result = detector.analyze_message("Hello, how are you?")
        
        health_status = {
            'ai_system': 'operational',
            'grooming_detector': 'active',
            'analysis_service': 'ready',
            'patterns_loaded': len(detector.patterns),
            'keywords_loaded': len(detector.risk_keywords),
            'test_analysis': 'passed' if test_result else 'failed',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'healthy',
            'components': health_status
        }), 200
        
    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@ai_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'message': 'Invalid request data',
        'status': 'error'
    }), 400

@ai_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required',
        'status': 'error'
    }), 401

@ai_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'AI analysis system error',
        'status': 'error'
    }), 500

# Register blueprint function
def register_ai_routes(app):
    """Register AI analysis routes with Flask app"""
    app.register_blueprint(ai_bp)
    logger.info("AI analysis routes registered successfully")

