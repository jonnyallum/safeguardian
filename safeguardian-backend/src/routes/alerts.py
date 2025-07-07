from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models import db
from src.models.user import User
from src.models.alert import Alert, AlertStatus, AlertSeverity, AlertType

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get alerts for guardian."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_guardian():
            return jsonify({'error': 'Only guardians can access alerts'}), 403
        
        # Get query parameters
        child_id = request.args.get('child_id')
        severity = request.args.get('severity')
        status = request.args.get('status')
        alert_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build query
        query = Alert.query.filter_by(guardian_id=user.id)
        
        # Apply filters
        if child_id:
            query = query.filter(Alert.child_id == child_id)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        if status:
            query = query.filter(Alert.status == status)
        
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Alert.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Alert.created_at <= end_dt)
        
        # Order by creation time (most recent first)
        query = query.order_by(Alert.created_at.desc())
        
        # Paginate
        total = query.count()
        alerts = query.offset((page - 1) * limit).limit(limit).all()
        
        # Get summary statistics
        summary = {
            'total': total,
            'new': Alert.query.filter_by(guardian_id=user.id, status=AlertStatus.NEW).count(),
            'acknowledged': Alert.query.filter_by(guardian_id=user.id, status=AlertStatus.ACKNOWLEDGED).count(),
            'investigating': Alert.query.filter_by(guardian_id=user.id, status=AlertStatus.INVESTIGATING).count(),
            'resolved': Alert.query.filter_by(guardian_id=user.id, status=AlertStatus.RESOLVED).count(),
            'escalated': Alert.query.filter_by(guardian_id=user.id, status=AlertStatus.ESCALATED).count()
        }
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'summary': summary,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get alerts: {str(e)}'}), 500

@alerts_bp.route('/<alert_id>', methods=['GET'])
@jwt_required()
def get_alert_details():
    """Get detailed alert information."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Check access permissions
        if user.is_guardian() and alert.guardian_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        elif not user.is_admin() and not user.is_guardian():
            return jsonify({'error': 'Access denied'}), 403
        
        # Get related data
        alert_data = alert.to_dict(include_evidence=True, include_actions=True)
        
        # Include session and message details if available
        if alert.session:
            alert_data['session'] = alert.session.to_dict()
        
        if alert.message:
            alert_data['message'] = alert.message.to_dict(include_content=True, include_analysis=True)
        
        # Include child information
        alert_data['child'] = alert.child.to_dict()
        
        return jsonify({
            'alert': alert_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get alert details: {str(e)}'}), 500

@alerts_bp.route('/<alert_id>/acknowledge', methods=['POST'])
@jwt_required()
def acknowledge_alert():
    """Acknowledge an alert."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Check permissions
        if not user.is_guardian() or alert.guardian_id != user.id:
            return jsonify({'error': 'Only the alert\'s guardian can acknowledge it'}), 403
        
        data = request.get_json() or {}
        notes = data.get('notes')
        
        # Acknowledge the alert
        alert.acknowledge(user.id, notes)
        
        return jsonify({
            'message': 'Alert acknowledged successfully',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to acknowledge alert: {str(e)}'}), 500

@alerts_bp.route('/<alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert():
    """Resolve an alert."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Check permissions
        if not user.is_guardian() or alert.guardian_id != user.id:
            return jsonify({'error': 'Only the alert\'s guardian can resolve it'}), 403
        
        data = request.get_json() or {}
        resolution_notes = data.get('resolution_notes')
        is_false_positive = data.get('is_false_positive', False)
        
        # Resolve the alert
        alert.resolve(user.id, resolution_notes, is_false_positive)
        
        message = 'Alert marked as false positive' if is_false_positive else 'Alert resolved successfully'
        
        return jsonify({
            'message': message,
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to resolve alert: {str(e)}'}), 500

@alerts_bp.route('/<alert_id>/escalate', methods=['POST'])
@jwt_required()
def escalate_alert():
    """Escalate alert to authorities."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Check permissions
        if not user.is_guardian() or alert.guardian_id != user.id:
            return jsonify({'error': 'Only the alert\'s guardian can escalate it'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('escalation_type'):
            return jsonify({'error': 'Escalation type is required'}), 400
        
        escalation_type = data['escalation_type']
        urgency = data.get('urgency', 'medium')
        notes = data.get('notes', '')
        contact_preference = data.get('contact_preference', 'both')
        
        # Generate reference number
        reference_number = f"SG-{datetime.utcnow().strftime('%Y%m%d')}-{alert.id[:8].upper()}"
        
        # Escalate the alert
        alert.escalate(user.id, escalation_type, reference_number, notes)
        
        # In production, this would trigger actual escalation to authorities
        escalation_info = {
            'reference_number': reference_number,
            'escalation_type': escalation_type,
            'urgency': urgency,
            'contact_preference': contact_preference,
            'estimated_response_time': get_estimated_response_time(escalation_type, urgency)
        }
        
        return jsonify({
            'message': 'Alert escalated successfully',
            'escalation': escalation_info,
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to escalate alert: {str(e)}'}), 500

@alerts_bp.route('/<alert_id>/status', methods=['PUT'])
@jwt_required()
def update_alert_status():
    """Update alert status."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Check permissions
        if not user.is_guardian() or alert.guardian_id != user.id:
            return jsonify({'error': 'Only the alert\'s guardian can update its status'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400
        
        try:
            new_status = AlertStatus(data['status'])
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        
        notes = data.get('notes')
        actions_taken = data.get('actions_taken', [])
        
        # Update status
        alert.status = new_status
        
        # Add action to history
        if notes or actions_taken:
            alert.add_action('status_updated', user.id, notes)
            
            if actions_taken:
                if not alert.actions_taken:
                    alert.actions_taken = []
                alert.actions_taken.extend(actions_taken)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Alert status updated successfully',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update alert status: {str(e)}'}), 500

@alerts_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_alerts_summary():
    """Get alerts summary for guardian."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_guardian():
            return jsonify({'error': 'Only guardians can access alerts summary'}), 403
        
        # Get time range from query parameters
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get summary statistics
        base_query = Alert.query.filter(
            Alert.guardian_id == user.id,
            Alert.created_at >= start_date
        )
        
        summary = {
            'period_days': days,
            'total_alerts': base_query.count(),
            'by_severity': {},
            'by_type': {},
            'by_status': {},
            'by_child': {},
            'trends': {
                'daily_counts': [],
                'risk_score_trend': []
            }
        }
        
        # Count by severity
        for severity in AlertSeverity:
            count = base_query.filter(Alert.severity == severity).count()
            summary['by_severity'][severity.value] = count
        
        # Count by type
        for alert_type in AlertType:
            count = base_query.filter(Alert.alert_type == alert_type).count()
            if count > 0:
                summary['by_type'][alert_type.value] = count
        
        # Count by status
        for status in AlertStatus:
            count = base_query.filter(Alert.status == status).count()
            summary['by_status'][status.value] = count
        
        # Count by child
        for child in user.child_profiles:
            count = base_query.filter(Alert.child_id == child.id).count()
            if count > 0:
                summary['by_child'][child.user.get_full_name()] = count
        
        # Get daily trends for the last 7 days
        for i in range(7):
            day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            daily_count = Alert.query.filter(
                Alert.guardian_id == user.id,
                Alert.created_at >= day_start,
                Alert.created_at < day_end
            ).count()
            
            avg_risk_score = db.session.query(
                db.func.avg(Alert.risk_score)
            ).filter(
                Alert.guardian_id == user.id,
                Alert.created_at >= day_start,
                Alert.created_at < day_end
            ).scalar() or 0
            
            summary['trends']['daily_counts'].insert(0, {
                'date': day_start.strftime('%Y-%m-%d'),
                'count': daily_count
            })
            
            summary['trends']['risk_score_trend'].insert(0, {
                'date': day_start.strftime('%Y-%m-%d'),
                'avg_risk_score': round(float(avg_risk_score), 2)
            })
        
        return jsonify({'summary': summary}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get alerts summary: {str(e)}'}), 500

def get_estimated_response_time(escalation_type, urgency):
    """Get estimated response time for escalation."""
    response_times = {
        'police': {
            'critical': '15-30 minutes',
            'high': '1-2 hours',
            'medium': '2-4 hours',
            'low': '4-8 hours'
        },
        'emergency': {
            'critical': '5-10 minutes',
            'high': '10-15 minutes',
            'medium': '15-30 minutes',
            'low': '30-60 minutes'
        },
        'social_services': {
            'critical': '1-2 hours',
            'high': '2-4 hours',
            'medium': '4-8 hours',
            'low': '1-2 business days'
        }
    }
    
    return response_times.get(escalation_type, {}).get(urgency, 'Unknown')

