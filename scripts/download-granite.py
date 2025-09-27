# 🏃‍♂️ Option A: Quick Start Guide - Complete Multimodal Implementation

## 🎯 **IMMEDIATE NEXT ACTIONS (Today)**

Based on our comprehensive 3-week plan, here's exactly what we'll do to get started:

---

## **1. PROJECT SETUP (15 minutes)**

### **Create New Directory Structure**
```powershell
# From ai-gateway directory:
cd C:\Learn\Code\fastembed\ai-gateway

# Create multimodal directories
New-Item -ItemType Directory -Path "src\converters" -Force
New-Item -ItemType Directory -Path "src\processors" -Force  
New-Item -ItemType Directory -Path "tests\multimodal" -Force
New-Item -ItemType Directory -Path "models\granite" -Force
New-Item -ItemType Directory -Path "models\whisper" -Force
New-Item -ItemType Directory -Path "examples\multimodal" -Force
```

### **Update Dependencies**
```powershell
# Add multimodal dependencies to requirements.txt
```

**New dependencies to add**:
```
# Document Processing
pymupdf>=1.23.0          # PDF processing
python-docx>=0.8.11      # DOCX processing  
pytesseract>=0.3.10      # OCR
pillow>=10.0.0           # Image processing

# Audio Processing (Week 3)
librosa>=0.10.0          # Audio processing
soundfile>=0.12.0        # Audio I/O

# Vision Processing (Week 2)  
opencv-python>=4.8.0     # Image preprocessing
transformers>=4.30.0     # Tokenization support
```

---

## **2. DOCUMENT PROCESSING KICKOFF (Today)**

### **Step 1: Create Granite Model Download Script** ⏱️ 30 minutes

<function_calls>
<invoke name="create_file">
<parameter name="content">#!/usr/bin/env python3
"""
Granite Model Download Script for Document Processing
Downloads IBM Granite Docling models for text extraction and layout analysis
"""

import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm
import argparse

GRANITE_MODELS = {
    "text-extraction": {
        "url": "https://huggingface.co/ibm-granite/granite-docling-text-extraction-256m/resolve/main/model.onnx",
        "filename": "granite-text-extraction-256m.onnx",
        "size_mb": 512
    },
    "layout-analysis": {
        "url": "https://huggingface.co/ibm-granite/granite-docling-layout-analysis-128m/resolve/main/model.onnx", 
        "filename": "granite-layout-analysis-128m.onnx",
        "size_mb": 256
    },
    "table-detection": {
        "url": "https://huggingface.co/ibm-granite/granite-docling-table-detection-64m/resolve/main/model.onnx",
        "filename": "granite-table-detection-64m.onnx", 
        "size_mb": 128
    }
}

def download_model(model_info, model_dir):
    """Download a single model with progress bar"""
    url = model_info["url"]
    filename = model_info["filename"]
    filepath = model_dir / filename
    
    if filepath.exists():
        print(f"✅ {filename} already exists")
        return True
        
    print(f"📥 Downloading {filename}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
                    
        print(f"✅ Downloaded {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        if filepath.exists():
            filepath.unlink()
        return False

def main():
    parser = argparse.ArgumentParser(description="Download Granite Docling models")
    parser.add_argument("--model-dir", default="../models/granite", 
                       help="Directory to save models")
    parser.add_argument("--models", nargs="+", 
                       choices=list(GRANITE_MODELS.keys()) + ["all"],
                       default=["all"],
                       help="Models to download")
    
    args = parser.parse_args()
    
    # Create model directory
    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which models to download
    if "all" in args.models:
        models_to_download = GRANITE_MODELS.keys()
    else:
        models_to_download = args.models
    
    print(f"📂 Model directory: {model_dir.absolute()}")
    print(f"📋 Models to download: {list(models_to_download)}")
    
    # Calculate total download size
    total_mb = sum(GRANITE_MODELS[model]["size_mb"] for model in models_to_download)
    print(f"💾 Total download size: ~{total_mb}MB")
    
    # Download models
    success_count = 0
    for model_name in models_to_download:
        model_info = GRANITE_MODELS[model_name]
        if download_model(model_info, model_dir):
            success_count += 1
    
    print(f"\n🎉 Downloaded {success_count}/{len(models_to_download)} models successfully")
    
    if success_count == len(models_to_download):
        print("✅ All models ready for document processing!")
        print(f"📁 Models location: {model_dir.absolute()}")
    else:
        print("⚠️  Some models failed to download. Check network connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()