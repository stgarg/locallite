# Import Patterns Learnings

**Date**: September 24, 2025  
**Context**: Task 1 - Shared Service Layer Implementation

## 🔍 **Key Learning: Absolute vs Relative Imports**

### **Issue Encountered**
When creating the shared services in `ai-gateway/src/services/`, initially used relative imports:

```python
# ❌ This failed
from ..embedding_engine import OptimizedEmbeddingEngine
from ..model_router import UnifiedRequest, RequestType
```

**Error**: `ImportError: attempted relative import beyond top-level package`

### **Solution Applied**
Changed to absolute imports:

```python
# ✅ This worked
from embedding_engine import OptimizedEmbeddingEngine
from model_router import UnifiedRequest, RequestType
```

### **Root Cause Analysis**
1. **Package Structure**: The `src` directory is not a proper Python package
2. **Execution Context**: When running `python main.py` from `src/`, Python treats `src` as the root
3. **Relative Import Limitation**: `..` tries to go beyond the top-level package scope

### **Current Project Structure**
```
ai-gateway/src/
├── main.py                    # Entry point
├── embedding_engine.py        # Core engine
├── model_router.py           # Model routing
└── services/                 # NEW: Shared services
    ├── __init__.py
    ├── embedding_service.py   # Uses absolute imports
    ├── chat_service.py        # Uses absolute imports  
    ├── model_service.py       # Uses absolute imports
    └── metrics_service.py     # Standalone service
```

## 📋 **Import Pattern Guidelines**

### **For This Project Structure**
- ✅ **Use absolute imports** within the `src` directory
- ✅ **Services import sibling modules** directly: `from embedding_engine import ...`
- ✅ **Main.py imports services** via: `from services import ...`

### **Future Considerations**
When restructuring the project, consider:

1. **Option 1: Proper Package Structure**
```
fastembed_gateway/
├── __init__.py
├── main.py
├── core/
│   ├── __init__.py
│   ├── embedding_engine.py
│   └── model_router.py
└── services/
    ├── __init__.py
    └── ...
```

2. **Option 2: Add `src` to PYTHONPATH**
```python
# At top of main.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
```

## 🎯 **Current Status**
- ✅ All services use absolute imports and work correctly
- ✅ Import structure is consistent across the codebase
- ✅ No import errors when running the application

## 🚀 **Action Items**
- [ ] Consider restructuring to proper package when refactoring
- [ ] Document import patterns for new team members
- [ ] Keep consistent absolute import pattern for current architecture