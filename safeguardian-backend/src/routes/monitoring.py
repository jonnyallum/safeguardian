from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models import db
from src.models.user import User
from src.models.child_profile import ChildProfile
from src.models.monitoring_session import MonitoringSession, SessionStatus
from src.models.message import Message
from src.models.session_participant import SessionParticipant

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get monitoring sessions for guardian."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_guardian():
            return jsonify({'error': 'Only guardians can access monitoring sessions'}), 403
        
        # Get query parameters
        child_id = request.args.get('child_id')
        status = request.args.get('status')
        platform = request.args.get('platform')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build query
        query = MonitoringSession.query.join(ChildProfile).filter(
            ChildProfile.guardian_id == user.id
        )
        
        # Apply filters
        if child_id:
            query = query.filter(MonitoringSession.child_id == child_id)
        
        if status:
            query = query.filter(MonitoringSession.status == status)
        
        if platform:
            from src.models.platform_connection import PlatformConnection
            query = query.join(PlatformConnection).filter(
                PlatformConnection.platform == platform
            )
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(MonitoringSession.start_time >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(MonitoringSession.start_time <= end_dt)
        
        # Order by start time (most recent first)
        query = query.order_by(MonitoringSession.start_time.desc())
        
        # Paginate
        total = query.count()
        sessions = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get sessions: {str(e)}'}), 500

@monitoring_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session_details():
    """Get detailed session information."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = MonitoringSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check access permissions
        if user.is_guardian() and session.child.guardian_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        elif user.is_child() and session.child.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        elif not user.is_admin() and not user.is_guardian() and not user.is_child():
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'session': session.to_dict(include_details=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get session details: {str(e)}'}), 500

@monitoring_bp.route('/sessions/<session_id>/messages', methods=['GET'])
@jwt_required()
def get_session_messages():
    """Get messages for a monitoring session."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = MonitoringSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check access permissions
        if user.is_guardian() and session.child.guardian_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        include_content = request.args.get('include_content', 'true').lower() == 'true'
        
        # Get messages
        query = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.desc())
        
        total = query.count()
        messages = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            'messages': [message.to_dict(include_content=include_content) for message in messages],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get session messages: {str(e)}'}), 500

@monitoring_bp.route('/sessions/<session_id>/actions', methods=['POST'])
@jwt_required()
def perform_session_action():
    """Perform action on monitoring session."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = MonitoringSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check permissions
        if not user.is_guardian() or session.child.guardian_id != user.id:
            return jsonify({'error': 'Only the child\'s guardian can perform session actions'}), 403
        
        data = request.get_json()
        action = data.get('action')
        reason = data.get('reason', '')
        notes = data.get('notes', '')
        
        if action == 'pause':
            if session.status == SessionStatus.ACTIVE:
                session.status = SessionStatus.PAUSED
                message = 'Session paused successfully'
            else:
                return jsonify({'error': 'Can only pause active sessions'}), 400
                
        elif action == 'resume':
            if session.status == SessionStatus.PAUSED:
                session.status = SessionStatus.ACTIVE
                message = 'Session resumed successfully'
            else:
                return jsonify({'error': 'Can only resume paused sessions'}), 400
                
        elif action == 'terminate':
            if session.status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
                session.end_session()
                session.status = SessionStatus.TERMINATED
                message = 'Session terminated successfully'
            else:
                return jsonify({'error': 'Can only terminate active or paused sessions'}), 400
                
        elif action == 'escalate':
            session.status = SessionStatus.EMERGENCY
            # Create alert for escalation
            from src.models.alert import Alert, AlertType, AlertSeverity
            alert = Alert(
                session_id=session.id,
                child_id=session.child_id,
                guardian_id=user.id,
                alert_type=AlertType.SUSPICIOUS_BEHAVIOR,
                severity=AlertSeverity.HIGH,
                title='Session Manually Escalated',
                description=f'Guardian manually escalated session. Reason: {reason}',
                risk_score=7.0,
                confidence_score=1.0,
                triggered_by={
                    'type': 'manual_escalation',
                    'user_id': user.id,
                    'reason': reason
                }
            )
            db.session.add(alert)
            message = 'Session escalated successfully'
            
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Log the action in session metadata
        if session.metadata is None:
            session.metadata = {}
        
        if 'actions' not in session.metadata:
            session.metadata['actions'] = []
        
        session.metadata['actions'].append({
            'action': action,
            'user_id': user.id,
            'timestamp': datetime.utcnow().isoformat(),
            'reason': reason,
            'notes': notes
        })
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Session action failed: {str(e)}'}), 500

@monitoring_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_monitoring_dashboard():
    """Get monitoring dashboard data for guardian."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_guardian():
            return jsonify({'error': 'Only guardians can access monitoring dashboard'}), 403
        
        # Get dashboard data
        children = user.child_profiles
        
        dashboard_data = {
            'summary': {
                'total_children': len(children),
                'active_sessions': 0,
                'total_alerts': 0,
                'unresolved_alerts': 0,
                'platforms_monitored': 0
            },
            'children': [],
            'recent_alerts': [],
            'active_sessions': []
        }
        
        # Collect data for each child
        for child in children:
            child_data = child.to_dict()
            
            # Get active sessions
            active_sessions = MonitoringSession.query.filter_by(
                child_id=child.id,
                status=SessionStatus.ACTIVE
            ).all()
            
            # Get recent alerts
            from src.models.alert import Alert
            recent_alerts = Alert.query.filter_by(child_id=child.id).order_by(
                Alert.created_at.desc()
            ).limit(5).all()
            
            # Get platform connections
            platform_count = len(child.get_active_platforms())
            
            child_data.update({
                'active_sessions_count': len(active_sessions),
                'recent_alerts_count': len(recent_alerts),
                'platforms_connected': platform_count
            })
            
            dashboard_data['children'].append(child_data)
            dashboard_data['summary']['active_sessions'] += len(active_sessions)
            dashboard_data['summary']['platforms_monitored'] += platform_count
            
            # Add to global lists
            dashboard_data['active_sessions'].extend([
                session.to_dict() for session in active_sessions
            ])
            dashboard_data['recent_alerts'].extend([
                alert.to_dict() for alert in recent_alerts
            ])
        
        # Get total alert counts
        from src.models.alert import Alert
        total_alerts = Alert.query.filter_by(guardian_id=user.id).count()
        unresolved_alerts = Alert.query.filter_by(guardian_id=user.id).filter(
            Alert.status.in_(['new', 'acknowledged', 'investigating'])
        ).count()
        
        dashboard_data['summary']['total_alerts'] = total_alerts
        dashboard_data['summary']['unresolved_alerts'] = unresolved_alerts
        
        # Sort recent alerts by creation time
        dashboard_data['recent_alerts'].sort(
            key=lambda x: x['created_at'], reverse=True
        )
        dashboard_data['recent_alerts'] = dashboard_data['recent_alerts'][:10]
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard data: {str(e)}'}), 500

@monitoring_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_monitoring_stats():
    """Get monitoring statistics."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_guardian():
            return jsonify({'error': 'Only guardians can access monitoring stats'}), 403
        
        # Get time range from query parameters
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get statistics
        stats = {}
        
        # Session statistics
        total_sessions = MonitoringSession.query.join(ChildProfile).filter(
            ChildProfile.guardian_id == user.id,
            MonitoringSession.start_time >= start_date
        ).count()
        
        avg_session_duration = db.session.query(
            db.func.avg(MonitoringSession.duration_seconds)
        ).join(ChildProfile).filter(
            ChildProfile.guardian_id == user.id,
            MonitoringSession.start_time >= start_date,
            MonitoringSession.duration_seconds.isnot(None)
        ).scalar() or 0
        
        # Alert statistics
        from src.models.alert import Alert
        total_alerts = Alert.query.filter(
            Alert.guardian_id == user.id,
            Alert.created_at >= start_date
        ).count()
        
        # Risk score statistics
        avg_risk_score = db.session.query(
            db.func.avg(MonitoringSession.risk_score)
        ).join(ChildProfile).filter(
            ChildProfile.guardian_id == user.id,
            MonitoringSession.start_time >= start_date
        ).scalar() or 0
        
        stats = {
            'period_days': days,
            'total_sessions': total_sessions,
            'avg_session_duration_minutes': round(avg_session_duration / 60, 1) if avg_session_duration else 0,
            'total_alerts': total_alerts,
            'avg_risk_score': round(float(avg_risk_score), 2),
            'alerts_per_session': round(total_alerts / max(total_sessions, 1), 2)
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get monitoring stats: {str(e)}'}), 500

