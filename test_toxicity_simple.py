#!/usr/bin/env python3
"""
Simple test script to validate toxicity detection logic
Tests the model directly without Docker to isolate issues
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.toxicity_detector import ToxicityDetector

def test_messages():
    """Test various messages to validate detection logic"""
    
    # Test cases with expected results
    test_cases = [
        # Clean content (should be non-toxic)
        {"content": "What a beautiful day! I love this sunshine.", "expected": False, "category": "✅ Positive"},
        {"content": "Thank you for the helpful feedback!", "expected": False, "category": "✅ Grateful"},
        {"content": "This is a normal technical discussion.", "expected": False, "category": "😐 Neutral"},
        {"content": "I disagree but respect your opinion.", "expected": False, "category": "😐 Respectful"},
        {"content": "The weather forecast shows rain.", "expected": False, "category": "😐 Factual"},
        
        # Mildly negative (borderline)
        {"content": "This is annoying and frustrating.", "expected": False, "category": "⚠️ Mild negative"},
        {"content": "That's really disappointing.", "expected": False, "category": "⚠️ Disappointed"},
        
        # Clearly toxic content (should be toxic)
        {"content": "You're a complete idiot.", "expected": True, "category": "🚨 Insult"},
        {"content": "Go kill yourself, nobody likes you.", "expected": True, "category": "🚨 Severe threat"},
        {"content": "You are so stupid and ugly.", "expected": True, "category": "🚨 Multiple insults"},
        {"content": "F**k this s**t, you're all morons.", "expected": True, "category": "🚨 Profanity + insult"},
        {"content": "I hate you so much, you should die.", "expected": True, "category": "🚨 Hate speech + threat"},
        {"content": "You're worthless trash and everyone knows it.", "expected": True, "category": "🚨 Dehumanizing"},
        {"content": "Kill yourself you pathetic loser.", "expected": True, "category": "🚨 Direct threat"},
        {"content": "You're the dumbest person alive.", "expected": True, "category": "🚨 Extreme insult"},
        {"content": "I hope you get cancer and die slowly.", "expected": True, "category": "🚨 Death wish"}
    ]
    
    print("🧪 TOXICITY DETECTION TEST")
    print("=" * 80)
    print(f"{'Category':<20} {'Expected':<10} {'Detected':<10} {'Score':<8} {'Result':<8} {'Content'}")
    print("-" * 80)
    
    # Initialize detector
    try:
        detector = ToxicityDetector(use_ml_model=True)
        print(f"✅ Detector initialized: {detector.get_detector_info()['detector_type']}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        return
    
    # Test each case
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = detector.check_toxicity(test_case["content"])
            
            predicted_toxic = result["is_toxic"]
            expected_toxic = test_case["expected"]
            score = result["toxicity_score"]
            
            # Check if prediction is correct
            is_correct = predicted_toxic == expected_toxic
            if is_correct:
                correct_predictions += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            # Format output
            expected_str = "TOXIC" if expected_toxic else "CLEAN"
            detected_str = "TOXIC" if predicted_toxic else "CLEAN"
            content_preview = test_case["content"][:50] + "..." if len(test_case["content"]) > 50 else test_case["content"]
            
            print(f"{test_case['category']:<20} {expected_str:<10} {detected_str:<10} {score:<8.3f} {status:<8} {content_preview}")
            
            # Show detailed info for failures
            if not is_correct:
                print(f"    💡 Raw logit: {result.get('raw_logit', 'N/A')}, Confidence: {result.get('confidence', 'N/A')}")
                print(f"    💡 Categories: {result.get('categories', [])}")
                print()
                
        except Exception as e:
            print(f"{test_case['category']:<20} {'ERROR':<10} {'ERROR':<10} {'N/A':<8} {'❌ ERR':<8} {test_case['content'][:50]}")
            print(f"    💥 Error: {e}")
    
    # Summary
    print("-" * 80)
    accuracy = (correct_predictions / total_tests) * 100
    print(f"📊 SUMMARY: {correct_predictions}/{total_tests} correct ({accuracy:.1f}% accuracy)")
    
    if accuracy >= 90:
        print("🎉 EXCELLENT! Model performance is very good.")
    elif accuracy >= 75:
        print("👍 GOOD! Model performance is acceptable with room for improvement.")
    elif accuracy >= 50:
        print("⚠️ FAIR! Model needs significant improvement.")
    else:
        print("❌ POOR! Model performance is unacceptable.")
    
    return accuracy

def test_model_raw_output():
    """Test the raw model output to understand what we're getting"""
    print("\n🔬 RAW MODEL OUTPUT TEST")
    print("=" * 50)
    
    try:
        detector = ToxicityDetector(use_ml_model=True)
        
        # Test with a few examples to see raw output
        test_inputs = [
            "I love you",
            "You are stupid", 
            "Go kill yourself"
        ]
        
        for content in test_inputs:
            try:
                # Get raw classifier output
                clean_content = detector._clean_content_for_ml(content)
                raw_result = detector.classifier(clean_content)
                
                print(f"\nInput: '{content}'")
                print(f"Raw classifier output: {raw_result}")
                
                # Process through our logic
                processed_result = detector.check_toxicity(content)
                print(f"Processed result: is_toxic={processed_result['is_toxic']}, score={processed_result['toxicity_score']}")
                
            except Exception as e:
                print(f"Error processing '{content}': {e}")
                
    except Exception as e:
        print(f"Failed to test raw output: {e}")

if __name__ == "__main__":
    print("🚀 Starting Toxicity Detection Tests...")
    print()
    
    # Test 1: Main functionality
    accuracy = test_messages()
    
    # Test 2: Raw model output
    test_model_raw_output()
    
    print("\n🏁 Tests completed!")
