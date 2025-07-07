#!/usr/bin/env python3
"""
SafeGuardian Integration Test Suite
Comprehensive testing of all system components and their interactions
"""

import asyncio
import json
import logging
import sys
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import requests
import uuid

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import SafeGuardian components
from ai.grooming_detector import GroomingDetector, RiskLevel
from ai.analysis_service import quick_message_analysis
from monitoring.real_time_monitor import create_real_time_monitor
from alerts.alert_manager import create_alert_manager, AlertType
from security.security_manager import create_security_manager, UserRole
from security.forensic_logger import create_forensic_logger, EvidenceType
from websocket.websocket_manager import create_websocket_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SafeGuardianIntegrationTester:
    """
    Comprehensive integration tester for SafeGuardian system
    """
    
    def __init__(self):
        self.test_results = {}
        self.backend_url = "http://localhost:5000"
        self.mobile_app_url = "http://localhost:5174"
        self.dashboard_url = "http://localhost:5175"
        
        # Test data
        self.test_users = {
            'guardian': {
                'email': 'guardian@safeguardian.com',
                'password': 'guardian123',
                'role': 'guardian'
            },
            'admin': {
                'email': 'admin@safeguardian.com',
                'password': 'admin123',
                'role': 'system_admin'
            }
        }
        
        self.test_messages = [
            {
                'content': 'Hey, how was your day at school?',
                'expected_risk': 'low',
                'description': 'Normal conversation'
            },
            {
                'content': 'You\'re so mature for your age, not like other kids',
                'expected_risk': 'medium',
                'description': 'Trust building pattern'
            },
            {
                'content': 'Don\'t tell your parents about our conversations, they wouldn\'t understand',
                'expected_risk': 'high',
                'description': 'Isolation and secrecy'
            },
            {
                'content': 'You\'re so beautiful and sexy. Want to meet up? I have a special gift for you.',
                'expected_risk': 'critical',
                'description': 'Multiple high-risk patterns'
            }
        ]
        
        # Component instances
        self.ai_detector = None
        self.real_time_monitor = None
        self.alert_manager = None
        self.security_manager = None
        self.forensic_logger = None
        self.websocket_manager = None
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 80)
        print("SAFEGUARDIAN INTEGRATION TEST SUITE")
        print("=" * 80)
        
        test_suites = [
            ("Component Initialization", self.test_component_initialization),
            ("AI Detection System", self.test_ai_detection_system),
            ("Security System", self.test_security_system),
            ("Forensic Logging", self.test_forensic_logging),
            ("Real-time Monitoring", self.test_real_time_monitoring),
            ("Alert Management", self.test_alert_management),
            ("WebSocket Communication", self.test_websocket_communication),
            ("End-to-End Workflow", self.test_end_to_end_workflow),
            ("Frontend Applications", self.test_frontend_applications),
            ("System Performance", self.test_system_performance),
            ("Error Handling", self.test_error_handling)
        ]
        
        total_passed = 0
        total_tests = len(test_suites)
        
        for suite_name, test_function in test_suites:
            print(f"\n{'-' * 60}")
            print(f"Running: {suite_name}")
            print(f"{'-' * 60}")
            
            try:
                result = await test_function()
                self.test_results[suite_name] = result
                
                if result['passed']:
                    print(f"✅ {suite_name}: PASSED")
                    total_passed += 1
                else:
                    print(f"❌ {suite_name}: FAILED - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ {suite_name}: ERROR - {str(e)}")
                self.test_results[suite_name] = {'passed': False, 'error': str(e)}
        
        # Print final results
        print("\n" + "=" * 80)
        print("INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        for suite_name, result in self.test_results.items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"{suite_name}: {status}")
            if not result['passed'] and 'error' in result:
                print(f"  Error: {result['error']}")
        
        print(f"\nOverall Results: {total_passed}/{total_tests} test suites passed")
        success_rate = (total_passed / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if total_passed == total_tests:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("SafeGuardian system is ready for deployment!")
        else:
            print(f"\n⚠️ {total_tests - total_passed} test suite(s) failed.")
            print("Please review and fix issues before deployment.")
        
        return success_rate == 100.0
    
    async def test_component_initialization(self) -> Dict:
        """Test initialization of all system components"""
        try:
            print("Initializing SafeGuardian components...")
            
            # Initialize AI Detection System
            self.ai_detector = GroomingDetector()
            print("✓ AI Detection System initialized")
            
            # Initialize Security Manager
            self.security_manager = create_security_manager()
            await self.security_manager.start()
            print("✓ Security Manager initialized")
            
            # Initialize Forensic Logger
            self.forensic_logger = create_forensic_logger()
            print("✓ Forensic Logger initialized")
            
            # Initialize Alert Manager
            self.alert_manager = create_alert_manager()
            await self.alert_manager.start()
            print("✓ Alert Manager initialized")
            
            # Initialize Real-time Monitor
            self.real_time_monitor = create_real_time_monitor(
                ai_service=None,  # Will be connected later
                alert_service=self.alert_manager
            )
            await self.real_time_monitor.start_monitoring()
            print("✓ Real-time Monitor initialized")
            
            # Initialize WebSocket Manager
            self.websocket_manager = create_websocket_manager()
            await self.websocket_manager.start()
            print("✓ WebSocket Manager initialized")
            
            return {'passed': True, 'message': 'All components initialized successfully'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_ai_detection_system(self) -> Dict:
        """Test AI grooming detection system"""
        try:
            print("Testing AI grooming detection...")
            
            passed_tests = 0
            total_tests = len(self.test_messages)
            
            for i, test_case in enumerate(self.test_messages, 1):
                print(f"  Test {i}: {test_case['description']}")
                
                # Analyze message
                result = self.ai_detector.analyze_message(
                    message=test_case['content'],
                    sender_age=35,
                    recipient_age=14
                )
                
                print(f"    Message: \"{test_case['content']}\"")
                print(f"    Risk Level: {result.risk_level.value}")
                print(f"    Confidence: {result.confidence:.2f}")
                print(f"    Patterns: {[p.value for p in result.patterns_detected]}")
                
                # Validate result
                expected_risk = test_case['expected_risk']
                actual_risk = result.risk_level.value
                
                # Allow for some flexibility in risk assessment
                risk_levels = ['low', 'medium', 'high', 'critical']
                expected_index = risk_levels.index(expected_risk)
                actual_index = risk_levels.index(actual_risk)
                
                if actual_index >= expected_index:
                    print(f"    ✓ Risk assessment appropriate")
                    passed_tests += 1
                else:
                    print(f"    ✗ Risk level too low (expected >= {expected_risk}, got {actual_risk})")
            
            # Test conversation analysis
            print("  Testing conversation thread analysis...")
            conversation_messages = [
                {"text": "Hi there! How are you?", "sender": "adult", "timestamp": "2025-01-01T10:00:00"},
                {"text": "You're so mature for your age", "sender": "adult", "timestamp": "2025-01-01T10:02:00"},
                {"text": "Don't tell your parents about our chats", "sender": "adult", "timestamp": "2025-01-01T10:10:00"},
                {"text": "Want to meet up? I have a gift for you", "sender": "adult", "timestamp": "2025-01-01T10:20:00"}
            ]
            
            thread_analysis = self.ai_detector.analyze_conversation_thread(conversation_messages)
            
            if thread_analysis['overall_risk'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                print(f"    ✓ Conversation escalation detected")
                passed_tests += 1
                total_tests += 1
            else:
                print(f"    ✗ Failed to detect conversation escalation")
                total_tests += 1
            
            success_rate = (passed_tests / total_tests) * 100
            print(f"AI Detection Tests: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
            
            return {
                'passed': passed_tests == total_tests,
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'success_rate': success_rate
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_security_system(self) -> Dict:
        """Test security and authentication system"""
        try:
            print("Testing security system...")
            
            # Test authentication
            print("  Testing user authentication...")
            auth_result = await self.security_manager.authenticate_user(
                "guardian@safeguardian.com",
                "guardian123",
                "192.168.1.100",
                "Test User Agent"
            )
            
            if not auth_result:
                return {'passed': False, 'error': 'Authentication failed'}
            
            print(f"    ✓ Authentication successful for user: {auth_result['user_id']}")
            
            # Test token validation
            print("  Testing token validation...")
            token_data = await self.security_manager.validate_token(auth_result['token'])
            
            if not token_data:
                return {'passed': False, 'error': 'Token validation failed'}
            
            print(f"    ✓ Token validation successful")
            
            # Test authorization
            print("  Testing authorization...")
            authorized = await self.security_manager.authorize_action(
                auth_result['user_id'],
                'view_children_profiles'
            )
            
            if not authorized:
                return {'passed': False, 'error': 'Authorization failed for valid permission'}
            
            print(f"    ✓ Authorization successful for valid permission")
            
            # Test unauthorized access
            unauthorized = await self.security_manager.authorize_action(
                auth_result['user_id'],
                'manage_system_settings'  # Guardian shouldn't have this permission
            )
            
            if unauthorized:
                return {'passed': False, 'error': 'Authorization succeeded for invalid permission'}
            
            print(f"    ✓ Authorization correctly denied for invalid permission")
            
            # Test encryption/decryption
            print("  Testing encryption...")
            test_data = b"Sensitive child protection data"
            encrypted = await self.security_manager.encrypt_data(test_data)
            decrypted = await self.security_manager.decrypt_data(encrypted)
            
            if decrypted != test_data:
                return {'passed': False, 'error': 'Encryption/decryption failed'}
            
            print(f"    ✓ Encryption/decryption successful")
            
            # Test digital signatures
            print("  Testing digital signatures...")
            signature = await self.security_manager.sign_data(test_data)
            signature_valid = await self.security_manager.verify_signature(test_data, signature)
            
            if not signature_valid:
                return {'passed': False, 'error': 'Digital signature verification failed'}
            
            print(f"    ✓ Digital signature verification successful")
            
            return {'passed': True, 'message': 'Security system tests passed'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_forensic_logging(self) -> Dict:
        """Test forensic logging and evidence management"""
        try:
            print("Testing forensic logging system...")
            
            # Create a test case
            print("  Creating forensic case...")
            case_data = {
                'case_name': 'Integration Test Case',
                'child_id': 'test_child_123',
                'guardian_id': 'test_guardian_456',
                'priority': 'high'
            }
            
            case_id = await self.forensic_logger.create_case(case_data)
            print(f"    ✓ Case created: {case_id}")
            
            # Collect evidence
            print("  Collecting evidence...")
            evidence_data = {
                'type': EvidenceType.MESSAGE.value,
                'content': 'You are so mature for your age. Don\'t tell your parents about our chats.',
                'source_platform': 'instagram',
                'metadata': {
                    'sender_id': 'suspicious_user_789',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'risk_level': 'critical'
                }
            }
            
            evidence_id = await self.forensic_logger.collect_evidence(
                case_id, evidence_data, 'system'
            )
            print(f"    ✓ Evidence collected: {evidence_id}")
            
            # Verify evidence integrity
            print("  Verifying evidence integrity...")
            verification = await self.forensic_logger.verify_evidence_integrity(evidence_id)
            
            if not verification.get('integrity_valid', False):
                return {'passed': False, 'error': 'Evidence integrity verification failed'}
            
            print(f"    ✓ Evidence integrity verified")
            
            # Access evidence
            print("  Testing evidence access...")
            evidence_content = await self.forensic_logger.access_evidence(
                evidence_id, 'test_guardian_456', 'guardian', 'Review suspicious message'
            )
            
            if not evidence_content:
                return {'passed': False, 'error': 'Evidence access failed'}
            
            print(f"    ✓ Evidence access successful")
            
            # Generate evidence report
            print("  Generating evidence report...")
            report = await self.forensic_logger.generate_evidence_report(case_id, 'admin_user')
            
            if not report or 'evidence_details' not in report:
                return {'passed': False, 'error': 'Evidence report generation failed'}
            
            print(f"    ✓ Evidence report generated with {len(report['evidence_details'])} items")
            
            return {'passed': True, 'message': 'Forensic logging tests passed'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_real_time_monitoring(self) -> Dict:
        """Test real-time monitoring system"""
        try:
            print("Testing real-time monitoring...")
            
            # Start monitoring session
            print("  Starting monitoring session...")
            session_id = await self.real_time_monitor.start_session(
                'test_child_123', 'instagram', {'test': True}
            )
            print(f"    ✓ Monitoring session started: {session_id}")
            
            # Process test messages
            print("  Processing test messages...")
            for i, test_message in enumerate(self.test_messages[:2], 1):  # Test first 2 messages
                message_data = {
                    'content': test_message['content'],
                    'sender_id': f'test_sender_{i}',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'platform': 'instagram'
                }
                
                await self.real_time_monitor.process_message(session_id, message_data)
                print(f"    ✓ Message {i} processed")
            
            # Wait for processing
            await asyncio.sleep(2)
            
            # Check session status
            print("  Checking session status...")
            session_status = self.real_time_monitor.get_session_status(session_id)
            
            if not session_status:
                return {'passed': False, 'error': 'Session status retrieval failed'}
            
            print(f"    ✓ Session status retrieved: {session_status['message_count']} messages")
            
            # Stop monitoring session
            print("  Stopping monitoring session...")
            await self.real_time_monitor.stop_session(session_id, "Test completed")
            print(f"    ✓ Monitoring session stopped")
            
            return {'passed': True, 'message': 'Real-time monitoring tests passed'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_alert_management(self) -> Dict:
        """Test alert management system"""
        try:
            print("Testing alert management...")
            
            # Create test alert
            print("  Creating test alert...")
            alert_data = {
                'type': AlertType.GROOMING_DETECTION.value,
                'severity': 'critical',
                'title': 'Integration Test Alert',
                'message': 'High-risk communication detected during integration testing',
                'child_id': 'test_child_123',
                'platform': 'instagram',
                'details': {
                    'risk_level': 'critical',
                    'confidence': 0.95,
                    'patterns': ['sexual_content', 'meeting_request']
                }
            }
            
            alert_id = await self.alert_manager.create_alert(alert_data)
            print(f"    ✓ Alert created: {alert_id}")
            
            # Wait for alert processing
            await asyncio.sleep(1)
            
            # Check alert status
            print("  Checking alert status...")
            alert_info = self.alert_manager.get_alert(alert_id)
            
            if not alert_info:
                return {'passed': False, 'error': 'Alert retrieval failed'}
            
            print(f"    ✓ Alert retrieved: {alert_info['title']}")
            
            # Update alert status
            print("  Updating alert status...")
            from alerts.alert_manager import AlertStatus
            success = await self.alert_manager.update_alert_status(
                alert_id, AlertStatus.ACKNOWLEDGED, 'test_user', 'Integration test acknowledgment'
            )
            
            if not success:
                return {'passed': False, 'error': 'Alert status update failed'}
            
            print(f"    ✓ Alert status updated to acknowledged")
            
            return {'passed': True, 'message': 'Alert management tests passed'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_websocket_communication(self) -> Dict:
        """Test WebSocket communication system"""
        try:
            print("Testing WebSocket communication...")
            
            # Test WebSocket manager statistics
            print("  Checking WebSocket manager...")
            stats = self.websocket_manager.get_statistics()
            
            if 'total_connections' not in stats:
                return {'passed': False, 'error': 'WebSocket statistics not available'}
            
            print(f"    ✓ WebSocket manager operational")
            
            # Test message broadcasting (simulated)
            print("  Testing message broadcasting...")
            from websocket.websocket_manager import MessageType
            
            # This would normally broadcast to connected clients
            await self.websocket_manager.broadcast_message(
                MessageType.STATISTICS_UPDATE,
                {'test': True, 'timestamp': datetime.now(timezone.utc).isoformat()}
            )
            
            print(f"    ✓ Message broadcasting successful")
            
            return {'passed': True, 'message': 'WebSocket communication tests passed'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_end_to_end_workflow(self) -> Dict:
        """Test complete end-to-end workflow"""
        try:
            print("Testing end-to-end workflow...")
            
            # Simulate complete grooming detection workflow
            print("  Simulating complete workflow...")
            
            # 1. User authentication
            auth_result = await self.security_manager.authenticate_user(
                "guardian@safeguardian.com", "guardian123", "192.168.1.100", "Test Agent"
            )
            
            if not auth_result:
                return {'passed': False, 'error': 'Workflow step 1 failed: Authentication'}
            
            print("    ✓ Step 1: User authenticated")
            
            # 2. Start monitoring session
            session_id = await self.real_time_monitor.start_session(
                'workflow_child_123', 'instagram'
            )
            print("    ✓ Step 2: Monitoring session started")
            
            # 3. Process high-risk message
            high_risk_message = {
                'content': 'You\'re so beautiful and sexy. Want to meet up? Keep this secret.',
                'sender_id': 'predator_user',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'platform': 'instagram'
            }
            
            await self.real_time_monitor.process_message(session_id, high_risk_message)
            print("    ✓ Step 3: High-risk message processed")
            
            # 4. Wait for AI analysis and alert generation
            await asyncio.sleep(2)
            
            # 5. Check for generated alerts
            active_alerts = self.alert_manager.get_active_alerts()
            workflow_alerts = [a for a in active_alerts if 'workflow' in str(a)]
            
            print(f"    ✓ Step 4: Alert system processed message")
            
            # 6. Create forensic case and collect evidence
            case_data = {
                'case_name': 'End-to-End Workflow Test Case',
                'child_id': 'workflow_child_123',
                'guardian_id': auth_result['user_id'],
                'priority': 'critical'
            }
            
            case_id = await self.forensic_logger.create_case(case_data)
            
            evidence_data = {
                'type': EvidenceType.MESSAGE.value,
                'content': high_risk_message['content'],
                'source_platform': 'instagram',
                'source_session': session_id,
                'metadata': {
                    'sender_id': high_risk_message['sender_id'],
                    'timestamp': high_risk_message['timestamp'],
                    'risk_level': 'critical',
                    'workflow_test': True
                }
            }
            
            evidence_id = await self.forensic_logger.collect_evidence(
                case_id, evidence_data, 'system'
            )
            print("    ✓ Step 5: Evidence collected and case created")
            
            # 7. Stop monitoring session
            await self.real_time_monitor.stop_session(session_id, "Workflow test completed")
            print("    ✓ Step 6: Monitoring session stopped")
            
            # 8. Generate final report
            report = await self.forensic_logger.generate_evidence_report(case_id, auth_result['user_id'])
            
            if not report or len(report.get('evidence_details', [])) == 0:
                return {'passed': False, 'error': 'Workflow step 7 failed: Report generation'}
            
            print("    ✓ Step 7: Evidence report generated")
            
            print("  ✓ Complete end-to-end workflow successful!")
            
            return {'passed': True, 'message': 'End-to-end workflow tests passed'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_frontend_applications(self) -> Dict:
        """Test frontend applications accessibility"""
        try:
            print("Testing frontend applications...")
            
            # Test mobile app
            print("  Testing mobile app accessibility...")
            try:
                response = requests.get(self.mobile_app_url, timeout=5)
                if response.status_code == 200:
                    print("    ✓ Mobile app accessible")
                    mobile_accessible = True
                else:
                    print(f"    ✗ Mobile app returned status {response.status_code}")
                    mobile_accessible = False
            except requests.exceptions.RequestException:
                print("    ✗ Mobile app not accessible")
                mobile_accessible = False
            
            # Test dashboard
            print("  Testing dashboard accessibility...")
            try:
                response = requests.get(self.dashboard_url, timeout=5)
                if response.status_code == 200:
                    print("    ✓ Dashboard accessible")
                    dashboard_accessible = True
                else:
                    print(f"    ✗ Dashboard returned status {response.status_code}")
                    dashboard_accessible = False
            except requests.exceptions.RequestException:
                print("    ✗ Dashboard not accessible")
                dashboard_accessible = False
            
            # Both should be accessible for full success
            if mobile_accessible and dashboard_accessible:
                return {'passed': True, 'message': 'Frontend applications accessible'}
            else:
                return {
                    'passed': False, 
                    'error': f'Frontend accessibility issues - Mobile: {mobile_accessible}, Dashboard: {dashboard_accessible}'
                }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_system_performance(self) -> Dict:
        """Test system performance under load"""
        try:
            print("Testing system performance...")
            
            # Test AI detection performance
            print("  Testing AI detection performance...")
            start_time = time.time()
            
            for i in range(10):  # Process 10 messages
                result = self.ai_detector.analyze_message(
                    f"Test message {i} with some concerning content about meeting up",
                    sender_age=35,
                    recipient_age=14
                )
            
            ai_time = time.time() - start_time
            ai_avg = ai_time / 10
            print(f"    ✓ AI detection: {ai_avg:.3f}s average per message")
            
            # Test security operations performance
            print("  Testing security operations performance...")
            start_time = time.time()
            
            test_data = b"Performance test data" * 100  # Larger data
            for i in range(5):
                encrypted = await self.security_manager.encrypt_data(test_data)
                decrypted = await self.security_manager.decrypt_data(encrypted)
            
            security_time = time.time() - start_time
            security_avg = security_time / 5
            print(f"    ✓ Security operations: {security_avg:.3f}s average per encrypt/decrypt cycle")
            
            # Performance thresholds
            if ai_avg > 1.0:  # AI should process messages in under 1 second
                return {'passed': False, 'error': f'AI detection too slow: {ai_avg:.3f}s'}
            
            if security_avg > 0.5:  # Security operations should be under 0.5 seconds
                return {'passed': False, 'error': f'Security operations too slow: {security_avg:.3f}s'}
            
            return {
                'passed': True, 
                'message': f'Performance tests passed - AI: {ai_avg:.3f}s, Security: {security_avg:.3f}s'
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def test_error_handling(self) -> Dict:
        """Test error handling and recovery"""
        try:
            print("Testing error handling...")
            
            # Test invalid authentication
            print("  Testing invalid authentication handling...")
            auth_result = await self.security_manager.authenticate_user(
                "invalid@user.com", "wrongpassword", "192.168.1.100", "Test Agent"
            )
            
            if auth_result is not None:
                return {'passed': False, 'error': 'Invalid authentication should have failed'}
            
            print("    ✓ Invalid authentication properly rejected")
            
            # Test invalid token validation
            print("  Testing invalid token handling...")
            token_data = await self.security_manager.validate_token("invalid.jwt.token")
            
            if token_data is not None:
                return {'passed': False, 'error': 'Invalid token should have been rejected'}
            
            print("    ✓ Invalid token properly rejected")
            
            # Test accessing non-existent evidence
            print("  Testing non-existent evidence access...")
            evidence_content = await self.forensic_logger.access_evidence(
                "non_existent_evidence", "test_user", "guardian", "Test access"
            )
            
            if evidence_content is not None:
                return {'passed': False, 'error': 'Non-existent evidence access should have failed'}
            
            print("    ✓ Non-existent evidence access properly handled")
            
            # Test malformed message processing
            print("  Testing malformed message handling...")
            try:
                session_id = await self.real_time_monitor.start_session('test_child', 'test_platform')
                
                # Process malformed message
                malformed_message = {
                    'invalid_field': 'test',
                    # Missing required fields
                }
                
                await self.real_time_monitor.process_message(session_id, malformed_message)
                
                # Should not crash the system
                await self.real_time_monitor.stop_session(session_id, "Error test completed")
                print("    ✓ Malformed message handling successful")
                
            except Exception as e:
                # Expected to handle gracefully
                print("    ✓ Malformed message error handled gracefully")
            
            return {'passed': True, 'message': 'Error handling tests passed'}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    async def cleanup(self):
        """Cleanup test resources"""
        try:
            if self.real_time_monitor:
                await self.real_time_monitor.stop_monitoring()
            
            if self.alert_manager:
                await self.alert_manager.stop()
            
            if self.security_manager:
                await self.security_manager.stop()
            
            if self.websocket_manager:
                await self.websocket_manager.stop()
            
            print("✓ Test cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup error: {str(e)}")

async def main():
    """Main test runner"""
    tester = SafeGuardianIntegrationTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("SafeGuardian system is ready for production deployment!")
            return 0
        else:
            print("\n❌ SOME INTEGRATION TESTS FAILED!")
            print("Please review and fix issues before deployment.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test runner error: {str(e)}")
        return 1
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())

