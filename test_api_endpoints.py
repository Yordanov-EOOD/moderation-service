#!/usr/bin/env python3
"""
API Endpoint Test Script
========================

This script tests the moderation service API endpoints directly to isolate
whether issues are in the HTTP layer, JSON handling, or service logic.
"""

import requests
import json
import time
from datetime import datetime

class APITester:
    """Test API endpoints directly"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ToxicityTester/1.0'
        })
        
        # Test cases
        self.test_cases = [
            # Simple clean content
            {"content": "Hello world", "expected": "clean"},
            {"content": "Thank you", "expected": "clean"},
            {"content": "Good morning", "expected": "clean"},
            
            # Simple toxic content  
            {"content": "You are stupid", "expected": "toxic"},
            {"content": "I hate you", "expected": "toxic"},
            {"content": "Go die", "expected": "toxic"},
        ]
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("🏥 Testing Health Endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.3f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Health Check: {data.get('status', 'unknown')}")
                    print(f"🔧 Service: {data.get('service', 'unknown')}")
                    print(f"📦 Version: {data.get('version', 'unknown')}")
                    if 'detector' in data:
                        detector = data['detector']
                        print(f"🤖 Detector: {detector.get('detector_type', 'unknown')}")
                        print(f"🏷️  Model: {detector.get('model_name', 'unknown')}")
                    return True
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    print(f"📄 Raw response: {response.text[:200]}...")
                    return False
            else:
                print(f"❌ Health check failed with status {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check request failed: {e}")
            return False
    
    def test_single_check_endpoint(self):
        """Test the single content check endpoint"""
        print("\n🧪 Testing Single Check Endpoint...")
        
        results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            content = test_case["content"]
            expected = test_case["expected"]
            
            print(f"\n📝 Test {i}: \"{content}\" (expect {expected})")
            
            payload = {"content": content}
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/moderation/check",
                    json=payload,
                    timeout=30
                )
                response_time = time.time() - start_time
                
                print(f"📡 Status: {response.status_code}")
                print(f"⏱️  Time: {response_time:.3f}s")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        is_toxic = data.get('toxic', False)
                        toxicity_score = data.get('toxicity_score', 0.0)
                        confidence = data.get('confidence', 0.0)
                        
                        result_status = "toxic" if is_toxic else "clean"
                        is_correct = (
                            (expected == "clean" and not is_toxic) or
                            (expected == "toxic" and is_toxic)
                        )
                        
                        status_icon = "✅" if is_correct else "❌"
                        print(f"📊 Result: {result_status.upper()} {status_icon}")
                        print(f"📈 Score: {toxicity_score:.4f}")
                        print(f"🎲 Confidence: {confidence:.4f}")
                        
                        if 'categories' in data:
                            print(f"🏷️  Categories: {data['categories']}")
                        
                        results.append({
                            "content": content,
                            "expected": expected,
                            "actual": result_status,
                            "is_correct": is_correct,
                            "toxicity_score": toxicity_score,
                            "confidence": confidence,
                            "response_time": response_time,
                            "full_response": data
                        })
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON: {e}")
                        print(f"📄 Raw response: {response.text[:200]}...")
                        results.append({
                            "content": content,
                            "expected": expected,
                            "error": "Invalid JSON response",
                            "is_correct": False
                        })
                        
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    print(f"📄 Response: {response.text[:200]}...")
                    results.append({
                        "content": content,
                        "expected": expected,
                        "error": f"HTTP {response.status_code}",
                        "is_correct": False
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}")
                results.append({
                    "content": content,
                    "expected": expected,
                    "error": str(e),
                    "is_correct": False
                })
        
        return results
    
    def test_batch_endpoint(self):
        """Test the batch processing endpoint"""
        print("\n📦 Testing Batch Endpoint...")
        
        # Prepare batch payload
        contents = [{"content": case["content"]} for case in self.test_cases[:3]]
        payload = {"contents": contents}
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/moderation/batch",
                json=payload,
                timeout=60
            )
            response_time = time.time() - start_time
            
            print(f"📡 Status: {response.status_code}")
            print(f"⏱️  Time: {response_time:.3f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results = data.get('results', [])
                    
                    print(f"📊 Processed: {len(results)} items")
                    
                    for i, result in enumerate(results):
                        content = result.get('content', 'unknown')[:30]
                        is_toxic = result.get('toxic', False)
                        score = result.get('toxicity_score', 0.0)
                        status = "TOXIC" if is_toxic else "CLEAN"
                        print(f"  {i+1}. \"{content}...\" → {status} ({score:.3f})")
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {e}")
                    return False
            else:
                print(f"❌ Batch request failed: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Batch request error: {e}")
            return False
    
    def test_invalid_requests(self):
        """Test invalid request handling"""
        print("\n🚫 Testing Invalid Requests...")
        
        invalid_tests = [
            {"name": "Empty content", "payload": {"content": ""}},
            {"name": "Missing content", "payload": {}},
            {"name": "Invalid JSON", "payload": "invalid json", "raw": True},
            {"name": "Wrong content type", "payload": {"content": 123}},
        ]
        
        for test in invalid_tests:
            print(f"\n🧪 Testing: {test['name']}")
            
            try:
                if test.get('raw'):
                    # Send raw string instead of JSON
                    response = self.session.post(
                        f"{self.base_url}/api/moderation/check",
                        data=test['payload'],
                        headers={'Content-Type': 'text/plain'},
                        timeout=10
                    )
                else:
                    response = self.session.post(
                        f"{self.base_url}/api/moderation/check",
                        json=test['payload'],
                        timeout=10
                    )
                
                print(f"📡 Status: {response.status_code}")
                
                if response.status_code >= 400:
                    print("✅ Correctly rejected invalid request")
                    try:
                        error_data = response.json()
                        print(f"📄 Error: {error_data.get('message', 'No message')}")
                    except:
                        print(f"📄 Response: {response.text[:100]}...")
                else:
                    print("❌ Should have rejected invalid request")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}")
    
    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Test...")
        print("=" * 80)
        
        # Test 1: Health check
        health_ok = self.test_health_endpoint()
        
        if not health_ok:
            print("\n❌ Health check failed - service may not be running")
            print("💡 Make sure the moderation service is running on", self.base_url)
            return False
        
        # Test 2: Single check endpoint
        single_results = self.test_single_check_endpoint()
        
        # Test 3: Batch endpoint
        batch_ok = self.test_batch_endpoint()
        
        # Test 4: Invalid requests
        self.test_invalid_requests()
        
        # Summary
        print("\n" + "=" * 80)
        print("📈 API TEST SUMMARY")
        print("=" * 80)
        
        if single_results:
            correct = sum(1 for r in single_results if r.get('is_correct', False))
            total = len(single_results)
            accuracy = correct / total if total > 0 else 0
            
            print(f"✅ Health Check: {'PASS' if health_ok else 'FAIL'}")
            print(f"🧪 Single Check: {correct}/{total} correct ({accuracy:.1%})")
            print(f"📦 Batch Check: {'PASS' if batch_ok else 'FAIL'}")
            
            # Show problematic results
            problems = [r for r in single_results if not r.get('is_correct', False)]
            if problems:
                print(f"\n❌ Issues found:")
                for p in problems:
                    error = p.get('error', 'Incorrect prediction')
                    print(f"   • \"{p['content']}\": {error}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"api_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "timestamp": timestamp,
                    "base_url": self.base_url,
                    "health_check": health_ok,
                    "batch_check": batch_ok,
                    "single_check_results": single_results
                }
            }, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        return health_ok and batch_ok and (accuracy > 0.5 if single_results else False)

def main():
    """Main execution"""
    print("🌐 Starting API Endpoint Test...")
    
    # Allow custom URL
    import sys
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    try:
        tester = APITester(base_url)
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n✅ API tests completed successfully!")
        else:
            print("\n❌ API tests found issues!")
        
        return success
        
    except Exception as e:
        print(f"\n❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
