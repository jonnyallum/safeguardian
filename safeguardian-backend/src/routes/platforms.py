from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

platforms_bp = Blueprint('platforms', __name__)

@platforms_bp.route('/', methods=['GET'])
@jwt_required()
def get_platforms():
    """Get supported platforms."""
    return jsonify({'message': 'Platforms endpoint - coming soon'}), 200

