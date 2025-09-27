#!/usr/bin/env python3
"""
Download Gemma 3N ONNX Model
Downloads the quantized Q4 version optimized for local inference
"""

import os
import requests
import logging
from pathlib import Path
from huggingface_hub import hf_hub_download
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_gemma_3n_model():
    """Download Gemma 3N ONNX model from Hugging Face"""
    
    model_dir = Path("c:/Learn/Code/fastembed/models/gemma-3n")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Hugging Face repository
    repo_id = "onnx-community/gemma-3n-E2B-it-ONNX"
    
    # Files to download (starting with text-only Q4 quantized version)
    files_to_download = [
        # Core config files
        "config.json",
        "generation_config.json", 
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        
        # Text model components (Q4 quantized for efficiency)
        "onnx/embed_tokens_quantized.onnx",
        "onnx/embed_tokens_quantized.onnx_data",
        "onnx/embed_tokens_quantized.onnx_data_1", 
        "onnx/decoder_model_merged_q4.onnx",
    ]
    
    logger.info(f"📥 Downloading Gemma 3N model to {model_dir}")
    logger.info(f"🔗 Repository: {repo_id}")
    
    total_start_time = time.time()
    
    for file_path in files_to_download:
        try:
            start_time = time.time()
            logger.info(f"⬇️ Downloading {file_path}...")
            
            # Download file
            local_file = hf_hub_download(
                repo_id=repo_id,
                filename=file_path,
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            
            download_time = time.time() - start_time
            file_size = os.path.getsize(local_file)
            size_mb = file_size / (1024 * 1024)
            
            logger.info(f"✅ Downloaded {file_path} ({size_mb:.1f} MB) in {download_time:.1f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to download {file_path}: {e}")
            return False
    
    total_time = time.time() - total_start_time
    
    logger.info(f"🎉 Gemma 3N model download completed in {total_time:.1f}s")
    logger.info(f"📁 Model location: {model_dir}")
    
    # Verify files exist
    expected_files = [
        "config.json", 
        "tokenizer.json", 
        "onnx/embed_tokens_quantized.onnx",
        "onnx/decoder_model_merged_q4.onnx"
    ]
    missing_files = []
    
    for file_name in expected_files:
        file_path = model_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        logger.warning(f"⚠️ Missing expected files: {missing_files}")
        return False
    
    logger.info("✅ All required files present")
    logger.info("💡 Text chat functionality ready (vision/audio can be added later)")
    return True

def check_disk_space():
    """Check if we have enough disk space for the model"""
    import shutil
    
    model_dir = Path("c:/Learn/Code/fastembed/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    free_space = shutil.disk_usage(model_dir).free
    free_gb = free_space / (1024**3)
    
    # Gemma 3N Q4 is approximately 4-5GB
    required_gb = 6  # Buffer for safety
    
    logger.info(f"💾 Available disk space: {free_gb:.1f} GB")
    logger.info(f"💾 Required space: {required_gb} GB")
    
    if free_gb < required_gb:
        logger.error(f"❌ Insufficient disk space. Need {required_gb}GB, have {free_gb:.1f}GB")
        return False
    
    logger.info("✅ Sufficient disk space available")
    return True

if __name__ == "__main__":
    logger.info("🚀 Starting Gemma 3N model download...")
    
    # Check disk space first
    if not check_disk_space():
        exit(1)
    
    # Install huggingface_hub if not available
    try:
        import huggingface_hub
    except ImportError:
        logger.info("📦 Installing huggingface_hub...")
        os.system("pip install huggingface_hub")
        import huggingface_hub
    
    # Download the model
    if download_gemma_3n_model():
        logger.info("🎯 Model download successful!")
        logger.info("💡 You can now start the AI Gateway with Gemma 3N support")
    else:
        logger.error("💥 Model download failed!")
        exit(1)