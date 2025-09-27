# Repository Development Guidelines

## Placeholder Message Policy

**CRITICAL RULE**: All placeholder or template responses in code must be clearly marked and never presented as real AI inference.

### Required Placeholder Format:
```python
# ❌ WRONG - Deceptive fake responses
return "I'm your local AI assistant powered by Phi-3 Mini"
return "That's an interesting question. I'm running locally..."

# ✅ CORRECT - Clearly marked placeholders
return "PLACEHOLDER: Simulated response - real ONNX inference not implemented"
return "PLACEHOLDER: Math calculation would happen here"
```

### Implementation Rules:

1. **All non-inference responses MUST start with "PLACEHOLDER:"**
2. **Include reason why it's a placeholder**
3. **Reference what real implementation should do**
4. **Never claim to be "AI inference" when using templates**

### Examples:

```python
# Template/fallback responses
if pattern_match(user_input):
    return "PLACEHOLDER: Pattern-matched response. Real implementation needs ONNX text generation with proper tokenization."

# Error fallbacks  
except OnnxInferenceError as e:
    return f"PLACEHOLDER: ONNX inference failed ({e}). Would show real model response when properly implemented."

# Unimplemented features
if feature_not_ready:
    return "PLACEHOLDER: Feature under development. Real Phi-3 ONNX inference coming soon."
```

## Code Quality Standards

### AI/ML Implementation:
- **Real inference only**: Never fake model outputs
- **Proper error handling**: Graceful failures with clear messages  
- **Performance logging**: Track actual inference times
- **Resource monitoring**: NPU/CPU usage tracking

### Testing Requirements:
- **End-to-end tests**: Verify real model inference
- **No hardcoded responses**: Test with varied inputs
- **Performance benchmarks**: NPU vs CPU comparison
- **Error scenario coverage**: Handle all failure modes

## Documentation Standards

### For AI Components:
- **Clearly state current limitations**
- **Document placeholder vs real functionality**
- **Provide implementation roadmap**
- **Include performance characteristics**

---
**Purpose**: Maintain development integrity and user trust
**Enforcement**: Code reviews must verify placeholder compliance
**Updated**: September 2025