#!/usr/bin/env python3
"""
Service Logic Test Script
=========================

This script replicates the exact logic used in our moderation service
to isolate whether the issue is in the service integration or model logic.
"""

import os
import sys
import json
from datetime import datetime

# Add the service source path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from services.toxicity_detector import ToxicityDetector
except ImportError as e:
    print(f"❌ Could not import ToxicityDetector: {e}")
    print("Make sure you're running from the moderation-service directory")
    sys.exit(1)

class ServiceLogicTester:
    """Test the exact service logic"""
    
    def __init__(self):
        print("🔧 Initializing Service Logic Tester...")
        
        # Test messages with different severity levels
        self.test_messages = [
            # Clean content
            {"content": "I love this beautiful day!", "expected_toxic": False, "severity": "✅ Clean"},
            {"content": "Thank you for your helpful feedback.", "expected_toxic": False, "severity": "✅ Clean"},
            {"content": "This is a great article about technology.", "expected_toxic": False, "severity": "✅ Clean"},
            {"content": "What a wonderful community we have here.", "expected_toxic": False, "severity": "✅ Clean"},
            {"content": "The weather forecast shows rain tomorrow.", "expected_toxic": False, "severity": "✅ Clean"},
            
            # Borderline content
            {"content": "I disagree with this opinion.", "expected_toxic": False, "severity": "😐 Neutral"},
            {"content": "This is quite frustrating to deal with.", "expected_toxic": False, "severity": "😐 Neutral"},
            {"content": "You're being annoying.", "expected_toxic": True, "severity": "⚠️ Mild"},
            {"content": "That's a stupid idea.", "expected_toxic": True, "severity": "⚠️ Mild"},
            {"content": "This is dumb.", "expected_toxic": True, "severity": "⚠️ Mild"},
            
            # Clearly toxic content
            {"content": "You're a complete idiot.", "expected_toxic": True, "severity": "🚨 Toxic"},
            {"content": "Go kill yourself.", "expected_toxic": True, "severity": "🚨 Toxic"},
            {"content": "I hate you so much.", "expected_toxic": True, "severity": "🚨 Toxic"},
            {"content": "You're worthless and should die.", "expected_toxic": True, "severity": "🚨 Toxic"},
            {"content": "F**k you, you piece of sh*t.", "expected_toxic": True, "severity": "🚨 Toxic"},
            {"content": "Nobody likes you, loser.", "expected_toxic": True, "severity": "🚨 Toxic"},
        ]
        
        # Initialize the detector (same as service)
        self.detector = ToxicityDetector(use_ml_model=True)
        
    def test_service_logic(self):
        """Test the service logic directly"""
        print("🧪 Testing Service Logic...")
        print("=" * 80)
        
        results = []
        correct_predictions = 0
        
        for i, test_case in enumerate(self.test_messages, 1):
            content = test_case["content"]
            expected = test_case["expected_toxic"]
            severity = test_case["severity"]
            
            print(f"\n📝 Test {i}/{len(self.test_messages)}: {severity}")
            print(f"💬 Content: \"{content}\"")
            print(f"🎯 Expected: {'TOXIC' if expected else 'CLEAN'}")
            
            try:
                # Call the exact same method our service uses
                result = self.detector.check_toxicity(content)
                
                # Extract key information
                is_toxic = result.get('is_toxic', False)
                toxicity_score = result.get('toxicity_score', 0.0)
                confidence = result.get('confidence', 0.0)
                categories = result.get('categories', [])
                detector_version = result.get('detector_version', 'unknown')
                model_used = result.get('model_used', 'unknown')
                threshold_used = result.get('threshold_used', 0.5)
                
                # Check if prediction is correct
                is_correct = (is_toxic == expected)
                if is_correct:
                    correct_predictions += 1
                    status_icon = "✅"
                else:
                    status_icon = "❌"
                
                print(f"📊 Result: {'TOXIC' if is_toxic else 'CLEAN'} {status_icon}")
                print(f"📈 Toxicity Score: {toxicity_score:.4f}")
                print(f"🎲 Confidence: {confidence:.4f}")
                print(f"🔧 Threshold: {threshold_used}")
                print(f"🏷️  Categories: {categories}")
                print(f"🤖 Model: {model_used}")
                print(f"📦 Detector: {detector_version}")
                
                # Store result
                results.append({
                    **test_case,
                    "actual_toxic": is_toxic,
                    "toxicity_score": toxicity_score,
                    "confidence": confidence,
                    "categories": categories,
                    "is_correct": is_correct,
                    "full_result": result
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({
                    **test_case,
                    "error": str(e),
                    "is_correct": False
                })
        
        # Calculate accuracy
        accuracy = correct_predictions / len(self.test_messages)
        
        print("\n" + "=" * 80)
        print("📈 SERVICE LOGIC TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Correct predictions: {correct_predictions}/{len(self.test_messages)}")
        print(f"📊 Accuracy: {accuracy:.2%}")
        
        # Breakdown by severity
        print("\n📋 Results by Severity:")
        severity_stats = {}
        for result in results:
            sev = result['severity']
            if sev not in severity_stats:
                severity_stats[sev] = {"correct": 0, "total": 0}
            severity_stats[sev]["total"] += 1
            if result.get('is_correct', False):
                severity_stats[sev]["correct"] += 1
        
        for sev, stats in severity_stats.items():
            sev_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {sev}: {stats['correct']}/{stats['total']} ({sev_acc:.1%})")
        
        # Detailed analysis
        print("\n🔬 DETAILED ANALYSIS:")
        
        # Check false positives (clean content marked as toxic)
        false_positives = [r for r in results if not r["expected_toxic"] and r.get("actual_toxic", False)]
        if false_positives:
            print(f"\n❌ False Positives ({len(false_positives)}):")
            for fp in false_positives:
                print(f"   • \"{fp['content']}\" - Score: {fp.get('toxicity_score', 'N/A')}")
        
        # Check false negatives (toxic content marked as clean)
        false_negatives = [r for r in results if r["expected_toxic"] and not r.get("actual_toxic", True)]
        if false_negatives:
            print(f"\n❌ False Negatives ({len(false_negatives)}):")
            for fn in false_negatives:
                print(f"   • \"{fn['content']}\" - Score: {fn.get('toxicity_score', 'N/A')}")
        
        # Score distribution analysis
        scores = [r.get('toxicity_score', 0) for r in results if 'toxicity_score' in r]
        if scores:
            print(f"\n📊 Score Distribution:")
            print(f"   • Min: {min(scores):.4f}")
            print(f"   • Max: {max(scores):.4f}")
            print(f"   • Average: {sum(scores)/len(scores):.4f}")
            print(f"   • Median: {sorted(scores)[len(scores)//2]:.4f}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"service_logic_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": len(self.test_messages),
                    "correct_predictions": correct_predictions,
                    "accuracy": accuracy,
                    "timestamp": timestamp,
                    "detector_info": self.detector.get_detector_info()
                },
                "results": results,
                "analysis": {
                    "false_positives": len(false_positives),
                    "false_negatives": len(false_negatives),
                    "score_stats": {
                        "min": min(scores) if scores else 0,
                        "max": max(scores) if scores else 0,
                        "avg": sum(scores)/len(scores) if scores else 0
                    }
                }
            }, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Final diagnosis
        print("\n🏥 DIAGNOSIS:")
        if accuracy < 0.4:
            print("🚨 CRITICAL: Service logic is severely broken")
            print("   • Check model loading and initialization")
            print("   • Verify toxicity score calculation")
            print("   • Check threshold application")
        elif accuracy < 0.6:
            print("⚠️  WARNING: Service logic has significant issues")
            print("   • Review score calculation logic")
            print("   • Check threshold settings")
            print("   • Verify model output interpretation")
        elif accuracy < 0.8:
            print("⚡ MODERATE: Service logic needs tuning")
            print("   • Consider adjusting thresholds")
            print("   • Review edge cases")
        else:
            print("✅ GOOD: Service logic is working well")
            print("   • Integration issues may be elsewhere")
            print("   • API layer or request handling might be the issue")
        
        return results

def main():
    """Main execution"""
    print("🚀 Starting Service Logic Test...")
    
    try:
        tester = ServiceLogicTester()
        results = tester.test_service_logic()
        
        print("\n✅ Service logic test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
