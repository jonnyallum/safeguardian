#!/usr/bin/env python3
"""
Test script for SafeGuardian AI Grooming Detection System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.grooming_detector import GroomingDetector, RiskLevel
from ai.analysis_service import quick_message_analysis
import asyncio
import json

def test_grooming_detector():
    """Test the core grooming detection functionality"""
    print("=" * 60)
    print("SAFEGUARDIAN AI GROOMING DETECTION SYSTEM TEST")
    print("=" * 60)
    
    detector = GroomingDetector()
    
    # Test cases with different risk levels
    test_cases = [
        {
            "message": "Hey, how was your day at school?",
            "expected_risk": RiskLevel.LOW,
            "description": "Normal conversation"
        },
        {
            "message": "You're so mature for your age, not like other kids your age",
            "expected_risk": RiskLevel.MEDIUM,
            "description": "Trust building pattern"
        },
        {
            "message": "Don't tell your parents about our conversations, they wouldn't understand you like I do",
            "expected_risk": RiskLevel.HIGH,
            "description": "Isolation and secrecy patterns"
        },
        {
            "message": "You're so beautiful and sexy. Want to meet up? I have a special gift for you. Keep this between us.",
            "expected_risk": RiskLevel.CRITICAL,
            "description": "Multiple high-risk patterns"
        },
        {
            "message": "Where do you live? When are your parents not home? I want to see you alone.",
            "expected_risk": RiskLevel.CRITICAL,
            "description": "Personal info request and meeting request"
        }
    ]
    
    print(f"\nTesting {len(test_cases)} scenarios...\n")
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Message: \"{test_case['message']}\"")
        
        # Analyze message
        result = detector.analyze_message(
            message=test_case['message'],
            sender_age=35,
            recipient_age=14
        )
        
        print(f"Risk Level: {result.risk_level.value.upper()}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Patterns: {[p.value for p in result.patterns_detected]}")
        print(f"Explanation: {result.explanation}")
        
        # Check if result matches expected risk level
        risk_levels_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        expected_index = risk_levels_order.index(test_case['expected_risk'])
        actual_index = risk_levels_order.index(result.risk_level)
        
        # Allow for some flexibility in risk assessment
        if actual_index >= expected_index:
            print("✅ PASS - Risk level appropriate")
            passed_tests += 1
        else:
            print("❌ FAIL - Risk level too low")
        
        print("-" * 50)
    
    print(f"\nTest Results: {passed_tests}/{total_tests} tests passed")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    return passed_tests == total_tests

def test_conversation_analysis():
    """Test conversation thread analysis"""
    print("\n" + "=" * 60)
    print("CONVERSATION THREAD ANALYSIS TEST")
    print("=" * 60)
    
    detector = GroomingDetector()
    
    # Simulated conversation showing escalation
    conversation_messages = [
        {"text": "Hi there! How are you doing?", "sender": "adult", "timestamp": "2025-01-01T10:00:00"},
        {"text": "I'm good, just finished school", "sender": "child", "timestamp": "2025-01-01T10:01:00"},
        {"text": "You seem really smart and mature for your age", "sender": "adult", "timestamp": "2025-01-01T10:02:00"},
        {"text": "Thanks! My friends say that too", "sender": "child", "timestamp": "2025-01-01T10:03:00"},
        {"text": "I bet they don't understand you like I do. You're special.", "sender": "adult", "timestamp": "2025-01-01T10:05:00"},
        {"text": "Yeah, sometimes I feel different", "sender": "child", "timestamp": "2025-01-01T10:06:00"},
        {"text": "Don't tell your parents about our chats. They might not understand our friendship.", "sender": "adult", "timestamp": "2025-01-01T10:10:00"},
        {"text": "Okay, I won't tell them", "sender": "child", "timestamp": "2025-01-01T10:11:00"},
        {"text": "You're so beautiful. Have you ever been curious about your body?", "sender": "adult", "timestamp": "2025-01-01T10:15:00"},
        {"text": "That's a weird question...", "sender": "child", "timestamp": "2025-01-01T10:16:00"},
        {"text": "Want to meet up? I have a special gift for you. Just between us.", "sender": "adult", "timestamp": "2025-01-01T10:20:00"}
    ]
    
    print(f"Analyzing conversation with {len(conversation_messages)} messages...")
    
    # Analyze the conversation thread
    thread_analysis = detector.analyze_conversation_thread(conversation_messages)
    
    print(f"\nThread Analysis Results:")
    print(f"Overall Risk: {thread_analysis['overall_risk'].value.upper()}")
    print(f"Confidence: {thread_analysis['confidence']:.2f}")
    print(f"Escalation Detected: {thread_analysis['escalation_detected']}")
    print(f"Summary: {thread_analysis['summary']}")
    print(f"Recommendations: {thread_analysis['recommendations'][:3]}")  # Show first 3
    
    # Check if high risk was detected
    if thread_analysis['overall_risk'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        print("✅ PASS - High risk conversation correctly identified")
        return True
    else:
        print("❌ FAIL - High risk conversation not detected")
        return False

async def test_analysis_service():
    """Test the analysis service"""
    print("\n" + "=" * 60)
    print("ANALYSIS SERVICE TEST")
    print("=" * 60)
    
    # Test quick analysis
    test_message = "You're so mature for your age. Don't tell anyone about our special friendship."
    
    print(f"Testing message: \"{test_message}\"")
    
    result = await quick_message_analysis(
        message_text=test_message,
        sender_age=35,
        recipient_age=14
    )
    
    print(f"Service Analysis Result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Check if analysis was successful
    if 'error' not in result and result.get('risk_level') in ['medium', 'high', 'critical']:
        print("✅ PASS - Analysis service working correctly")
        return True
    else:
        print("❌ FAIL - Analysis service error or incorrect result")
        return False

def test_pattern_detection():
    """Test specific pattern detection"""
    print("\n" + "=" * 60)
    print("PATTERN DETECTION TEST")
    print("=" * 60)
    
    detector = GroomingDetector()
    
    pattern_tests = [
        {
            "message": "You can trust me with anything, I understand you",
            "expected_patterns": ["trust_building"],
            "description": "Trust building detection"
        },
        {
            "message": "Don't tell your parents, keep this our secret",
            "expected_patterns": ["isolation", "secrecy"],
            "description": "Isolation and secrecy detection"
        },
        {
            "message": "You're so sexy and beautiful, want to see you",
            "expected_patterns": ["sexual_content"],
            "description": "Sexual content detection"
        },
        {
            "message": "Want to meet up? Come to my place",
            "expected_patterns": ["meeting_request"],
            "description": "Meeting request detection"
        }
    ]
    
    passed_pattern_tests = 0
    
    for test in pattern_tests:
        print(f"\nTesting: {test['description']}")
        print(f"Message: \"{test['message']}\"")
        
        result = detector.analyze_message(test['message'])
        detected_patterns = [p.value for p in result.patterns_detected]
        
        print(f"Detected patterns: {detected_patterns}")
        print(f"Expected patterns: {test['expected_patterns']}")
        
        # Check if at least one expected pattern was detected
        if any(pattern in detected_patterns for pattern in test['expected_patterns']):
            print("✅ PASS - Expected pattern detected")
            passed_pattern_tests += 1
        else:
            print("❌ FAIL - Expected pattern not detected")
    
    print(f"\nPattern Detection Results: {passed_pattern_tests}/{len(pattern_tests)} tests passed")
    return passed_pattern_tests == len(pattern_tests)

def main():
    """Run all tests"""
    print("Starting SafeGuardian AI System Tests...")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Grooming Detector", test_grooming_detector()))
    test_results.append(("Conversation Analysis", test_conversation_analysis()))
    test_results.append(("Pattern Detection", test_pattern_detection()))
    
    # Run async test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    analysis_service_result = loop.run_until_complete(test_analysis_service())
    loop.close()
    test_results.append(("Analysis Service", analysis_service_result))
    
    # Print final results
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} test suites passed")
    print(f"System Status: {'✅ READY FOR DEPLOYMENT' if passed_tests == total_tests else '❌ NEEDS ATTENTION'}")
    
    if passed_tests == total_tests:
        print("\n🛡️ SafeGuardian AI System is fully operational and ready to protect children!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test suite(s) failed. Please review and fix issues.")

if __name__ == "__main__":
    main()

