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
from src.models import db, init_supabase
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
from src.routes.supabase_test import supabase_test_bp

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
    
    # Database configuration - Use Supabase PostgreSQL
    supabase_url = os.getenv('SUPABASE_URL')
    if supabase_url:
        # Extract database connection details from Supabase URL
        # Format: postgresql://postgres:[password]@db.project.supabase.co:5432/postgres
        project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')
        database_url = f"postgresql://postgres.{project_ref}:@db.{project_ref}.supabase.co:5432/postgres"
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
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
    
    # Initialize Supabase clients
    supabase_initialized = init_supabase()
    
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
    app.register_blueprint(supabase_test_bp, url_prefix='/api/supabase')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'SafeGuardian API',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'Supabase PostgreSQL' if supabase_url else 'SQLite',
            'supabase_connected': supabase_initialized
        })
    
    # API info endpoint
    @app.route('/api/info')
    def api_info():
        return jsonify({
            'name': 'SafeGuardian API',
            'version': '1.0.0',
            'description': 'Multi-platform child protection monitoring system',
            'database': 'Supabase PostgreSQL' if supabase_url else 'SQLite',
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
    
    # Supabase connection test endpoint
    @app.route('/api/supabase/test')
    def test_supabase():
        try:
            from src.models import supabase
            if supabase:
                # Test connection by getting auth user (should work even without auth)
                response = supabase.auth.get_session()
                return jsonify({
                    'status': 'connected',
                    'message': 'Supabase connection successful',
                    'url': os.getenv('SUPABASE_URL'),
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Supabase client not initialized'
                }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Supabase connection failed: {str(e)}'
            }), 500
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
            
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
                print("✅ Default admin user created: admin@safeguardian.com / SafeGuardian2024!")
                
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
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
                # Return API test interface if no frontend is available
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>SafeGuardian API</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
                        .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
                        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
                        button:hover { background: #0056b3; }
                        .response { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; font-family: monospace; white-space: pre-wrap; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🛡️ SafeGuardian API</h1>
                        <div class="status success">
                            <strong>✅ API Server Running</strong><br>
                            Version: 1.0.0<br>
                            Database: """ + ('Supabase PostgreSQL' if supabase_url else 'SQLite') + """<br>
                            Supabase: """ + ('Connected' if supabase_initialized else 'Not Connected') + """
                        </div>
                        
                        <h2>API Endpoints</h2>
                        <div class="endpoint">
                            <strong>GET /api/health</strong> - Health check
                            <button onclick="testEndpoint('/api/health')">Test</button>
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/info</strong> - API information
                            <button onclick="testEndpoint('/api/info')">Test</button>
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/supabase/test</strong> - Supabase connection test
                            <button onclick="testEndpoint('/api/supabase/test')">Test</button>
                        </div>
                        
                        <div id="response" class="response" style="display: none;"></div>
                        
                        <script>
                            async function testEndpoint(endpoint) {
                                const responseDiv = document.getElementById('response');
                                responseDiv.style.display = 'block';
                                responseDiv.textContent = 'Loading...';
                                
                                try {
                                    const response = await fetch(endpoint);
                                    const data = await response.json();
                                    responseDiv.textContent = JSON.stringify(data, null, 2);
                                } catch (error) {
                                    responseDiv.textContent = 'Error: ' + error.message;
                                }
                            }
                        </script>
                    </div>
                </body>
                </html>
                """
    
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
    
    print(f"🚀 Starting SafeGuardian API server on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🗄️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

