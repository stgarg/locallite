## Dependency & Version Pins (Initial)

Primary runtime: .NET 8 (win-arm64 RID)

NuGet Packages:
- Microsoft.ML.OnnxRuntime 1.19.2
- Microsoft.ML.OnnxRuntime.DirectML 1.19.2 (optional EP)
- System.Text.Json 8.0.4 (Bundled in framework; explicit pin for trimming clarity)

Model Assets (place under `models/bge-small-en-v1.5/`):
- `model.onnx` : Exported fp32 BERT-like encoder (bge-small-en-v1.5)
- `vocab.txt` : WordPiece vocabulary
- `tokenizer_config.json` : (Optional) Contains do_lower_case, max_len
- `special_tokens_map.json` : (Optional) CLS/SEP/PAD/MASK specification

Version Guidance:
- Prefer ONNX Runtime >=1.19.x for optimized ARM64 kernels.
- If using quantized model, track a second artifact: `model.int8.onnx` (dynamic or static quantization).

Hash Verification (example process once files downloaded):
```powershell
Get-FileHash .\models\bge-small-en-v1.5\model.onnx -Algorithm SHA256
```

Planned future optional dependencies (not yet added):
- Serilog (structured logging) if extended beyond Console logging.
- CommandLineParser (if CLI argument parsing grows).

No native tokenizers dependency to keep single-file publish simpler.
