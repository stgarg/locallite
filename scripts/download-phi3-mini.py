#!/usr/bin/env python3
"""
Download Microsoft Phi-3 Mini 4K Instruct ONNX - NPU Optimized
This model is specifically designed for NPU acceleration
"""

import os
import requests
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_phi3_mini_onnx():
    """Download Microsoft Phi-3 Mini DirectML ONNX model optimized for NPU"""
    
    model_info = {
        "name": "phi-3-mini-4k-directml",
        "repo": "microsoft/Phi-3-mini-4k-instruct-onnx",
        "base_path": "directml/directml-int4-awq-block-128",
        "files": [
            "model.onnx",
            "model.onnx.data", 
            "tokenizer.json",
            "tokenizer_config.json", 
            "special_tokens_map.json",
            "config.json",
            "genai_config.json"
        ]
    }
    
    # Create model directory
    model_dir = Path("../models/phi-3-mini-4k")
    onnx_dir = model_dir / "onnx"
    
    model_dir.mkdir(parents=True, exist_ok=True)
    onnx_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Created model directory: {model_dir}")
    
    # Download files
    base_url = f"https://huggingface.co/{model_info['repo']}/resolve/main/{model_info['base_path']}"
    
    for file_name in model_info['files']:
        if file_name.startswith('model.onnx'):
            local_path = onnx_dir / file_name  # Keep original names for ONNX files
        else:
            local_path = model_dir / file_name
            
        if local_path.exists():
            logger.info(f"⏭️  Skipping {file_name} (already exists)")
            continue
            
        logger.info(f"📥 Downloading {file_name}...")
        
        try:
            response = requests.get(f"{base_url}/{file_name}", stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\\r  Progress: {progress:.1f}%", end='', flush=True)
                
                print()  # New line
            
            logger.info(f"✅ Downloaded {file_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to download {file_name}: {e}")
            return False
    
    # Create model info
    info_file = model_dir / "model_info.json"
    import json
    with open(info_file, 'w') as f:
        json.dump({
            "model_name": "Phi-3 Mini 4K DirectML",
            "architecture": "phi3",
            "parameters": "3.8B",
            "context_length": 4096,
            "quantization": "int4-awq",
            "npu_optimized": True,
            "directml_optimized": True,
            "provider_priority": ["DmlExecutionProvider", "QNNExecutionProvider", "CPUExecutionProvider"],
            "download_date": "2024-09-24",
            "source": model_info['repo']
        }, f, indent=2)
    
    logger.info("✅ Phi-3 Mini DirectML ONNX model downloaded successfully!")
    logger.info("🚀 This is Microsoft's DirectML-optimized version for NPU!")
    
    return True

if __name__ == "__main__":
    success = download_phi3_mini_onnx()
    if success:
        print("🎉 Ready to test Phi-3 Mini with NPU acceleration!")
    else:
        print("❌ Download failed.")