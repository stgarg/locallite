# 🚀 Snapdragon NPU Model Building - Detailed Analysis & Implementation Plan

## 📋 **Process Overview**

The ONNX Runtime documentation provides a complete methodology for building NPU-optimized models for Snapdragon processors. This would enable **true NPU acceleration** even in WSL environments.

## 🔍 **Detailed Analysis**

### **What This Methodology Provides:**
1. **True NPU Acceleration**: Direct Qualcomm NPU utilization
2. **QNN Context Binaries**: Hardware-optimized binary format
3. **ONNX Wrapper Models**: Standard ONNX interface with NPU backend
4. **Quantized Models**: INT4/INT8 optimization for NPU efficiency

### **Key Requirements:**
- ✅ **WSL Compatible**: Linux environment requirement is satisfied
- ✅ **Snapdragon Hardware**: We have Qualcomm ARM64 processor
- 🔧 **Qualcomm AI Hub Access**: Need to sign up
- 🔧 **QNN SDK**: Need to download and install
- 🔧 **Model License**: Need HuggingFace access for Llama models

## 📊 **Current vs Target Architecture:**

| Component | Current Status | Target with NPU Models |
|-----------|----------------|------------------------|
| **Embedding Model** | bge-small-en-v1.5 (Azure Provider) | Custom NPU-optimized embedding |
| **Chat Model** | Gemma-3n-4b (CPU) | Llama-3.2-3B (True NPU) |
| **Acceleration** | ARM64 + Azure optimization | Qualcomm NPU hardware |
| **Performance** | 193ms (single), 833ms (batch) | Expected: 2-5x faster |

## 🛠️ **Implementation Plan**

### **Phase 1: Environment Setup (1-2 hours)**

#### **1.1 Prerequisites Installation**
```bash
# Already have WSL ✅
# Install libc++-dev
sudo apt install libc++-dev

# Install ONNX
pip install onnx
```

#### **1.2 Qualcomm Accounts & SDKs**
- [ ] Sign up for [Qualcomm AI Hub](https://aihub.qualcomm.com/)
- [ ] Configure AI Hub API token
- [ ] Download [Qualcomm AI Engine Direct SDK](https://softwarecenter.qualcomm.com/#/catalog/item/qualcomm_neural_processing_sdk_public)
- [ ] Set `QNN_SDK_ROOT` environment variable

#### **1.3 Model Access**
- [ ] Sign up for [Llama-3.2-3B HuggingFace access](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- [ ] Obtain HuggingFace token for model download

### **Phase 2: Model Generation (2-4 hours)**

#### **2.1 Install Qualcomm Model Tools**
```bash
python -m pip install -U qai_hub_models[llama-v3-2-3b-chat-quantized]
```

#### **2.2 Generate QNN Context Binaries**
```bash
# This uploads model to Qualcomm AI Hub for NPU optimization
python -m qai_hub_models.models.llama_v3_2_3b_chat_quantized.export \
  --device "Snapdragon X Elite CRD" \
  --skip-inferencing \
  --skip-profiling \
  --output-dir ./npu_models/
```

**Expected Output:**
- `*.bin` - QNN context binaries (NPU-optimized)
- Hardware-specific optimization for our Snapdragon X Elite

#### **2.3 Extract QNN Graph Information**
```bash
# Download ONNX wrapper generation script
curl -LO https://raw.githubusercontent.com/microsoft/onnxruntime/refs/heads/main/onnxruntime/python/tools/qnn/gen_qnn_ctx_onnx_model.py

# Extract graph info from each binary
for bin_file in *.bin; do 
  $QNN_SDK_ROOT/bin/x86_64-linux-clang/qnn-context-binary-utility \
    --context_binary="$bin_file" \
    --json_file="${bin_file%.bin}.json"
done
```

#### **2.4 Generate ONNX Wrapper Models**
```bash
# Create ONNX models that use QNN context binaries
for bin_file in *.bin; do 
  python gen_qnn_ctx_onnx_model.py \
    -b "$bin_file" \
    -q "${bin_file%.bin}.json" \
    --quantized_IO \
    --disable_embed_mode
done
```

#### **2.5 Download Additional Assets**
```bash
# Download tokenizer and config files
wget https://huggingface.co/onnx-community/Llama-3.2-3B-instruct-hexagon-npu-assets/resolve/main/genai_config.json
wget https://huggingface.co/onnx-community/Llama-3.2-3B-instruct-hexagon-npu-assets/resolve/main/tokenizer.json
wget https://huggingface.co/onnx-community/Llama-3.2-3B-instruct-hexagon-npu-assets/resolve/main/tokenizer_config.json
wget https://huggingface.co/onnx-community/Llama-3.2-3B-instruct-hexagon-npu-assets/resolve/main/special_tokens_map.json
```

### **Phase 3: Integration (2-3 hours)**

#### **3.1 Model Directory Structure**
```
models/llama-3.2-3b-npu/
├── genai_config.json
├── tokenizer.json
├── tokenizer_config.json
├── special_tokens_map.json
├── quantizer.onnx
├── dequantizer.onnx
├── position-processor.onnx
├── transformer_*.bin      # QNN context binaries
├── transformer_*.json     # Metadata
└── transformer_*.onnx     # ONNX wrappers
```

#### **3.2 ONNX Runtime with QNN Provider**
```bash
# Install ONNX Runtime with QNN support
pip uninstall onnxruntime
pip install onnxruntime-qnn  # If available for Linux ARM64
# OR build from source with QNN provider enabled
```

#### **3.3 Update AI Gateway Configuration**
- Modify `gemma_model.py` to support Llama-3.2-3B
- Add QNNExecutionProvider detection and usage
- Update model loading logic for new binary format

### **Phase 4: Testing & Validation (1-2 hours)**

#### **4.1 NPU Detection Test**
```python
import onnxruntime as ort
providers = ort.get_available_providers()
assert "QNNExecutionProvider" in providers
```

#### **4.2 Performance Benchmarking**
- Compare NPU vs current Azure provider performance
- Measure latency improvements
- Test batch processing efficiency

## 🎯 **Expected Benefits**

### **Performance Improvements:**
- **Chat Latency**: 280ms → ~100-150ms (2-3x faster)
- **Batch Processing**: Better scaling with NPU parallel processing
- **Memory Efficiency**: Quantized models use less RAM
- **Power Efficiency**: NPU uses less power than CPU

### **Capabilities:**
- **True Hardware Acceleration**: Direct NPU utilization
- **Production Ready**: Qualcomm-validated optimization
- **Scalable**: Better performance for concurrent requests

## 🚨 **Potential Challenges**

### **Technical Risks:**
1. **QNN Provider Availability**: May not be available for Linux ARM64
2. **SDK Compatibility**: WSL compatibility with Qualcomm SDK
3. **Model Size**: NPU models may be larger than current models
4. **Development Complexity**: More complex build and deployment process

### **Resource Requirements:**
- **Time**: 6-10 hours total implementation
- **Storage**: ~5-10GB for model assets and tools
- **Network**: Multiple GB downloads from AI Hub
- **Accounts**: Qualcomm and HuggingFace registrations

## 📅 **Execution Strategy**

### **Recommended Approach: Proof of Concept First**

#### **Step 1: Quick Feasibility Test (30 minutes)**
```bash
# Test Qualcomm SDK installation
# Check if QNN provider can be built/installed
# Verify AI Hub access
```

#### **Step 2: Single Model Test (2-3 hours)**
- Build just one Llama-3.2-3B model component
- Test NPU detection and basic inference
- Benchmark performance vs current solution

#### **Step 3: Full Integration (if Step 2 succeeds)**
- Complete model build process
- Integrate into AI Gateway
- Performance optimization and testing

## 🎯 **Decision Matrix**

| Factor | Current Azure Solution | NPU Model Building |
|--------|----------------------|-------------------|
| **Time to Implement** | ✅ Already working | ⚠️ 6-10 hours |
| **Performance Gain** | ✅ Good (Azure optimization) | 🚀 Excellent (2-3x faster) |
| **Complexity** | ✅ Low maintenance | ⚠️ High complexity |
| **Hardware Dependency** | ✅ Universal | ⚠️ Snapdragon-specific |
| **Future-Proof** | ✅ Stable | 🚀 Leading edge |

## 🚀 **Recommendation**

**I recommend we proceed with a Proof of Concept approach:**

1. **Quick validation** (Step 1) to ensure feasibility
2. **If successful**, build one NPU model for testing
3. **Compare performance** against current Azure optimization
4. **Make informed decision** based on actual performance gains

This would give us the **best of both worlds**: 
- Keep current working Azure optimization
- Add true NPU acceleration if the benefits justify the complexity

Would you like me to start with **Step 1: Quick Feasibility Test** to check if the Qualcomm SDK and tools work in our WSL environment?