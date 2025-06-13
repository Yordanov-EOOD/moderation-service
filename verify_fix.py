#!/usr/bin/env python3
"""
Quick test to verify the toxicity calculation fix
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_fixed_calculations():
    """Test that the calculations are now correct"""
    print("🧪 Testing Fixed Toxicity Calculations")
    print("=" * 50)
    
    test_cases = [
        {
            "content": "What a beautiful day! I love this sunshine.",
            "expected": "clean",
            "description": "Positive content"
        },
        {
            "content": "I love spending time with my friends!",
            "expected": "clean", 
            "description": "Another positive content"
        },
        {
            "content": "You are an idiot and I hate you",
            "expected": "toxic",
            "description": "Clearly toxic content"
        },
        {
            "content": "Go kill yourself, nobody likes you",
            "expected": "toxic",
            "description": "Very toxic content"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test['description']}")
        print(f"Content: \"{test['content']}\"")
        
        try:
            payload = {
                "content": test["content"],
                "yeet_id": f"test_{i}",
                "user_id": "test_user"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/moderation/check",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                is_toxic = result['is_toxic']
                score = result['toxicity_score']
                confidence = result['confidence']
                
                # Check if result matches expectation
                expected_toxic = test["expected"] == "toxic"
                correct = is_toxic == expected_toxic
                
                status_emoji = "✅" if correct else "❌"
                toxicity_emoji = "🚨" if is_toxic else "✅"
                
                print(f"{status_emoji} Result: {toxicity_emoji} {'TOXIC' if is_toxic else 'CLEAN'}")
                print(f"   Score: {score:.3f}")
                print(f"   Confidence: {confidence:.3f}")
                print(f"   Expected: {test['expected'].upper()}")
                
                if not correct:
                    print(f"   ⚠️  INCORRECT RESULT!")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    print(f"\n{'=' * 50}")
    print("🏁 Test completed! Please restart the service to apply fixes.")

if __name__ == "__main__":
    test_fixed_calculations()
