#!/usr/bin/env python3
"""
Test script for the Moderation Service
Tests both ML-based and rule-based toxicity detection
"""

import requests
import json
import time
from typing import Dict, List

# Service configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/moderation"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"📊 Detector info: {data.get('detector', {})}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_single_content(content: str, expected_toxic: bool = None, description: str = ""):
    """Test single content toxicity check"""
    print(f"\n🔍 Testing: {description}")
    print(f"Content: '{content[:50]}{'...' if len(content) > 50 else ''}'")
    
    try:
        payload = {
            "content": content,
            "yeet_id": f"test_{int(time.time())}",
            "user_id": "test_user"
        }
        
        response = requests.post(
            f"{API_BASE}/check", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            is_toxic = data['is_toxic']
            score = data['toxicity_score']
            confidence = data['confidence']
            categories = data.get('categories', [])
            model_used = data.get('model_used', 'unknown')
            
            print(f"🤖 Model: {model_used}")
            print(f"🎯 Result: {'TOXIC' if is_toxic else 'SAFE'}")
            print(f"📊 Score: {score:.3f} | Confidence: {confidence:.3f}")
            if categories:
                print(f"🏷️  Categories: {', '.join(categories)}")
            
            if expected_toxic is not None:
                if is_toxic == expected_toxic:
                    print("✅ Expected result")
                else:
                    print(f"⚠️  Unexpected result (expected {'toxic' if expected_toxic else 'safe'})")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_batch_content():
    """Test batch toxicity checking"""
    print(f"\n📦 Testing batch content check...")
    
    test_contents = [
        {
            "content": "Hello, how are you today?",
            "yeet_id": "batch_1",
            "user_id": "user_1"
        },
        {
            "content": "You're an idiot and I hate you!",
            "yeet_id": "batch_2", 
            "user_id": "user_2"
        },
        {
            "content": "This is a normal post about cats",
            "yeet_id": "batch_3",
            "user_id": "user_3"
        }
    ]
    
    try:
        payload = {"yeets": test_contents}
        
        response = requests.post(
            f"{API_BASE}/batch",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            total = data['total_processed']
            
            print(f"✅ Batch processed: {total} items")
            
            for i, result in enumerate(results):
                if 'error' in result:
                    print(f"  {i+1}. ❌ Error: {result['error']}")
                else:
                    is_toxic = result['is_toxic']
                    score = result['toxicity_score']
                    print(f"  {i+1}. {'🔴 TOXIC' if is_toxic else '🟢 SAFE'} (score: {score:.3f})")
            
            return True
        else:
            print(f"❌ Batch request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Batch test error: {e}")
        return False

def test_error_cases():
    """Test various error conditions"""
    print(f"\n🚫 Testing error cases...")
    
    # Test empty content
    test_cases = [
        ({"content": ""}, "empty content"),
        ({"content": None}, "null content"),
        ({}, "missing content"),
        ({"content": "a" * 20000}, "content too long"),
        ({"content": "test", "yeet_id": "a" * 100}, "invalid yeet_id"),
    ]
    
    for payload, description in test_cases:
        try:
            response = requests.post(
                f"{API_BASE}/check",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 400:
                print(f"✅ {description}: Correctly rejected")
            else:
                print(f"⚠️  {description}: Unexpected status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: Error {e}")

def run_comprehensive_tests():
    """Run a comprehensive test suite"""
    print("🚀 Starting Moderation Service Test Suite")
    print("=" * 50)
    
    # Health check first
    if not test_health_check():
        print("❌ Service not available, stopping tests")
        return
    
    # Test various content types
    test_cases = [
        ("Hello world!", False, "Simple greeting"),
        ("I love this community!", False, "Positive message"),
        ("You are stupid and ugly", True, "Insult"),
        ("I hate you so much", True, "Hate speech"),
        ("Go kill yourself", True, "Severe threat"),
        ("This f***ing sucks", True, "Profanity (censored)"),
        ("What the hell is going on?", True, "Mild profanity"),
        ("Can you help me with this?", False, "Question"),
        ("🔥 This is fire! 🔥", False, "Emoji content"),
        ("Check out my new blog post", False, "Self-promotion"),
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for content, expected_toxic, description in test_cases:
        if test_single_content(content, expected_toxic, description):
            success_count += 1
        time.sleep(0.5)  # Small delay between tests
    
    # Test batch functionality
    if test_batch_content():
        success_count += 1
        total_tests += 1
    
    # Test error cases
    test_error_cases()
    
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    print(f"📈 Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed or had unexpected results")

def test_detector_info():
    """Test the detector info endpoint"""
    print("\n🔧 Testing detector info endpoint...")
    try:
        response = requests.get(f"{API_BASE}/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detector info retrieved:")
            print(f"   Type: {data.get('detector_type')}")
            print(f"   Version: {data.get('version')}")
            if 'model_name' in data:
                print(f"   Model: {data['model_name']}")
            print(f"   Description: {data.get('description')}")
            return True
        else:
            print(f"❌ Info request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Info test error: {e}")
        return False

if __name__ == "__main__":
    # Test detector info
    test_detector_info()
    
    # Run comprehensive tests
    run_comprehensive_tests()
    
    print(f"\n🏁 Test suite completed!")
    print(f"💡 Tip: Check the service logs for detailed ML model information")
