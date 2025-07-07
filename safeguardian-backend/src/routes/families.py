from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

families_bp = Blueprint('families', __name__)

@families_bp.route('/', methods=['GET'])
@jwt_required()
def get_family():
    """Get family information."""
    return jsonify({'message': 'Families endpoint - coming soon'}), 200

@families_bp.route('/members', methods=['GET'])
@jwt_required()
def get_family_members():
    """Get family members."""
    return jsonify({'message': 'Family members endpoint - coming soon'}), 200

