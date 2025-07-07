from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

evidence_bp = Blueprint('evidence', __name__)

@evidence_bp.route('/', methods=['GET'])
@jwt_required()
def get_evidence():
    """Get evidence files."""
    return jsonify({'message': 'Evidence endpoint - coming soon'}), 200

