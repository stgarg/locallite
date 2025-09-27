#!/usr/bin/env python3
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
        print(f"[OK] {filename} already exists")
        return True
        
    print(f"[DOWNLOAD] Downloading {filename}...")
    
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
                    
        print(f"[OK] Downloaded {filename}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to download {filename}: {e}")
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
    
    print(f"Model directory: {model_dir.absolute()}")
    print(f"Models to download: {list(models_to_download)}")
    
    # Calculate total download size
    total_mb = sum(GRANITE_MODELS[model]["size_mb"] for model in models_to_download)
    print(f"[INFO] Total download size: ~{total_mb}MB")
    
    # Download models
    success_count = 0
    for model_name in models_to_download:
        model_info = GRANITE_MODELS[model_name]
        if download_model(model_info, model_dir):
            success_count += 1
    
    print(f"\n[COMPLETE] Downloaded {success_count}/{len(models_to_download)} models successfully")
    
    if success_count == len(models_to_download):
        print("[OK] All models ready for document processing!")
        print(f"📁 Models location: {model_dir.absolute()}")
    else:
        print("[WARNING] Some models failed to download. Check network connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()