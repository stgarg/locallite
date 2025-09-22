#!/usr/bin/env python3
"""
FastEmbed SDK Setup Script
Helps configure environment for secure benchmarking
"""

import os
import shutil

def setup_environment():
    """Set up environment for FastEmbed SDK"""
    print("🚀 FastEmbed SDK Setup")
    print("=" * 30)
    
    # Check if .env.example exists
    if not os.path.exists(".env.example"):
        print("❌ .env.example not found!")
        return False
    
    # Check if .env already exists
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        choice = input("📝 Overwrite existing .env file? (y/N): ").lower().strip()
        if choice not in ['y', 'yes']:
            print("📁 Keeping existing .env file")
            return True
    
    # Copy .env.example to .env
    try:
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from template")
        print()
        print("📝 Next steps:")
        print("   1. Edit .env file with your credentials:")
        print("      - Add your GPT Nano 4.1 endpoint URL and key")
        print("      - Add your ADA-003 endpoint URL and key")
        print("      - Optionally add public API keys for comparison")
        print()
        print("   2. Run benchmarks:")
        print("      python secure_benchmark.py")
        print()
        print("🔒 Security notes:")
        print("   - .env file is gitignored (never committed)")
        print("   - Credentials stay on your local machine")
        print("   - No keys exposed in benchmark outputs")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        "fastembed",
        "httpx", 
        "python-dotenv",
        "numpy"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    else:
        print(f"\n✅ All dependencies installed!")
        return True

def test_fastembed_connection():
    """Test connection to FastEmbed server"""
    print("\n🔌 Testing FastEmbed server connection...")
    
    try:
        import fastembed
        client = fastembed.FastEmbedClient()
        health = client.health()
        
        print(f"   ✅ Connected to {client.base_url}")
        print(f"   NPU Available: {health.npu_available}")
        print(f"   Models: {', '.join(health.models_loaded)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print(f"   💡 Make sure FastEmbed server is running:")
        print(f"      cd ai-gateway/src && python main.py")
        return False

def main():
    """Run complete setup"""
    print("🎯 FastEmbed SDK Complete Setup")
    print("=" * 40)
    
    success = True
    
    # 1. Check dependencies
    if not check_dependencies():
        success = False
    
    # 2. Test FastEmbed connection
    if not test_fastembed_connection():
        success = False
    
    # 3. Setup environment
    if not setup_environment():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Setup complete!")
        print()
        print("🚀 Ready to run benchmarks:")
        print("   python secure_benchmark.py")
        print()
        print("📚 Or try examples:")
        print("   python simple_demo.py")
        print("   python examples/basic_usage.py")
    else:
        print("❌ Setup incomplete")
        print("🔧 Please resolve the issues above and try again")

if __name__ == "__main__":
    main()