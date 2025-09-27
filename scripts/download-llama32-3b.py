#!/usr/bin/env python3
"""
Download Llama 3.2 3B ONNX model for NPU acceleration
Optimized for Qualcomm Snapdragon X NPUs
"""

import os
import requests
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_llama32_3b():
    """Download Llama 3.2 3B ONNX model from Hugging Face"""
    
    # Model configuration
    model_info = {
        "name": "llama-3.2-3b",
        "repo": "microsoft/Llama-3.2-3B-Instruct-onnx",
        "files": [
            "model.onnx",
            "model.onnx_data",
            "tokenizer.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "config.json"
        ]
    }
    
    # Create model directory
    model_dir = Path("../models/llama-3.2-3b")
    onnx_dir = model_dir / "onnx"
    
    model_dir.mkdir(parents=True, exist_ok=True)
    onnx_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Created model directory: {model_dir}")
    
    # Download files
    base_url = f"https://huggingface.co/{model_info['repo']}/resolve/main"
    
    for file_name in model_info['files']:
        file_path = model_dir / file_name if not file_name.endswith('.onnx') else onnx_dir / file_name
        
        if file_path.exists():
            logger.info(f"⏭️  Skipping {file_name} (already exists)")
            continue
            
        logger.info(f"📥 Downloading {file_name}...")
        
        try:
            response = requests.get(f"{base_url}/{file_name}", stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
                
                print()  # New line after progress
            
            logger.info(f"✅ Downloaded {file_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to download {file_name}: {e}")
            return False
    
    # Create model info file
    info_file = model_dir / "model_info.json"
    with open(info_file, 'w') as f:
        json.dump({
            "model_name": "Llama 3.2 3B Instruct",
            "architecture": "llama",
            "parameters": "3B",
            "context_length": 131072,
            "quantization": "fp16",
            "npu_optimized": True,
            "provider_priority": ["QNNExecutionProvider", "CPUExecutionProvider"],
            "download_date": "2024-09-24",
            "source": model_info['repo']
        }, indent=2)
    
    logger.info("✅ Llama 3.2 3B model downloaded successfully!")
    logger.info(f"📍 Location: {model_dir}")
    
    # Print size info
    total_size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    logger.info(f"📊 Total size: {size_mb:.1f} MB")
    
    return True

if __name__ == "__main__":
    success = download_llama32_3b()
    if success:
        print("🎉 Ready to use Llama 3.2 3B with NPU acceleration!")
    else:
        print("❌ Download failed. Please check the errors above.")