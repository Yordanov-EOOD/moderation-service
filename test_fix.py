#!/usr/bin/env python3
"""
Quick test to validate the toxicity calculation fix
"""
import requests
import json

def test_toxicity_fix():
    """Test if the toxicity calculations are now correct"""
    base_url = "http://localhost:5000"
    
    test_cases = [
        {
            "content": "What a beautiful day! I love this sunshine.",
            "expected_toxic": False,
            "description": "Positive content (should be non-toxic)"
        },
        {
            "content": "I love spending time with my friends!",
            "expected_toxic": False,
            "description": "Positive content (should be non-toxic)"
        },
        {
            "content": "You're such an amazing person",
            "expected_toxic": False,
            "description": "Compliment (should be non-toxic)"
        },
        {
            "content": "You are an idiot and I hate your opinion",
            "expected_toxic": True,
            "description": "Insulting language (should be toxic)"
        },
        {
            "content": "Go kill yourself, nobody likes you",
            "expected_toxic": True,
            "description": "Severe toxicity (should be toxic)"
        }
    ]
    
    print("🧪 Testing Toxicity Calculation Fix")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        try:
            payload = {
                "content": test["content"],
                "yeet_id": f"test_{i}",
                "user_id": "test_user"
            }
            
            response = requests.post(
                f"{base_url}/api/moderation/check",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                is_toxic = data['is_toxic']
                score = data['toxicity_score']
                
                # Check if result matches expectation
                if is_toxic == test["expected_toxic"]:
                    status = "✅ CORRECT"
                    color = "🟢"
                else:
                    status = "❌ INCORRECT"
                    color = "🔴"
                
                print(f"\n{i}. {test['description']}")
                print(f"   Content: \"{test['content']}\"")
                print(f"   Result: {color} {status}")
                print(f"   Toxic: {is_toxic} | Score: {score:.3f}")
                
            else:
                print(f"\n{i}. ❌ HTTP Error {response.status_code}")
                print(f"   Content: \"{test['content']}\"")
                
        except Exception as e:
            print(f"\n{i}. ❌ Error: {e}")
            print(f"   Content: \"{test['content']}\"")
    
    print("\n" + "=" * 50)
    print("Test completed! Please restart the service and run this test again.")

if __name__ == "__main__":
    test_toxicity_fix()
