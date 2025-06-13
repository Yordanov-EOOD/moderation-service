#!/usr/bin/env python3
"""
Test script to verify the custom toxicity model is working correctly
"""

import os
import sys
import logging

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.toxicity_detector import ToxicityDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_custom_model():
    """Test the custom toxicity model"""
    
    # Set environment variables for the custom model
    os.environ['MODEL_NAME'] = 'toxicity-model-final'
    os.environ['MODEL_CACHE_DIR'] = './models'
    os.environ['USE_GPU'] = 'false'
    
    print("=" * 60)
    print("Testing Custom Toxicity Model: toxicity-model-final")
    print("=" * 60)
    
    try:
        # Initialize the detector
        print("\n1. Initializing ToxicityDetector...")
        detector = ToxicityDetector(use_ml_model=True)
        
        print(f"   ✓ Model type: {'ML-based' if detector.use_ml_model else 'Rule-based'}")
        
        # Test cases
        test_cases = [
            "Hello there, how are you doing today?",
            "I love this new feature!",
            "This is absolutely terrible and stupid",
            "You're an idiot and should go die",
            "Great job on the project!"
        ]
        
        print("\n2. Testing toxicity detection...")
        print("-" * 40)
        
        for i, text in enumerate(test_cases, 1):
            try:
                result = detector.check_toxicity(text)
                status = "🔴 TOXIC" if result['is_toxic'] else "🟢 SAFE"
                score = result['toxicity_score']
                
                print(f"{i}. {status} (Score: {score:.3f})")
                print(f"   Text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
                print(f"   Confidence: {result['confidence']:.3f}")
                print(f"   Categories: {result['categories']}")
                print()
                
            except Exception as e:
                print(f"{i}. ❌ ERROR: {str(e)}")
                print(f"   Text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
                print()
        
        print("=" * 60)
        print("✓ Custom model test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print("\nPossible issues:")
        print("- Custom model 'toxicity-model-final' not found")
        print("- Missing model files in ./models directory")
        print("- Network connectivity issues (if model needs to be downloaded)")
        print("- Missing dependencies")
        return False

def test_fallback():
    """Test rule-based fallback"""
    print("\n" + "=" * 60)
    print("Testing Rule-based Fallback")
    print("=" * 60)
    
    try:
        # Initialize with ML disabled to force rule-based
        detector = ToxicityDetector(use_ml_model=False)
        
        print(f"   ✓ Model type: {'ML-based' if detector.use_ml_model else 'Rule-based'}")
        
        test_cases = [
            "Hello there, how are you doing today?",
            "This is fucking terrible",
            "You're such an idiot",
            "Great work!"
        ]
        
        print("\nTesting rule-based detection...")
        for i, text in enumerate(test_cases, 1):
            result = detector.check_toxicity(text)
            status = "🔴 TOXIC" if result['is_toxic'] else "🟢 SAFE"
            print(f"{i}. {status} - \"{text}\"")
        
        print("✓ Rule-based fallback working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error in rule-based test: {str(e)}")
        return False

if __name__ == "__main__":
    print("Custom Toxicity Model Test Suite")
    print("This script tests your custom 'toxicity-model-final' model")
    
    # Test custom model
    model_success = test_custom_model()
    
    # Test fallback
    fallback_success = test_fallback()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Custom Model Test: {'✓ PASSED' if model_success else '❌ FAILED'}")
    print(f"Fallback Test: {'✓ PASSED' if fallback_success else '❌ FAILED'}")
    
    if not model_success:
        print("\nTo use your custom model:")
        print("1. Ensure 'toxicity-model-final' is available in your models directory")
        print("2. Or update MODEL_NAME in .env to point to the correct model path")
        print("3. Make sure all dependencies are installed: pip install -r requirements.txt")
    
    sys.exit(0 if model_success and fallback_success else 1)
