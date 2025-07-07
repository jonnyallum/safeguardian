import os
import sys
from datetime import datetime, timedelta

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Import database and models
from src.models import db
from src.models.user import User
from src.models.family import Family
from src.models.child_profile import ChildProfile
from src.models.platform_connection import PlatformConnection
from src.models.monitoring_session import MonitoringSession
from src.models.session_participant import SessionParticipant
from src.models.message import Message
from src.models.alert import Alert
from src.models.ai_analysis import AIAnalysis
from src.models.evidence import Evidence

# Import routes
from src.routes.auth import auth_bp
from src.routes.users import users_bp
from src.routes.families import families_bp
from src.routes.children import children_bp
from src.routes.platforms import platforms_bp
from src.routes.monitoring import monitoring_bp
from src.routes.alerts import alerts_bp
from src.routes.evidence import evidence_bp
from src.routes.analytics import analytics_bp
from src.routes.admin import admin_bp

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'safeguardian-dev-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'safeguardian.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Enable CORS for all routes
    CORS(app, origins="*", supports_credentials=True)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize SocketIO for real-time features
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(families_bp, url_prefix='/api/families')
    app.register_blueprint(children_bp, url_prefix='/api/children')
    app.register_blueprint(platforms_bp, url_prefix='/api/platforms')
    app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(evidence_bp, url_prefix='/api/evidence')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'SafeGuardian API',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # API info endpoint
    @app.route('/api/info')
    def api_info():
        return jsonify({
            'name': 'SafeGuardian API',
            'version': '1.0.0',
            'description': 'Multi-platform child protection monitoring system',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'families': '/api/families',
                'children': '/api/children',
                'platforms': '/api/platforms',
                'monitoring': '/api/monitoring',
                'alerts': '/api/alerts',
                'evidence': '/api/evidence',
                'analytics': '/api/analytics',
                'admin': '/api/admin'
            },
            'documentation': '/api/docs',
            'health': '/api/health'
        })
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
            
            # Create default admin user if it doesn't exist
            admin_user = User.query.filter_by(email='admin@safeguardian.com').first()
            if not admin_user:
                from src.models.user import UserRole
                admin_user = User(
                    email='admin@safeguardian.com',
                    first_name='System',
                    last_name='Administrator',
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True
                )
                admin_user.set_password('SafeGuardian2024!')
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin user created: admin@safeguardian.com / SafeGuardian2024!")
                
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    # Frontend serving routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return jsonify({'error': 'Static folder not configured'}), 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                # Return API info if no frontend is available
                return jsonify({
                    'message': 'SafeGuardian API is running',
                    'api_info': '/api/info',
                    'health_check': '/api/health'
                })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': 'File too large'}), 413
    
    # Store socketio instance for use in other modules
    app.socketio = socketio
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting SafeGuardian API server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

