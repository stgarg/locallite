#!/usr/bin/env python3
"""
Install Missing Dependencies Script
Automatically installs and configures missing dependencies for the document processing system.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description):
    """Run a system command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_dependency(module_name, test_code, description):
    """Check if a dependency is available"""
    try:
        exec(test_code)
        print(f"✅ {description}: Available")
        return True
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def install_tesseract_windows():
    """Install Tesseract OCR on Windows"""
    print("\n🎯 Installing Tesseract OCR...")
    
    # Check if chocolatey is available
    choco_available = run_command("choco --version", "Checking Chocolatey")
    
    if choco_available:
        success = run_command("choco install tesseract -y", "Installing Tesseract via Chocolatey")
        if success:
            # Add to PATH if not already there
            tesseract_path = "C:\\ProgramData\\chocolatey\\lib\\tesseract\\tools"
            current_path = os.environ.get('PATH', '')
            if tesseract_path not in current_path:
                print(f"⚠️  Please add {tesseract_path} to your system PATH manually")
        return success
    else:
        print("❌ Chocolatey not found. Please install Tesseract manually:")
        print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Install to: C:\\Program Files\\Tesseract-OCR\\")
        print("   3. Add C:\\Program Files\\Tesseract-OCR to your PATH")
        return False

def install_libmagic_windows():
    """Install libmagic on Windows"""
    print("\n🎯 Installing libmagic...")
    
    # Try conda first
    conda_available = run_command("conda --version", "Checking Conda")
    
    if conda_available:
        return run_command("conda install -c conda-forge python-magic -y", "Installing python-magic via Conda")
    else:
        print("❌ Conda not found. libmagic installation on Windows requires manual setup:")
        print("   1. Download libmagic DLL from: https://github.com/pidydx/libmagicwin64")
        print("   2. Extract to your Python directory or add to PATH")
        return False

def install_web_dependencies():
    """Install FastAPI and related web dependencies"""
    print("\n🎯 Installing Web Service Dependencies...")
    
    commands = [
        ("pip install fastapi", "Installing FastAPI"),
        ("pip install uvicorn", "Installing Uvicorn ASGI server"),
    ]
    
    all_success = True
    for command, description in commands:
        if not run_command(command, description):
            all_success = False
    
    return all_success

def install_optional_dependencies():
    """Install optional advanced dependencies"""
    print("\n🎯 Installing Optional Dependencies...")
    
    print("⚠️  Note: Docling requires pandas which may conflict with our Polars setup")
    user_input = input("Install Docling? (y/N): ").lower().strip()
    
    if user_input == 'y':
        return run_command("pip install docling", "Installing Docling")
    else:
        print("⏭️  Skipping Docling installation")
        return True

def main():
    """Main installation process"""
    print("🚀 FastEmbed Document Processing - Dependency Installer")
    print("=" * 60)
    
    # Check current status
    print("\n📋 Checking Current Status...")
    
    dependencies = [
        ("pytesseract.get_tesseract_version()", "import pytesseract", "Tesseract OCR"),
        ("magic.Magic()", "import magic", "libmagic"),
        ("import fastapi", "import fastapi", "FastAPI"),
        ("import docling", "import docling", "Docling")
    ]
    
    missing = []
    for test_code, import_code, name in dependencies:
        try:
            exec(import_code)
            try:
                exec(test_code)
                print(f"✅ {name}: Available")
            except Exception:
                missing.append(name)
                print(f"❌ {name}: Installed but not working")
        except ImportError:
            missing.append(name)
            print(f"❌ {name}: Not installed")
    
    if not missing:
        print("\n🎉 All dependencies are already installed!")
        return
    
    print(f"\n🎯 Found {len(missing)} missing dependencies")
    print("Missing:", ", ".join(missing))
    
    # Installation process
    system = platform.system()
    
    if system == "Windows":
        print(f"\n🖥️  Installing for Windows...")
        
        # Install critical dependencies
        if "Tesseract OCR" in missing:
            install_tesseract_windows()
        
        if "libmagic" in missing:
            install_libmagic_windows()
        
        # Install web dependencies
        if "FastAPI" in missing:
            install_web_dependencies()
        
        # Install optional dependencies
        if "Docling" in missing:
            install_optional_dependencies()
    
    else:
        print(f"❌ Automated installation not supported for {system}")
        print("Please install dependencies manually according to MISSING_DEPENDENCIES.md")
    
    # Final verification
    print("\n🔍 Final Verification...")
    
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR: Working")
    except Exception as e:
        print(f"❌ Tesseract OCR: {e}")
    
    try:
        import magic
        magic.Magic()
        print("✅ libmagic: Working")
    except Exception as e:
        print(f"❌ libmagic: {e}")
    
    try:
        import fastapi
        print("✅ FastAPI: Available")
    except ImportError:
        print("❌ FastAPI: Not available")
    
    print("\n🎉 Installation process complete!")
    print("💡 You may need to restart your terminal/IDE for PATH changes to take effect")

if __name__ == "__main__":
    main()