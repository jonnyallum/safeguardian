from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models import db
from src.models.user import User, UserRole

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'family': user.family.to_dict() if user.family else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'timezone' in data:
            user.timezone = data['timezone']
        if 'language' in data:
            user.language = data['language']
        if 'preferences' in data:
            user.preferences.update(data['preferences'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500

@users_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user preferences."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'preferences': user.preferences
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get preferences: {str(e)}'}), 500

@users_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user preferences."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Merge new preferences with existing ones
        if user.preferences is None:
            user.preferences = {}
        
        user.preferences.update(data)
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': user.preferences
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Preferences update failed: {str(e)}'}), 500

@users_bp.route('/family-members', methods=['GET'])
@jwt_required()
def get_family_members():
    """Get family members for current user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.family_id:
            return jsonify({'error': 'User not found or not part of a family'}), 404
        
        family_members = User.query.filter_by(family_id=user.family_id).all()
        
        return jsonify({
            'family_members': [member.to_dict() for member in family_members],
            'total': len(family_members)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get family members: {str(e)}'}), 500

@users_bp.route('/children', methods=['GET'])
@jwt_required()
def get_children():
    """Get children for guardian user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_guardian():
            return jsonify({'error': 'Only guardians can access children'}), 403
        
        children = user.child_profiles
        
        return jsonify({
            'children': [child.to_dict() for child in children],
            'total': len(children)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get children: {str(e)}'}), 500

@users_bp.route('/notifications/settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """Get notification settings for user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get notification preferences from user preferences
        notification_settings = user.preferences.get('notifications', {
            'email': True,
            'sms': True,
            'push': True,
            'in_app': True,
            'alert_thresholds': {
                'low': False,
                'medium': True,
                'high': True,
                'critical': True,
                'emergency': True
            },
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00'
            },
            'digest': {
                'enabled': True,
                'frequency': 'daily',
                'time': '09:00'
            }
        })
        
        return jsonify({
            'notification_settings': notification_settings
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get notification settings: {str(e)}'}), 500

@users_bp.route('/notifications/settings', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """Update notification settings for user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Initialize preferences if not exists
        if user.preferences is None:
            user.preferences = {}
        
        # Update notification settings
        user.preferences['notifications'] = data
        db.session.commit()
        
        return jsonify({
            'message': 'Notification settings updated successfully',
            'notification_settings': data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Notification settings update failed: {str(e)}'}), 500

@users_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_user_activity():
    """Get user activity summary."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get activity summary based on user role
        activity_summary = {
            'login_count': user.login_count,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'account_created': user.created_at.isoformat(),
            'email_verified': user.is_verified,
            'two_factor_enabled': user.two_factor_enabled
        }
        
        if user.is_guardian():
            # Add guardian-specific activity
            from src.models.alert import Alert
            from src.models.monitoring_session import MonitoringSession
            
            total_alerts = Alert.query.filter_by(guardian_id=user.id).count()
            unresolved_alerts = Alert.query.filter_by(guardian_id=user.id).filter(
                Alert.status.in_(['new', 'acknowledged', 'investigating'])
            ).count()
            
            active_sessions = MonitoringSession.query.join(
                user.child_profiles
            ).filter(MonitoringSession.status == 'active').count()
            
            activity_summary.update({
                'total_alerts': total_alerts,
                'unresolved_alerts': unresolved_alerts,
                'active_monitoring_sessions': active_sessions,
                'children_count': len(user.child_profiles)
            })
        
        return jsonify({
            'activity_summary': activity_summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user activity: {str(e)}'}), 500

@users_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate user account."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Verify password for security
        if not data.get('password') or not user.check_password(data['password']):
            return jsonify({'error': 'Password verification required'}), 401
        
        # Deactivate account
        user.is_active = False
        user.deleted_at = db.func.now()
        
        # Add reason to metadata
        if data.get('reason'):
            if user.metadata is None:
                user.metadata = {}
            user.metadata['deactivation_reason'] = data['reason']
            user.metadata['deactivated_at'] = db.func.now()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Account deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Account deactivation failed: {str(e)}'}), 500

@users_bp.route('/export-data', methods=['POST'])
@jwt_required()
def export_user_data():
    """Export user data (GDPR compliance)."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Collect all user data
        user_data = {
            'user_profile': user.to_dict(include_sensitive=True),
            'family': user.family.to_dict() if user.family else None
        }
        
        if user.is_guardian():
            # Include guardian-specific data
            from src.models.alert import Alert
            from src.models.monitoring_session import MonitoringSession
            
            alerts = Alert.query.filter_by(guardian_id=user.id).all()
            user_data['alerts'] = [alert.to_dict(include_evidence=True) for alert in alerts]
            
            children_data = []
            for child in user.child_profiles:
                child_data = child.to_dict(include_sensitive=True)
                
                # Include monitoring sessions
                sessions = MonitoringSession.query.filter_by(child_id=child.id).all()
                child_data['monitoring_sessions'] = [session.to_dict(include_details=True) for session in sessions]
                
                children_data.append(child_data)
            
            user_data['children'] = children_data
        
        # In production, this would generate a secure download link
        return jsonify({
            'message': 'Data export prepared',
            'data': user_data,
            'export_timestamp': db.func.now(),
            'note': 'In production, this would be a secure download link'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Data export failed: {str(e)}'}), 500

