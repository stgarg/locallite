# Model Setup Guide

FastEmbed requires pre-trained ONNX models to be placed in the `EmbeddingServer/models/` directory. Models are **not included** in the repository to keep it lightweight.

## 📂 Required Directory Structure

```
EmbeddingServer/models/
├── bge-small-en-v1.5/           # Recommended: Fast, high-quality English embeddings
│   ├── model.onnx               # Main ONNX model file
│   ├── tokenizer.json           # Tokenizer configuration 
│   ├── vocab.txt                # Vocabulary file
│   └── config.json              # Model configuration
├── all-MiniLM-L6-v2/            # Alternative: Smaller, faster model
│   ├── model.onnx
│   ├── tokenizer.json
│   └── vocab.txt
└── multilingual-e5-small/       # Optional: Multilingual support
    ├── model.onnx
    ├── tokenizer.json
    ├── tokenizer_config.json
    ├── vocab.txt
    └── config.json
```

## 🚀 Quick Setup

### Option 1: Automated Download (Recommended)
Use our PowerShell scripts to download models automatically:

```powershell
# Download BGE-small-en-v1.5 (recommended)
cd EmbeddingServer/scripts
.\download-bge-model.ps1

# Download E5-small multilingual (optional)  
.\download-e5-prebuilt.ps1
```

### Option 2: Manual Download
1. **BGE-small-en-v1.5** (Primary model):
   - Source: [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
   - Download ONNX version or convert from PyTorch
   - Place in `EmbeddingServer/models/bge-small-en-v1.5/`

2. **All-MiniLM-L6-v2** (Alternative):
   - Source: [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
   - Smaller model, faster inference
   - Place in `EmbeddingServer/models/all-MiniLM-L6-v2/`

## 🔧 Model Configuration

The AI Gateway automatically detects available models in the `models/` directory. Configure your preferred model in `EmbeddingServer/src/Config.cs`:

```csharp
public static class Config
{
    public static string DefaultModel = "bge-small-en-v1.5"; // Change as needed
    public static string ModelsPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "models");
}
```

## 📊 Model Comparison

| Model | Size | Dimensions | Speed | Quality | Use Case |
|-------|------|------------|-------|---------|----------|
| **bge-small-en-v1.5** | ~120MB | 384 | Fast | High | **Recommended for most use cases** |
| all-MiniLM-L6-v2 | ~90MB | 384 | Fastest | Good | Quick prototyping, low latency |
| multilingual-e5-small | ~470MB | 384 | Medium | High | Multilingual applications |

## 🎯 Performance with NPU

On Snapdragon X Elite (NPU acceleration):
- **BGE-small-en-v1.5**: ~150ms per batch (1000 tokens)
- **All-MiniLM-L6-v2**: ~120ms per batch (1000 tokens)
- **E5-multilingual**: ~200ms per batch (1000 tokens)

## ⚠️ Important Notes

1. **Model files are large** (100-500MB each) - that's why they're excluded from Git
2. **ONNX format required** - PyTorch/TensorFlow models need conversion
3. **Directory names must match exactly** - The server looks for specific folder names
4. **At least one model required** - The server won't start without models

## 🛠️ Troubleshooting

**Server won't start?**
- Check that model files exist in correct directories
- Verify ONNX files are valid (not corrupted downloads)
- Check console output for specific error messages

**Poor performance?**
- Ensure you're using the NPU-optimized ONNX models
- Check that DirectML/NPU drivers are installed
- Monitor CPU vs NPU usage in Task Manager

**Out of memory errors?**
- Try the smaller all-MiniLM-L6-v2 model
- Reduce batch sizes in your API calls
- Close other memory-intensive applications

## 📚 Next Steps

After model setup:
1. Start the AI Gateway: `cd EmbeddingServer/src && dotnet run`
2. Test with examples: `cd fastembed-sdk/examples && python basic_usage.py`
3. Run benchmarks: `python azure_demo.py` 

For detailed usage instructions, see the main [README.md](../README.md).