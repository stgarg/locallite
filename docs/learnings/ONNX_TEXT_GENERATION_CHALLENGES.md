# ONNX Text Generation Implementation Challenges

## Current Status
- ✅ Phi-3 Mini ONNX model loaded successfully with NPU acceleration
- ✅ Model inference session created (QNNExecutionProvider + CPUExecutionProvider)
- ❌ **FAKE responses using pattern matching instead of real inference**
- ❌ No proper tokenization or text generation pipeline

## Core Technical Challenges

### 1. **Tokenization Pipeline**
**Problem**: Using fake hash-based tokenization instead of real tokenizer
**Requirements**:
- Load actual Phi-3 tokenizer vocabulary (vocab.json, merges.txt, or tokenizer.json)
- Implement proper BPE (Byte Pair Encoding) tokenization
- Handle special tokens (BOS, EOS, PAD, UNK)
- Convert text → token IDs → model input

**Dependencies Needed**:
```bash
pip install tokenizers transformers
# OR implement custom tokenizer loading
```

### 2. **Iterative Text Generation**
**Problem**: Current code only runs single forward pass, but text generation requires multiple iterations
**Requirements**:
- Autoregressive generation (generate one token at a time)
- Maintain conversation context across token generations
- Implement stopping criteria (EOS token, max_tokens)
- Handle temperature/sampling for token selection

**Implementation Pattern**:
```python
for i in range(max_tokens):
    logits = model_session.run(inputs)
    next_token = sample_token(logits, temperature)
    if next_token == EOS_TOKEN:
        break
    input_ids = append(input_ids, next_token)
```

### 3. **Model Input/Output Handling**
**Problem**: Don't know exact input/output shapes and names for Phi-3 ONNX
**Investigation Needed**:
- Inspect model inputs: `session.get_inputs()` - names, shapes, types
- Inspect model outputs: `session.get_outputs()` - logits shape
- Handle attention masks, position IDs if required
- Proper batch dimension handling

### 4. **Memory and Context Management**
**Problem**: Phi-3 has 4K context window, need proper context sliding
**Requirements**:
- Track conversation history within context limits
- Implement context sliding window for long conversations
- Optimize memory usage for NPU inference
- Handle key-value caching for efficiency (if model supports it)

### 5. **Vocabulary Mapping**
**Problem**: No way to convert generated token IDs back to readable text
**Requirements**:
- Load vocabulary file (30K+ tokens for Phi-3)
- Implement detokenization (token IDs → text)
- Handle special characters, Unicode, whitespace properly
- Deal with subword tokens and merging

### 6. **Error Handling & Fallbacks**
**Problem**: ONNX inference can fail, need robust error handling
**Requirements**:
- Graceful degradation when NPU fails → CPU fallback
- Handle OOM errors with smaller batch sizes
- Timeout handling for long generations
- Proper logging for debugging inference issues

### 7. **Performance Optimization**
**Problem**: Real-time chat needs fast inference
**Requirements**:
- NPU optimization for Qualcomm chips
- Batch processing where possible
- Model quantization considerations
- Memory pre-allocation

## Dependency Analysis

### Critical Missing Dependencies:
```bash
# For proper tokenization
pip install tokenizers>=0.15.0

# For Phi-3 tokenizer loading (heavy dependency)
pip install transformers>=4.36.0

# Alternative: Custom tokenizer implementation
# - Load vocab.json manually
# - Implement BPE algorithm
# - Handle special tokens
```

### Dependency Conflicts:
- `transformers` package is heavy (torch dependency)
- May conflict with ONNX Runtime on ARM64
- Alternative: Use `tokenizers` package only (lighter)

## Implementation Strategy Options

### Option A: Full Transformers Integration
**Pros**: Complete tokenizer support, easy implementation
**Cons**: Heavy dependencies, potential ARM64 conflicts
```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-4k-instruct")
```

### Option B: Tokenizers-Only Approach
**Pros**: Lighter dependencies, more control
**Cons**: Need to handle model-specific details manually
```python
from tokenizers import Tokenizer
tokenizer = Tokenizer.from_file("tokenizer.json")
```

### Option C: Custom Tokenizer Implementation
**Pros**: Full control, minimal dependencies
**Cons**: Complex implementation, higher maintenance
```python
# Load vocab.json + merges.txt manually
# Implement BPE algorithm from scratch
```

## Files That Need Real Implementation

### `model_router.py` - ChatEngine class
- [ ] `_simple_tokenize()` → Real tokenizer implementation
- [ ] `_simple_detokenize()` → Real vocab-based detokenization  
- [ ] `_generate_with_fallback()` → Iterative ONNX text generation
- [ ] Add proper input/output shape handling
- [ ] Remove all placeholder pattern matching

### Required Model Files Investigation
- [ ] Check what tokenizer files exist in `models/phi-3-mini-4k/`
- [ ] Identify input names, shapes from ONNX model
- [ ] Verify if attention_mask, position_ids needed

## Testing Strategy
1. **Unit Tests**: Test tokenization roundtrip (text → tokens → text)
2. **Integration Tests**: Test full generation pipeline
3. **Performance Tests**: Measure NPU vs CPU inference speed
4. **Regression Tests**: Ensure no fake responses slip through

## Success Criteria
- [ ] Generate different responses for "What is 2+5?" vs "What is 4+5?"
- [ ] Handle multi-turn conversations with context
- [ ] Real mathematical reasoning (not hardcoded patterns)
- [ ] Proper text generation with coherent responses
- [ ] NPU acceleration working for text generation

## Next Session Action Items
1. **Investigate model files**: Check tokenizer availability in Phi-3 directory
2. **Dependency resolution**: Choose tokenization approach (A/B/C above)
3. **ONNX model inspection**: Get exact input/output specifications
4. **Implement iterative generation**: Replace single-pass inference
5. **Add comprehensive logging**: Track token generation process
6. **Remove all placeholders**: Implement "PLACEHOLDER:" prefix requirement

---
**Status**: CHALLENGES DOCUMENTED - Ready for implementation battle
**Priority**: HIGH - Core functionality depends on this
**Complexity**: HIGH - Requires deep ONNX + NLP knowledge