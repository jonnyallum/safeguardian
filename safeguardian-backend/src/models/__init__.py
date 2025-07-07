from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os
from supabase import create_client, Client

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

# Supabase client initialization
def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError("Supabase URL and ANON_KEY must be set in environment variables")
    
    return create_client(url, key)

# Service role client for admin operations
def get_supabase_service_client() -> Client:
    """Initialize and return Supabase service role client"""
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not service_key:
        raise ValueError("Supabase URL and SERVICE_ROLE_KEY must be set in environment variables")
    
    return create_client(url, service_key)

# Global Supabase clients
supabase: Client = None
supabase_admin: Client = None

def init_supabase():
    """Initialize Supabase clients"""
    global supabase, supabase_admin
    try:
        supabase = get_supabase_client()
        supabase_admin = get_supabase_service_client()
        print("✅ Supabase clients initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Supabase clients: {e}")
        return False

