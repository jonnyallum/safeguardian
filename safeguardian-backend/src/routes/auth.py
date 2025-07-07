from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from src.models import db
from src.models.user import User, UserRole
from src.models.family import Family

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        email = data['email'].lower().strip()
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Validate role
        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Handle family association
        family = None
        if data.get('family_code'):
            family = Family.query.filter_by(family_code=data['family_code']).first()
            if not family:
                return jsonify({'error': 'Invalid family code'}), 400
        elif role == UserRole.GUARDIAN:
            # Create new family for guardian
            family = Family(
                name=f"{data['first_name']} {data['last_name']} Family"
            )
            db.session.add(family)
            db.session.flush()  # Get the family ID
        
        # Create user
        user = User(
            email=email,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            family_id=family.id if family else None,
            phone=data.get('phone'),
            timezone=data.get('timezone', 'UTC'),
            language=data.get('language', 'en')
        )
        user.set_password(password)
        
        db.session.add(user)
        
        # Set as primary guardian if creating new family
        if family and role == UserRole.GUARDIAN and not family.primary_guardian_id:
            family.primary_guardian_id = user.id
        
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role.value,
                'family_id': user.family_id
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict(),
            'family': family.to_dict() if family else None,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user credentials."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if account is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            return jsonify({
                'error': 'Account is temporarily locked due to failed login attempts',
                'locked_until': user.locked_until.isoformat()
            }), 423
        
        # Verify password
        if not user.check_password(password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            db.session.commit()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check for MFA if enabled
        if user.two_factor_enabled:
            mfa_code = data.get('mfa_code')
            if not mfa_code:
                return jsonify({
                    'error': 'MFA code required',
                    'mfa_required': True
                }), 200
            
            # Verify MFA code (placeholder - would implement actual TOTP verification)
            if not verify_mfa_code(user, mfa_code):
                return jsonify({'error': 'Invalid MFA code'}), 401
        
        # Successful login - reset failed attempts and update login info
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        user.login_count += 1
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role.value,
                'family_id': user.family_id
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'family': user.family.to_dict() if user.family else None,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        # Create new access token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role.value,
                'family_id': user.family_id
            }
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Invalidate user session and tokens."""
    try:
        # In a production system, you would add the token to a blacklist
        # For now, we'll just return success
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
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
        return jsonify({'error': f'Failed to get user info: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        new_password = data['new_password']
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400
        
        # Update password
        user.set_password(new_password)
        user.password_changed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset."""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        user = User.query.filter_by(email=email).first()
        
        # Always return success to prevent email enumeration
        if user and user.is_active:
            # In production, send password reset email
            # For now, just log the request
            print(f"Password reset requested for {email}")
        
        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Password reset request failed: {str(e)}'}), 500

@auth_bp.route('/verify-email', methods=['POST'])
@jwt_required()
def verify_email():
    """Verify user email address."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        verification_code = data.get('verification_code')
        
        # In production, verify the actual code
        # For now, just mark as verified
        if verification_code:
            user.is_verified = True
            user.email_verified_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({'message': 'Email verified successfully'}), 200
        
        return jsonify({'error': 'Verification code is required'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Email verification failed: {str(e)}'}), 500

def verify_mfa_code(user, code):
    """Verify MFA code (placeholder implementation)."""
    # In production, implement actual TOTP verification
    # For demo purposes, accept '123456' as valid code
    return code == '123456'

