#!/usr/bin/env python3
"""
Setup script for YOLO Streamlit App
This script helps users set up the environment and dependencies
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["models", "sample_images"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}/")

def download_sample_yolo():
    """Download a sample YOLO model"""
    print("\n🤖 Downloading sample YOLO model...")
    try:
        # Try to download a small YOLO model
        import torch
        from ultralytics import YOLO
        
        print("Downloading YOLOv5n (nano) model...")
        model = YOLO('yolov5n.pt')  # This will download automatically
        print("✅ Sample YOLO model downloaded successfully!")
        return True
    except ImportError:
        print("⚠️  Ultralytics not installed yet. Run this script again after installing requirements.")
        return False
    except Exception as e:
        print(f"⚠️  Could not download sample model: {e}")
        print("You can manually download a YOLO model from: https://github.com/ultralytics/yolov5/releases")
        return False

def run_sample_script():
    """Run the sample data creation script"""
    print("\n🎨 Creating sample data...")
    try:
        subprocess.check_call([sys.executable, "example_usage.py"])
        print("✅ Sample data created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not create sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up YOLO Streamlit App")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Download sample YOLO model
    download_sample_yolo()
    
    # Create sample data
    run_sample_script()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("\nTo run the application:")
    print("1. streamlit run yolo_test_app.py")
    print("\nTo create sample data manually:")
    print("1. python example_usage.py")
    print("\nFor more information, see README.md")
    print("=" * 50)

if __name__ == "__main__":
    main() 