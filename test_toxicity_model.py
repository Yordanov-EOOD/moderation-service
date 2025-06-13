#!/usr/bin/env python3
"""
Simple Toxicity Model Test Script
=================================

This script tests the toxicity detection model directly to determine if issues
are with the model itself or our implementation.
"""

import os
import sys
import json
import torch
import numpy as np
from typing import Dict, List
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    from scipy.special import expit
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("❌ Transformers not available. Install with: pip install transformers torch")
    sys.exit(1)

class ToxicityModelTester:
    """Direct model testing class"""
    
    def __init__(self, model_path="./models/toxicity-model-final"):
        self.model_path = model_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 Using device: {self.device}")
        
        # Test data with expected results
        self.test_cases = [
            # Clean content (should be NON-TOXIC)
            {"text": "I love this beautiful day!", "expected": "NON_TOXIC", "category": "✅ Positive"},
            {"text": "Thank you for the helpful feedback.", "expected": "NON_TOXIC", "category": "✅ Polite"},
            {"text": "This is a great article about technology.", "expected": "NON_TOXIC", "category": "✅ Neutral"},
            {"text": "What a wonderful community we have here.", "expected": "NON_TOXIC", "category": "✅ Appreciation"},
            {"text": "The weather forecast shows rain tomorrow.", "expected": "NON_TOXIC", "category": "✅ Factual"},
            
            # Mildly negative but not toxic
            {"text": "I disagree with this opinion.", "expected": "NON_TOXIC", "category": "😐 Disagreement"},
            {"text": "This is quite frustrating to deal with.", "expected": "NON_TOXIC", "category": "😐 Mild negative"},
            {"text": "I'm having a difficult day today.", "expected": "NON_TOXIC", "category": "😐 Personal struggle"},
            
            # Borderline toxic
            {"text": "You're being annoying.", "expected": "BORDERLINE", "category": "⚠️ Mild insult"},
            {"text": "This is stupid.", "expected": "BORDERLINE", "category": "⚠️ Mild profanity"},
            {"text": "That's a dumb idea.", "expected": "BORDERLINE", "category": "⚠️ Criticism"},
            
            # Clearly toxic content
            {"text": "You're a complete idiot.", "expected": "TOXIC", "category": "🚨 Direct insult"},
            {"text": "Go kill yourself.", "expected": "TOXIC", "category": "🚨 Self-harm suggestion"},
            {"text": "I hate you so much.", "expected": "TOXIC", "category": "🚨 Hate speech"},
            {"text": "You're worthless and should die.", "expected": "TOXIC", "category": "🚨 Severe harassment"},
            {"text": "F**k you, you piece of sh*t.", "expected": "TOXIC", "category": "🚨 Profanity + insult"},
            {"text": "Nobody likes you, loser.", "expected": "TOXIC", "category": "🚨 Bullying"},
        ]
        
        self.load_model()
    
    def load_model(self):
        """Load the model using different methods"""
        print("🤖 Loading toxicity detection model...")
        
        # Method 1: Try our local model
        if os.path.exists(self.model_path):
            print(f"📁 Attempting to load local model from: {self.model_path}")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
                self.model.to(self.device)
                self.model.eval()
                
                # Create pipeline
                self.classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device == "cuda" else -1,
                    return_all_scores=True
                )
                
                print("✅ Local model loaded successfully")
                self.model_source = "local"
                return
                
            except Exception as e:
                print(f"❌ Failed to load local model: {e}")
        
        # Method 2: Try pre-trained toxic-bert
        print("🌐 Attempting to load pre-trained toxic-bert...")
        try:
            model_name = "unitary/toxic-bert"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline
            self.classifier = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            print("✅ Pre-trained toxic-bert loaded successfully")
            self.model_source = "pretrained"
            return
            
        except Exception as e:
            print(f"❌ Failed to load pre-trained model: {e}")
        
        # Method 3: Try alternative model
        print("🔄 Attempting to load alternative model...")
        try:
            model_name = "martin-ha/toxic-comment-model"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline
            self.classifier = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            print("✅ Alternative model loaded successfully")
            self.model_source = "alternative"
            return
            
        except Exception as e:
            print(f"❌ Failed to load alternative model: {e}")
            
        raise Exception("Could not load any toxicity model")
    
    def test_raw_model_output(self, text: str) -> Dict:
        """Test raw model output to understand what it returns"""
        print(f"\n🔍 Raw Model Analysis for: '{text[:50]}...'")
        
        # Method 1: Pipeline approach
        try:
            pipeline_result = self.classifier(text)
            print(f"📊 Pipeline result: {pipeline_result}")
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            pipeline_result = None
        
        # Method 2: Direct model inference
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
            print(f"🧮 Raw logits: {logits}")
            print(f"📐 Logits shape: {logits.shape}")
            
            # Different interpretations based on output shape
            if logits.shape[-1] == 1:
                # Single output - sigmoid for probability
                prob = torch.sigmoid(logits).cpu().numpy()[0][0]
                print(f"🎯 Sigmoid probability: {prob:.4f}")
                prediction = "TOXIC" if prob > 0.5 else "NON_TOXIC"
                confidence = prob if prob > 0.5 else (1 - prob)
                
            elif logits.shape[-1] == 2:
                # Two outputs [NON_TOXIC, TOXIC] - softmax
                probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
                print(f"🎯 Softmax probabilities: NON_TOXIC={probs[0]:.4f}, TOXIC={probs[1]:.4f}")
                prediction = "TOXIC" if probs[1] > probs[0] else "NON_TOXIC"
                confidence = max(probs)
                prob = probs[1]  # toxicity probability
                
            else:
                print(f"❓ Unexpected output shape: {logits.shape}")
                prob = 0.5
                prediction = "UNKNOWN"
                confidence = 0.0
                
            direct_result = {
                "prediction": prediction,
                "toxicity_probability": prob,
                "confidence": confidence,
                "logits": logits.cpu().numpy().tolist()
            }
            print(f"🎲 Direct inference: {direct_result}")
            
        except Exception as e:
            print(f"❌ Direct inference failed: {e}")
            direct_result = None
        
        return {
            "text": text,
            "pipeline_result": pipeline_result,
            "direct_result": direct_result,
            "model_source": self.model_source
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("=" * 80)
        print("🧪 COMPREHENSIVE TOXICITY MODEL TEST")
        print("=" * 80)
        
        print(f"📋 Model source: {self.model_source}")
        print(f"🔧 Device: {self.device}")
        print(f"📊 Test cases: {len(self.test_cases)}")
        
        results = []
        correct_predictions = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n{'='*20} Test {i}/{len(self.test_cases)} {'='*20}")
            print(f"📝 {test_case['category']}: {test_case['text']}")
            print(f"🎯 Expected: {test_case['expected']}")
            
            # Get raw model output
            raw_result = self.test_raw_model_output(test_case['text'])
            
            # Determine actual prediction
            if raw_result['direct_result']:
                actual_prob = raw_result['direct_result']['toxicity_probability']
                actual_prediction = raw_result['direct_result']['prediction']
                
                # Classify based on probability thresholds
                if actual_prob < 0.3:
                    classified = "NON_TOXIC"
                elif actual_prob < 0.7:
                    classified = "BORDERLINE"
                else:
                    classified = "TOXIC"
                    
            else:
                actual_prob = 0.5
                actual_prediction = "UNKNOWN"
                classified = "UNKNOWN"
            
            # Check if prediction is reasonable
            expected = test_case['expected']
            is_correct = (
                (expected == "NON_TOXIC" and classified in ["NON_TOXIC", "BORDERLINE"]) or
                (expected == "BORDERLINE" and classified in ["NON_TOXIC", "BORDERLINE", "TOXIC"]) or
                (expected == "TOXIC" and classified in ["BORDERLINE", "TOXIC"])
            )
            
            if is_correct:
                correct_predictions += 1
                status = "✅ CORRECT"
            else:
                status = "❌ INCORRECT"
            
            print(f"📊 Toxicity Probability: {actual_prob:.4f}")
            print(f"🏷️  Classified as: {classified}")
            print(f"🎭 Result: {status}")
            
            results.append({
                **test_case,
                "actual_probability": actual_prob,
                "actual_prediction": actual_prediction,
                "classified": classified,
                "is_correct": is_correct,
                "raw_result": raw_result
            })
        
        # Summary
        accuracy = correct_predictions / len(self.test_cases)
        print("\n" + "="*80)
        print("📈 TEST SUMMARY")
        print("="*80)
        print(f"✅ Correct predictions: {correct_predictions}/{len(self.test_cases)}")
        print(f"📊 Accuracy: {accuracy:.2%}")
        print(f"🤖 Model source: {self.model_source}")
        
        # Category breakdown
        print("\n📋 Results by Category:")
        categories = {}
        for result in results:
            cat = result['category'].split(' ')[1] if ' ' in result['category'] else result['category']
            if cat not in categories:
                categories[cat] = {"correct": 0, "total": 0}
            categories[cat]["total"] += 1
            if result['is_correct']:
                categories[cat]["correct"] += 1
        
        for cat, stats in categories.items():
            acc = stats["correct"] / stats["total"]
            print(f"  {cat}: {stats['correct']}/{stats['total']} ({acc:.1%})")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"toxicity_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": len(self.test_cases),
                    "correct_predictions": correct_predictions,
                    "accuracy": accuracy,
                    "model_source": self.model_source,
                    "device": self.device,
                    "timestamp": timestamp
                },
                "results": results
            }, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Diagnosis
        print("\n🔬 DIAGNOSIS:")
        if accuracy < 0.5:
            print("❌ Model is performing poorly - likely an implementation issue")
            print("   • Check model loading and inference logic")
            print("   • Verify model format and expected outputs")
        elif accuracy < 0.7:
            print("⚠️  Model has moderate performance - may need tuning")
            print("   • Consider adjusting thresholds")
            print("   • Check for systematic biases in predictions")
        else:
            print("✅ Model is performing well - implementation is likely correct")
            print("   • Service integration issues may be elsewhere")
        
        return results

def main():
    """Main test execution"""
    print("🚀 Starting Toxicity Model Test...")
    
    try:
        tester = ToxicityModelTester()
        results = tester.run_comprehensive_test()
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
