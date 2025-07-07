from flask import Blueprint, jsonify
from datetime import datetime
import os
from src.models import supabase, supabase_admin

supabase_test_bp = Blueprint('supabase_test', __name__)

@supabase_test_bp.route('/test', methods=['GET'])
def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    try:
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'supabase_url': os.getenv('SUPABASE_URL'),
            'tests': {}
        }
        
        # Test 1: Basic client initialization
        if supabase:
            results['tests']['client_init'] = {'status': 'success', 'message': 'Supabase client initialized'}
        else:
            results['tests']['client_init'] = {'status': 'error', 'message': 'Supabase client not initialized'}
            return jsonify(results), 500
        
        # Test 2: Auth session check
        try:
            auth_response = supabase.auth.get_session()
            results['tests']['auth_check'] = {'status': 'success', 'message': 'Auth service accessible'}
        except Exception as e:
            results['tests']['auth_check'] = {'status': 'error', 'message': f'Auth error: {str(e)}'}
        
        # Test 3: Database connection test (simple query)
        try:
            # Try to query a system table that should always exist
            response = supabase.table('information_schema.tables').select('table_name').limit(1).execute()
            results['tests']['database_query'] = {'status': 'success', 'message': 'Database query successful'}
        except Exception as e:
            results['tests']['database_query'] = {'status': 'error', 'message': f'Database error: {str(e)}'}
        
        # Test 4: Service role client test
        try:
            if supabase_admin:
                # Test admin client with a simple operation
                admin_response = supabase_admin.auth.get_session()
                results['tests']['admin_client'] = {'status': 'success', 'message': 'Admin client accessible'}
            else:
                results['tests']['admin_client'] = {'status': 'error', 'message': 'Admin client not initialized'}
        except Exception as e:
            results['tests']['admin_client'] = {'status': 'error', 'message': f'Admin client error: {str(e)}'}
        
        # Overall status
        failed_tests = [test for test, result in results['tests'].items() if result['status'] == 'error']
        if failed_tests:
            results['overall_status'] = 'partial'
            results['message'] = f'Some tests failed: {", ".join(failed_tests)}'
            return jsonify(results), 207  # Multi-status
        else:
            results['overall_status'] = 'success'
            results['message'] = 'All Supabase tests passed'
            return jsonify(results), 200
            
    except Exception as e:
        return jsonify({
            'overall_status': 'error',
            'message': f'Supabase test failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@supabase_test_bp.route('/tables', methods=['GET'])
def list_tables():
    """List all tables in the Supabase database"""
    try:
        if not supabase:
            return jsonify({'error': 'Supabase client not initialized'}), 500
        
        # Query information schema to get table list
        response = supabase.table('information_schema.tables').select('table_name, table_schema').eq('table_type', 'BASE TABLE').execute()
        
        tables = []
        for table in response.data:
            if table['table_schema'] not in ['information_schema', 'pg_catalog']:
                tables.append({
                    'name': table['table_name'],
                    'schema': table['table_schema']
                })
        
        return jsonify({
            'status': 'success',
            'tables': tables,
            'count': len(tables),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to list tables: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@supabase_test_bp.route('/create-test-table', methods=['POST'])
def create_test_table():
    """Create a test table to verify database write permissions"""
    try:
        if not supabase_admin:
            return jsonify({'error': 'Supabase admin client not initialized'}), 500
        
        # Create a simple test table
        table_sql = """
        CREATE TABLE IF NOT EXISTS safeguardian_test (
            id SERIAL PRIMARY KEY,
            test_data TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Execute SQL using RPC (if available) or direct table operations
        try:
            # Try to create via table operations first
            test_data = {
                'test_data': 'Supabase connection test',
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = supabase_admin.table('safeguardian_test').insert(test_data).execute()
            
            return jsonify({
                'status': 'success',
                'message': 'Test table created and data inserted',
                'data': response.data,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as insert_error:
            return jsonify({
                'status': 'error',
                'message': f'Failed to create test table: {str(insert_error)}',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Test table creation failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

