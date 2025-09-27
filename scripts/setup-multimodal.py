#!/usr/bin/env python3
"""
Option A: Multimodal Implementation - Quick Setup Script
Automates the initial setup for document processing implementation
"""

import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def create_directory(path, description):
    """Create directory and handle errors"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {description}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {description}: {e}")
        return False

def main():
    print("🚀 OPTION A: MULTIMODAL AI GATEWAY - QUICK SETUP")
    print("=" * 60)
    
    # Get current directory
    current_dir = Path.cwd()
    ai_gateway_dir = current_dir / "ai-gateway"
    
    print(f"📂 Working directory: {current_dir}")
    print(f"📂 AI Gateway directory: {ai_gateway_dir}")
    
    if not ai_gateway_dir.exists():
        print("❌ ai-gateway directory not found!")
        print("   Please run this script from the fastembed project root")
        sys.exit(1)
    
    # Step 1: Create directory structure
    print("\n📁 STEP 1: Creating multimodal directory structure")
    directories = [
        (ai_gateway_dir / "src" / "converters", "Document converters"),
        (ai_gateway_dir / "src" / "processors", "Document processors"),
        (ai_gateway_dir / "tests" / "multimodal", "Multimodal tests"),
        (ai_gateway_dir / "examples" / "multimodal", "Multimodal examples"),
        (current_dir / "models" / "granite", "Granite models"),
        (current_dir / "models" / "whisper", "Whisper models (future)"),
    ]
    
    for dir_path, description in directories:
        create_directory(dir_path, description)
    
    # Step 2: Update requirements.txt
    print("\n📦 STEP 2: Adding multimodal dependencies")
    requirements_file = ai_gateway_dir / "requirements.txt"
    
    multimodal_deps = """
# Document Processing Dependencies
pymupdf>=1.23.0          # PDF processing
python-docx>=0.8.11      # DOCX processing  
pytesseract>=0.3.10      # OCR capability
pillow>=10.0.0           # Image processing
python-magic>=0.4.27     # File type detection
tqdm>=4.65.0             # Progress bars for downloads

# Future: Audio Processing (Week 3)
# librosa>=0.10.0          # Audio processing
# soundfile>=0.12.0        # Audio I/O

# Future: Vision Processing (Week 2)  
# opencv-python>=4.8.0     # Image preprocessing
# transformers>=4.30.0     # Tokenization support
"""
    
    try:
        with open(requirements_file, 'a') as f:
            f.write(multimodal_deps)
        print("✅ Added multimodal dependencies to requirements.txt")
    except Exception as e:
        print(f"❌ Failed to update requirements.txt: {e}")
    
    # Step 3: Install new dependencies
    print("\n🔽 STEP 3: Installing document processing dependencies")
    venv_python = current_dir / ".venv" / "Scripts" / "python.exe"  # Windows
    if not venv_python.exists():
        venv_python = current_dir / ".venv" / "bin" / "python"  # Linux/Mac
    
    if venv_python.exists():
        install_cmd = f'"{venv_python}" -m pip install pymupdf python-docx pytesseract pillow python-magic tqdm'
        run_command(install_cmd, "Installing document processing dependencies")
    else:
        print("⚠️  Virtual environment not found. Please install dependencies manually:")
        print("   pip install pymupdf python-docx pytesseract pillow python-magic tqdm")
    
    # Step 4: Download Granite models
    print("\n📥 STEP 4: Downloading Granite models")
    scripts_dir = current_dir / "scripts"
    download_script = scripts_dir / "download-granite-docling.py"
    
    if download_script.exists():
        if venv_python.exists():
            download_cmd = f'"{venv_python}" "{download_script}" --model-dir "../models/granite"'
            success = run_command(download_cmd, "Downloading Granite Docling models", cwd=scripts_dir)
            if not success:
                print("⚠️  Model download failed. You can run it manually later:")
                print(f"   cd {scripts_dir}")
                print(f"   python download-granite-docling.py")
        else:
            print("⚠️  Please download models manually:")
            print(f"   cd {scripts_dir}")
            print("   python download-granite-docling.py")
    else:
        print("⚠️  Download script not found. Please ensure download-granite-docling.py exists in scripts/")
    
    # Step 5: Create placeholder files
    print("\n📝 STEP 5: Creating implementation files")
    
    # Create __init__.py files
    init_files = [
        ai_gateway_dir / "src" / "converters" / "__init__.py",
        ai_gateway_dir / "src" / "processors" / "__init__.py",
        ai_gateway_dir / "tests" / "multimodal" / "__init__.py",
    ]
    
    for init_file in init_files:
        try:
            init_file.touch()
            print(f"✅ Created: {init_file.name}")
        except Exception as e:
            print(f"❌ Failed to create {init_file.name}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 QUICK SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n✅ COMPLETED:")
    print("   • Multimodal directory structure created")
    print("   • Dependencies added to requirements.txt")  
    print("   • Document processing packages installed")
    print("   • Granite model download initiated")
    print("   • Implementation files created")
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Verify Granite models downloaded successfully")
    print("   2. Implement document converters (see OPTION_A_QUICK_START.md)")
    print("   3. Add document processing endpoints")
    print("   4. Test with sample PDF files")
    
    print(f"\n📚 DOCUMENTATION:")
    print(f"   • Complete plan: {current_dir / 'OPTION_A_COMPLETE_MULTIMODAL_PLAN.md'}")
    print(f"   • Quick start guide: {current_dir / 'OPTION_A_QUICK_START.md'}")
    
    print("\n🚀 Ready to transform your AI gateway into a multimodal powerhouse!")

if __name__ == "__main__":
    main()