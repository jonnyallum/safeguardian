from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

children_bp = Blueprint('children', __name__)

@children_bp.route('/', methods=['GET'])
@jwt_required()
def get_children():
    """Get children for guardian."""
    return jsonify({'message': 'Children endpoint - coming soon'}), 200

@children_bp.route('/', methods=['POST'])
@jwt_required()
def add_child():
    """Add a new child profile."""
    return jsonify({'message': 'Add child endpoint - coming soon'}), 200

