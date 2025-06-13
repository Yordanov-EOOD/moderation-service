#!/usr/bin/env python3
"""
Setup script for the Moderation Service
This script helps set up the environment and test the custom toxicity model
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"  Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {description} completed successfully")
            return True
        else:
            print(f"  ❌ {description} failed:")
            print(f"     {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Error running {description}: {str(e)}")
        return False

def check_python_version():
    """Check if Python version is sufficient"""
    print("1. Checking Python version...")
    if sys.version_info < (3, 8):
        print("  ❌ Python 3.8 or higher is required")
        return False
    print(f"  ✓ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n2. Installing dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("  ❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def create_directories():
    """Create necessary directories"""
    print("\n3. Creating directories...")
    
    directories = ["models", "logs", ".vscode"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✓ Created/verified directory: {directory}")
    
    return True

def setup_environment():
    """Set up environment configuration"""
    print("\n4. Setting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("  ❌ .env.example not found")
        return False
    
    if not env_file.exists():
        shutil.copy(env_example, env_file)
        print("  ✓ Created .env from .env.example")
    else:
        print("  ✓ .env file already exists")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n5. Testing imports...")
    
    required_modules = [
        ("flask", "Flask web framework"),
        ("transformers", "Hugging Face Transformers"),
        ("torch", "PyTorch"),
        ("numpy", "NumPy"),
    ]
    
    all_imports_ok = True
    
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {description} imported successfully")
        except ImportError:
            print(f"  ❌ Failed to import {module} ({description})")
            all_imports_ok = False
    
    return all_imports_ok

def test_custom_model():
    """Test the custom toxicity model"""
    print("\n6. Testing custom toxicity model...")
    
    test_script = Path("test_custom_model.py")
    if not test_script.exists():
        print("  ❌ test_custom_model.py not found")
        return False
    
    return run_command(
        f"{sys.executable} test_custom_model.py",
        "Testing custom model functionality"
    )

def run_basic_service_test():
    """Run a basic test of the service"""
    print("\n7. Running basic service test...")
    
    test_script = Path("test_service.py")
    if not test_script.exists():
        print("  ❌ test_service.py not found")
        return False
    
    return run_command(
        f"{sys.executable} test_service.py",
        "Running basic service tests"
    )

def main():
    """Main setup function"""
    print("=" * 60)
    print("Moderation Service Setup")
    print("=" * 60)
    print("This script will set up your moderation service environment")
    print("and test the custom toxicity-model-final integration.")
    print()
    
    # Track success of each step
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Create Directories", create_directories),
        ("Setup Environment", setup_environment),
        ("Test Imports", test_imports),
        ("Test Custom Model", test_custom_model),
        ("Basic Service Test", run_basic_service_test),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"  ❌ Unexpected error in {step_name}: {str(e)}")
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    
    if not failed_steps:
        print("✅ All setup steps completed successfully!")
        print("\nYour moderation service is ready to use:")
        print("  - Start the service: python src/app.py")
        print("  - Or use: flask run")
        print("  - Service will be available at: http://localhost:5000")
        print("  - API documentation: http://localhost:5000/api/info")
    else:
        print("❌ Some setup steps failed:")
        for step in failed_steps:
            print(f"  - {step}")
        
        print("\nTroubleshooting:")
        if "Install Dependencies" in failed_steps:
            print("  - Try: pip install --upgrade pip")
            print("  - Try: pip install -r requirements.txt --no-cache-dir")
        
        if "Test Custom Model" in failed_steps:
            print("  - Ensure 'toxicity-model-final' is accessible")
            print("  - Check MODEL_NAME in .env file")
            print("  - Verify model files are in ./models directory")
        
        if "Test Imports" in failed_steps:
            print("  - Install missing packages: pip install <package-name>")
            print("  - Check Python version compatibility")
    
    print(f"\nFor more information, see: API-DOCUMENTATION.md")
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
