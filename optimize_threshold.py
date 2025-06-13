#!/usr/bin/env python3
"""
Threshold optimization test to find the best toxicity threshold
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.toxicity_detector import ToxicityDetector
import numpy as np

def optimize_threshold():
    """Find the optimal threshold for toxicity detection"""
    
    # Test cases with ground truth labels
    test_cases = [
        # Clean content (False = non-toxic)
        {"content": "What a beautiful day! I love this sunshine.", "label": False},
        {"content": "Thank you for the helpful feedback!", "label": False},
        {"content": "This is a normal technical discussion.", "label": False},
        {"content": "I disagree but respect your opinion.", "label": False},
        {"content": "The weather forecast shows rain.", "label": False},
        {"content": "This is annoying and frustrating.", "label": False},
        {"content": "That's really disappointing.", "label": False},
        
        # Toxic content (True = toxic)
        {"content": "You're a complete idiot.", "label": True},
        {"content": "Go kill yourself, nobody likes you.", "label": True},
        {"content": "You are so stupid and ugly.", "label": True},
        {"content": "F**k this s**t, you're all morons.", "label": True},
        {"content": "I hate you so much, you should die.", "label": True},
        {"content": "You're worthless trash and everyone knows it.", "label": True},
        {"content": "Kill yourself you pathetic loser.", "label": True},
        {"content": "You're the dumbest person alive.", "label": True},
        {"content": "I hope you get cancer and die slowly.", "label": True}
    ]
    
    print("🎯 THRESHOLD OPTIMIZATION")
    print("=" * 60)
    
    # Initialize detector
    detector = ToxicityDetector(use_ml_model=True)
    
    # Get toxicity scores for all test cases
    scores = []
    labels = []
    
    for test_case in test_cases:
        result = detector.check_toxicity(test_case["content"])
        scores.append(result["toxicity_score"])
        labels.append(test_case["label"])
    
    scores = np.array(scores)
    labels = np.array(labels)
    
    # Test different thresholds
    thresholds = np.arange(0.45, 0.75, 0.01)
    best_threshold = 0.5
    best_accuracy = 0
    
    print(f"{'Threshold':<12} {'Accuracy':<10} {'TP':<4} {'FP':<4} {'TN':<4} {'FN':<4} {'Precision':<10} {'Recall':<8}")
    print("-" * 60)
    
    for threshold in thresholds:
        predictions = scores >= threshold
        
        # Calculate metrics
        tp = np.sum((predictions == True) & (labels == True))   # True Positives
        fp = np.sum((predictions == True) & (labels == False))  # False Positives  
        tn = np.sum((predictions == False) & (labels == False)) # True Negatives
        fn = np.sum((predictions == False) & (labels == True))  # False Negatives
        
        accuracy = (tp + tn) / len(labels)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        print(f"{threshold:<12.3f} {accuracy:<10.3f} {tp:<4} {fp:<4} {tn:<4} {fn:<4} {precision:<10.3f} {recall:<8.3f}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = threshold
    
    print("-" * 60)
    print(f"🏆 Best threshold: {best_threshold:.3f} (accuracy: {best_accuracy:.3f})")
    
    # Show score distribution
    print(f"\n📊 Score Distribution:")
    clean_scores = scores[labels == False]
    toxic_scores = scores[labels == True]
    
    print(f"Clean content scores: min={clean_scores.min():.3f}, max={clean_scores.max():.3f}, mean={clean_scores.mean():.3f}")
    print(f"Toxic content scores: min={toxic_scores.min():.3f}, max={toxic_scores.max():.3f}, mean={toxic_scores.mean():.3f}")
    
    return best_threshold

if __name__ == "__main__":
    best_threshold = optimize_threshold()
    print(f"\n💡 Recommended threshold: {best_threshold:.3f}")
    print(f"💡 Set environment variable: TOXICITY_THRESHOLD={best_threshold:.3f}")
