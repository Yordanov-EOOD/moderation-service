#!/usr/bin/env python3
"""
Moderation Service Demo Script

This script demonstrates the AI-powered toxicity detection capabilities
of the moderation service with a user-friendly interface.

Usage:
    python demo_moderation.py [--url URL] [--interactive] [--no-tests]
"""

import argparse
import json
import requests
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text: str, color: str = Colors.ENDC) -> None:
    """Print text with color."""
    print(f"{color}{text}{Colors.ENDC}")

def print_header(title: str) -> None:
    """Print a formatted header."""
    print()
    print_colored("=" * 60, Colors.HEADER)
    print_colored(f" {title}", Colors.HEADER)
    print_colored("=" * 60, Colors.HEADER)
    print()

def format_toxicity_result(result: Dict) -> None:
    """Format and display toxicity analysis result."""
    if result.get('is_toxic'):
        status_color = Colors.FAIL
        status = "🚨 TOXIC"
    else:
        status_color = Colors.OKGREEN
        status = "✅ CLEAN"
    
    print_colored(f"Status: {status}", status_color)
    print_colored(f"Toxicity Score: {result.get('toxicity_score', 'N/A')} / 1.0", Colors.OKBLUE)
    print_colored(f"Confidence: {result.get('confidence', 'N/A')}", Colors.OKBLUE)
    print_colored(f"Model Used: {result.get('model_used', 'N/A')}", Colors.OKBLUE)
    
    categories = result.get('categories', [])
    if categories:
        print_colored(f"Categories: {', '.join(categories)}", Colors.WARNING)
    else:
        print_colored("Categories: None detected", Colors.OKBLUE)
    
    print_colored(f"Content Length: {result.get('content_length', 'N/A')} characters", Colors.OKBLUE)
    print_colored(f"Timestamp: {result.get('timestamp', 'N/A')}", Colors.OKBLUE)
    print()

def test_service_health(service_url: str) -> bool:
    """Test if the service is healthy and accessible."""
    print_header("🏥 HEALTH CHECK")
    
    try:
        response = requests.get(f"{service_url}/health", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print_colored("✅ Service is healthy!", Colors.OKGREEN)
        print_colored(f"Service: {data.get('service', 'N/A')}", Colors.OKBLUE)
        print_colored(f"Version: {data.get('version', 'N/A')}", Colors.OKBLUE)
        
        detector = data.get('detector', {})
        print_colored(f"Detector Type: {detector.get('detector_type', 'N/A')}", Colors.OKBLUE)
        print_colored(f"Model: {detector.get('model_name', 'N/A')}", Colors.OKBLUE)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_colored(f"❌ Service health check failed: {str(e)}", Colors.FAIL)
        return False

def test_single_content(service_url: str, content: str, description: str = "") -> Optional[Dict]:
    """Test a single piece of content for toxicity."""
    if description:
        print_colored(f"🧪 Testing: {description}", Colors.HEADER)
    print_colored(f'Content: "{content}"', Colors.OKBLUE)
    print()
    
    try:
        payload = {
            "content": content,
            "yeet_id": f"demo-{int(time.time())}",
            "user_id": "demo-user"
        }
        
        response = requests.post(
            f"{service_url}/api/moderation/check",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        format_toxicity_result(result)
        return result
        
    except requests.exceptions.RequestException as e:
        print_colored(f"❌ Error testing content: {str(e)}", Colors.FAIL)
        print()
        return None

def test_batch_content(service_url: str) -> None:
    """Test batch processing of multiple contents."""
    print_header("📦 BATCH TESTING")
    test_messages = [
        {"content": "I love spending time with my friends!", "description": "✅ Positive message"},
        {"content": "This weather is absolutely terrible today", "description": "😐 Negative but not toxic"},
        {"content": "You're such an amazing person", "description": "✅ Compliment"},
        {"content": "That's really annoying and frustrating", "description": "⚠️ Mild negativity"},
        {"content": "You're being stupid about this", "description": "🚨 Insulting language"}
    ]
    
    yeets = []
    for i, msg in enumerate(test_messages):
        yeets.append({
            "content": msg["content"],
            "yeet_id": f"batch-{i}-{int(time.time())}",
            "user_id": "demo-user"
        })
    
    try:
        payload = {"yeets": yeets}
        response = requests.post(
            f"{service_url}/api/moderation/batch",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        print_colored(f"📊 Batch Results (Total: {data.get('total_processed', 'N/A')})", Colors.HEADER)
        print()
        
        results = data.get('results', [])
        for i, result in enumerate(results):
            if i < len(test_messages):
                print_colored(f"[{i + 1}] {test_messages[i]['description']}", Colors.OKBLUE)
                print_colored(f'Content: "{test_messages[i]["content"]}"', Colors.OKBLUE)
                format_toxicity_result(result)
                
    except requests.exceptions.RequestException as e:
        print_colored(f"❌ Error in batch testing: {str(e)}", Colors.FAIL)

def run_demo_tests(service_url: str) -> None:
    """Run a comprehensive set of demo tests."""
    print_header("🚀 MODERATION SERVICE DEMO")
    
    # Test service health
    if not test_service_health(service_url):
        print_colored("Cannot proceed without healthy service. Please start the moderation service.", Colors.FAIL)
        return
    
    print_header("🧪 SINGLE CONTENT TESTS")
      # Test cases with various content types (from clean to toxic)
    test_cases = [
        {"content": "What a beautiful day! I love this sunshine.", "description": "✅ Positive content"},
        {"content": "I'm having a challenging day, but I'll get through it.", "description": "😐 Neutral/slightly negative"},
        {"content": "This is just a normal comment about technology.", "description": "😐 Neutral technical content"},
        {"content": "I disagree with your opinion, but I respect your right to have it.", "description": "😐 Respectful disagreement"},
        {"content": "The weather forecast shows rain for tomorrow.", "description": "😐 Factual statement"},
        {"content": "You're kind of annoying sometimes", "description": "⚠️ Mildly negative"},
        {"content": "This is stupid and makes no sense", "description": "⚠️ Moderate negativity"},
        {"content": "You are an idiot and I hate your opinion", "description": "🚨 Insulting language"},
        {"content": "Go kill yourself, nobody likes you", "description": "🚨 Severe toxicity/harassment"},
        {"content": "F**k this s**t, you're all morons", "description": "🚨 Profanity + insults"}
    ]
    
    results = []
    for test in test_cases:
        result = test_single_content(service_url, test["content"], test["description"])
        if result:
            results.append(result)
        time.sleep(0.5)  # Small delay for readability
    
    # Show summary statistics
    if results:
        print_header("📈 SUMMARY STATISTICS")
        total_tests = len(results)
        toxic_count = sum(1 for r in results if r.get('is_toxic'))
        clean_count = total_tests - toxic_count
        avg_score = sum(r.get('toxicity_score', 0) for r in results) / total_tests if total_tests > 0 else 0
        avg_confidence = sum(r.get('confidence', 0) for r in results) / total_tests if total_tests > 0 else 0
        
        print_colored(f"Total Tests: {total_tests}", Colors.OKBLUE)
        print_colored(f"Clean Content: {clean_count} ({clean_count/total_tests*100:.1f}%)", Colors.OKGREEN)
        print_colored(f"Toxic Content: {toxic_count} ({toxic_count/total_tests*100:.1f}%)", Colors.FAIL)
        print_colored(f"Average Toxicity Score: {avg_score:.3f}", Colors.OKBLUE)
        print_colored(f"Average Confidence: {avg_confidence:.3f}", Colors.OKBLUE)
        print()
    
    # Batch testing
    test_batch_content(service_url)

def start_interactive_mode(service_url: str) -> None:
    """Start interactive mode for user input."""
    print_header("🎮 INTERACTIVE MODE")
    print_colored("Enter text to check for toxicity. Type 'quit' to exit.", Colors.OKBLUE)
    print()
    
    while True:
        try:
            user_input = input(f"{Colors.HEADER}Enter content to analyze: {Colors.ENDC}")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print_colored("👋 Goodbye!", Colors.OKGREEN)
                break
                
            if not user_input.strip():
                print_colored("⚠️ Please enter some content to analyze.", Colors.WARNING)
                continue
            
            print()
            test_single_content(service_url, user_input)
            
        except KeyboardInterrupt:
            print_colored("\n👋 Goodbye!", Colors.OKGREEN)
            break
        except EOFError:
            print_colored("\n👋 Goodbye!", Colors.OKGREEN)
            break

def show_service_info(service_url: str) -> None:
    """Show detailed service information."""
    print_header("ℹ️ SERVICE INFORMATION")
    
    try:
        response = requests.get(f"{service_url}/api/moderation/info", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print_colored(f"Detector Type: {data.get('detector_type', 'N/A')}", Colors.OKBLUE)
        print_colored(f"Version: {data.get('version', 'N/A')}", Colors.OKBLUE)
        print_colored(f"Framework: {data.get('framework', 'N/A')}", Colors.OKBLUE)
        print_colored(f"Model Name: {data.get('model_name', 'N/A')}", Colors.OKBLUE)
        print_colored(f"Description: {data.get('description', 'N/A')}", Colors.OKBLUE)
        
    except requests.exceptions.RequestException as e:
        print_colored(f"❌ Could not retrieve service info: {str(e)}", Colors.FAIL)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Demo script for the moderation service")
    parser.add_argument("--url", default="http://localhost:5000", help="Service URL")
    parser.add_argument("--interactive", action="store_true", help="Start in interactive mode")
    parser.add_argument("--no-tests", action="store_true", help="Skip running demo tests")
    
    args = parser.parse_args()
    
    # Print banner
    print_colored("""
 ╔══════════════════════════════════════════════════════════════╗
 ║                    MODERATION SERVICE DEMO                    ║
 ║                                                              ║
 ║  This script demonstrates the AI-powered toxicity detection  ║
 ║  capabilities of our moderation service.                     ║
 ╚══════════════════════════════════════════════════════════════╝
    """, Colors.HEADER)
    
    print_colored(f"🔗 Service URL: {args.url}", Colors.OKBLUE)
    print()
    
    # Show service information
    show_service_info(args.url)
    
    # Run tests if requested
    if not args.no_tests:
        run_demo_tests(args.url)
    
    # Start interactive mode if requested
    if args.interactive:
        start_interactive_mode(args.url)
    else:
        print()
        print_colored("💡 Tip: Run with --interactive flag for interactive mode!", Colors.OKBLUE)
        print_colored("💡 Example: python demo_moderation.py --interactive", Colors.OKBLUE)
    
    print()
    print_colored("Demo completed! 🎉", Colors.OKGREEN)

if __name__ == "__main__":
    main()
