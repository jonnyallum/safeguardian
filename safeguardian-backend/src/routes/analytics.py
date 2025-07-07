from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get analytics data."""
    return jsonify({'message': 'Analytics endpoint - coming soon'}), 200

