#!/usr/bin/env python3
"""
OpenCV Dependency Fixer for YOLO Streamlit App
This script helps detect and fix OpenCV library issues
"""

import subprocess
import sys
import platform
import os

def detect_os():
    """Detect the operating system"""
    system = platform.system().lower()
    if system == "linux":
        # Try to detect Linux distribution
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "ubuntu" in content or "debian" in content:
                    return "ubuntu_debian"
                elif "centos" in content or "rhel" in content:
                    return "centos_rhel"
                elif "fedora" in content:
                    return "fedora"
                elif "arch" in content:
                    return "arch"
                else:
                    return "linux_generic"
        except:
            return "linux_generic"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

def check_opencv():
    """Check if OpenCV can be imported"""
    try:
        import cv2
        print("✅ OpenCV is working correctly!")
        return True
    except ImportError as e:
        print(f"❌ OpenCV import error: {e}")
        return False
    except Exception as e:
        if "libGL.so.1" in str(e):
            print("❌ OpenCV GL library error detected")
            return False
        else:
            print(f"❌ OpenCV error: {e}")
            return False

def get_install_commands(os_type):
    """Get installation commands for the detected OS"""
    commands = {
        "ubuntu_debian": [
            "sudo apt update",
            "sudo apt install -y libgl1-mesa-glx libglib2.0-0"
        ],
        "centos_rhel": [
            "sudo yum install -y mesa-libGL"
        ],
        "fedora": [
            "sudo dnf install -y mesa-libGL"
        ],
        "arch": [
            "sudo pacman -S mesa"
        ],
        "linux_generic": [
            "sudo apt update && sudo apt install -y libgl1-mesa-glx libglib2.0-0",
            "# Or try: sudo yum install mesa-libGL",
            "# Or try: sudo dnf install mesa-libGL"
        ]
    }
    return commands.get(os_type, commands["linux_generic"])

def main():
    """Main function"""
    print("🔧 OpenCV Dependency Fixer for YOLO Streamlit App")
    print("=" * 60)
    
    # Detect OS
    os_type = detect_os()
    print(f"📋 Detected OS: {os_type}")
    
    # Check OpenCV
    print("\n🔍 Checking OpenCV...")
    opencv_ok = check_opencv()
    
    if opencv_ok:
        print("\n🎉 Everything is working correctly!")
        print("You can now run: streamlit run yolo_test_app.py")
        return
    
    print("\n⚠️ OpenCV has dependency issues.")
    print("Here are the solutions:")
    
    # Show installation commands
    commands = get_install_commands(os_type)
    print(f"\n📦 Installation commands for {os_type}:")
    for cmd in commands:
        print(f"  {cmd}")
    
    # Alternative solutions
    print("\n🔄 Alternative Solutions:")
    print("1. Use headless OpenCV (no GUI features):")
    print("   pip uninstall opencv-python")
    print("   pip install opencv-python-headless")
    
    print("\n2. Use Docker (recommended):")
    print("   docker run -p 8501:8501 -v $(pwd):/app streamlit/streamlit:latest")
    
    print("\n3. Install system libraries manually:")
    print("   - Ubuntu/Debian: libgl1-mesa-glx, libglib2.0-0")
    print("   - CentOS/RHEL: mesa-libGL")
    print("   - Fedora: mesa-libGL")
    print("   - Arch: mesa")
    
    # Ask user if they want to run commands
    print("\n" + "=" * 60)
    response = input("Do you want to try installing the dependencies? (y/n): ").lower()
    
    if response in ['y', 'yes']:
        print("\n🚀 Attempting to install dependencies...")
        for cmd in commands:
            if not cmd.startswith("#"):
                print(f"Running: {cmd}")
                try:
                    result = subprocess.run(cmd, shell=True, check=True)
                    print(f"✅ Success: {cmd}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed: {cmd}")
                    print(f"Error: {e}")
        
        print("\n🔄 Checking OpenCV again...")
        if check_opencv():
            print("🎉 Success! OpenCV is now working.")
            print("You can now run: streamlit run yolo_test_app.py")
        else:
            print("❌ OpenCV still has issues. Try the alternative solutions above.")
    else:
        print("\n📝 Please run the installation commands manually or try the alternative solutions.")

if __name__ == "__main__":
    main() 