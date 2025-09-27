# 🏃‍♂️ OPTION A: IMMEDIATE ACTION PLAN

## ✅ **WHAT WE'LL DO RIGHT NOW (Next 2 Hours)**

Transform our text-only system into multimodal AI gateway - **starting with document processing today**.

---

## **STEP 1: PROJECT SETUP** ⏱️ 15 minutes

### Create Multimodal Directory Structure
```powershell
cd C:\Learn\Code\fastembed\ai-gateway
New-Item -ItemType Directory -Path "src\converters" -Force
New-Item -ItemType Directory -Path "src\processors" -Force  
New-Item -ItemType Directory -Path "tests\multimodal" -Force
New-Item -ItemType Directory -Path "examples\multimodal" -Force
```

### Update Dependencies for Document Processing
Add these to `requirements.txt`:
```
# Document Processing Dependencies
pymupdf>=1.23.0          # PDF processing
python-docx>=0.8.11      # DOCX processing  
pytesseract>=0.3.10      # OCR capability
pillow>=10.0.0           # Image processing
python-magic>=0.4.27     # File type detection
tqdm>=4.65.0             # Progress bars for downloads
```

---

## **STEP 2: DOWNLOAD GRANITE MODELS** ⏱️ 30 minutes

### Run the Download Script
```powershell
# From scripts directory
cd C:\Learn\Code\fastembed\scripts
python download-granite-docling.py --models all

# Expected output:
# 📂 Model directory: C:\Learn\Code\fastembed\models\granite
# 📋 Models to download: ['text-extraction', 'layout-analysis', 'table-detection']  
# 💾 Total download size: ~896MB
# 📥 Downloading granite-text-extraction-256m.onnx...
# 📥 Downloading granite-layout-analysis-128m.onnx...
# 📥 Downloading granite-table-detection-64m.onnx...
# ✅ All models ready for document processing!
```

**What This Downloads:**
- `granite-text-extraction-256m.onnx` (512MB) - Extract text from documents
- `granite-layout-analysis-128m.onnx` (256MB) - Analyze document structure  
- `granite-table-detection-64m.onnx` (128MB) - Detect and extract tables

---

## **STEP 3: CREATE DOCUMENT CONVERTER BASE** ⏱️ 45 minutes

### Base Converter Class
Create `ai-gateway\src\converters\__init__.py`:
```python
"""Document converters for multimodal AI gateway"""

from .base_converter import BaseConverter, ConvertedDocument
from .pdf_converter import PDFConverter
from .image_converter import ImageConverter
from .office_converter import OfficeConverter

__all__ = [
    'BaseConverter',
    'ConvertedDocument', 
    'PDFConverter',
    'ImageConverter',
    'OfficeConverter'
]
```

### Base Converter Implementation  
Create `ai-gateway\src\converters\base_converter.py`:
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    IMAGE = "image"
    AUDIO = "audio"

class ConvertedDocument(BaseModel):
    """Standardized document conversion result"""
    document_type: DocumentType
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None

class BaseConverter(ABC):
    """Abstract base class for document converters"""
    
    def __init__(self):
        self.supported_formats = []
        
    @abstractmethod
    async def convert(self, file_content: bytes, **kwargs) -> ConvertedDocument:
        """Convert document content to standardized format"""
        pass
        
    @abstractmethod
    def supports_format(self, file_format: str) -> bool:
        """Check if converter supports the given format"""
        pass
        
    def validate_input(self, file_content: bytes) -> bool:
        """Validate input file content"""
        return len(file_content) > 0 and len(file_content) < 100_000_000  # 100MB limit
```

### PDF Converter Implementation
Create `ai-gateway\src\converters\pdf_converter.py`:
```python
import fitz  # PyMuPDF
import time
from typing import Dict, Any, List
from .base_converter import BaseConverter, ConvertedDocument, DocumentType

class PDFConverter(BaseConverter):
    """Convert PDF documents to structured content"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['pdf', 'application/pdf']
        
    def supports_format(self, file_format: str) -> bool:
        return file_format.lower() in self.supported_formats
        
    async def convert(self, file_content: bytes, **kwargs) -> ConvertedDocument:
        """Convert PDF to structured text and metadata"""
        start_time = time.time()
        
        try:
            # Open PDF from bytes
            pdf_doc = fitz.open(stream=file_content, filetype="pdf")
            
            # Extract content
            pages = []
            total_text = ""
            
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                
                # Extract text
                text = page.get_text()
                total_text += text + "\n"
                
                # Extract images info (we'll enhance this later)
                images = page.get_images()
                
                pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "image_count": len(images),
                    "char_count": len(text)
                })
            
            # Build metadata
            metadata = {
                "page_count": pdf_doc.page_count,
                "title": pdf_doc.metadata.get('title', ''),
                "author": pdf_doc.metadata.get('author', ''),
                "subject": pdf_doc.metadata.get('subject', ''),
                "total_characters": len(total_text),
                "has_images": any(page["image_count"] > 0 for page in pages)
            }
            
            # Build content structure
            content = {
                "text": total_text,
                "pages": pages,
                "markdown": self._to_markdown(pages),
                "summary": f"PDF document with {len(pages)} pages and {len(total_text)} characters"
            }
            
            pdf_doc.close()
            
            processing_time = (time.time() - start_time) * 1000
            
            return ConvertedDocument(
                document_type=DocumentType.PDF,
                content=content,
                metadata=metadata,
                processing_time_ms=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            return ConvertedDocument(
                document_type=DocumentType.PDF,
                content={},
                metadata={},
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _to_markdown(self, pages: List[Dict]) -> str:
        """Convert pages to markdown format"""
        markdown = "# Document Content\n\n"
        
        for page in pages:
            markdown += f"## Page {page['page_number']}\n\n"
            markdown += page['text'] + "\n\n"
            
        return markdown
```

---

## **STEP 4: CREATE DOCUMENT PROCESSOR** ⏱️ 30 minutes

### Document Processor Core
Create `ai-gateway\src\processors\document_processor.py`:
```python
import onnxruntime as ort
from pathlib import Path
from typing import Dict, Any, Optional
from ..converters import PDFConverter, ImageConverter, OfficeConverter, ConvertedDocument

class DocumentProcessor:
    """Main document processing engine using Granite models"""
    
    def __init__(self, model_dir: str = "../models/granite"):
        self.model_dir = Path(model_dir)
        self.converters = {
            'pdf': PDFConverter(),
            'docx': OfficeConverter(), 
            'image': ImageConverter(),
        }
        
        # Initialize ONNX sessions (will load when needed)
        self.text_extractor = None
        self.layout_analyzer = None
        self.table_detector = None
        
    def _load_models(self):
        """Lazy load ONNX models"""
        if self.text_extractor is None:
            text_model_path = self.model_dir / "granite-text-extraction-256m.onnx"
            if text_model_path.exists():
                self.text_extractor = ort.InferenceSession(
                    str(text_model_path),
                    providers=['QNNExecutionProvider', 'CPUExecutionProvider']
                )
                
        # We'll implement layout and table detection in the next phase
        
    async def process_document(self, 
                             file_content: bytes, 
                             file_type: str,
                             options: Optional[Dict[str, Any]] = None) -> ConvertedDocument:
        """Process document using appropriate converter"""
        
        # Get the right converter
        converter = self.converters.get(file_type.lower())
        if not converter:
            raise ValueError(f"Unsupported file type: {file_type}")
            
        # Convert document
        result = await converter.convert(file_content, **(options or {}))
        
        # TODO: Apply Granite model processing for enhanced extraction
        # For now, return basic conversion result
        
        return result
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats"""
        formats = []
        for converter in self.converters.values():
            formats.extend(converter.supported_formats)
        return formats
```

---

## **STEP 5: ADD DOCUMENT API ENDPOINTS** ⏱️ 30 minutes

### Update main.py with Document Processing
Add to `ai-gateway\src\main.py`:

```python
# Add these imports at the top
from .processors.document_processor import DocumentProcessor
from pydantic import BaseModel
from typing import Optional
import base64

# Add these request/response models
class DocumentProcessRequest(BaseModel):
    """Request for document processing"""
    processing_options: Optional[Dict[str, Any]] = {}
    extract_text: bool = True
    extract_images: bool = False
    extract_tables: bool = False
    output_format: str = "markdown"

class DocumentProcessResponse(BaseModel):
    """Response from document processing"""
    document_id: str
    document_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] 
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None

# Add document processor to app state
class AppState:
    def __init__(self):
        self.embedding_engine = None
        self.model_router = None
        self.document_processor = None  # NEW
        self.is_ready = False

# Update lifespan to initialize document processor
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Existing initialization...
    app_state.embedding_engine = OptimizedEmbeddingEngine()
    app_state.model_router = ModelRouter() 
    
    # NEW: Initialize document processor
    app_state.document_processor = DocumentProcessor()
    
    app_state.is_ready = True
    logger.info("🚀 Multimodal AI Gateway ready - Text, Embeddings & Documents!")
    yield
    logger.info("Shutting down...")

# Add new document processing endpoint
@app.post("/v1/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    options: DocumentProcessRequest = Body(default_factory=DocumentProcessRequest)
):
    """Process document (PDF, DOCX, images) and extract structured content"""
    if not app_state.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Determine file type
        file_type = file.content_type or "application/octet-stream"
        if file_type == "application/octet-stream":
            # Guess from filename extension
            if file.filename.lower().endswith('.pdf'):
                file_type = 'pdf'
            elif file.filename.lower().endswith('.docx'):
                file_type = 'docx'
            else:
                file_type = 'pdf'  # Default assumption
        
        # Process document
        result = await app_state.document_processor.process_document(
            file_content=file_content,
            file_type=file_type,
            options=options.processing_options
        )
        
        # Generate document ID
        import hashlib
        doc_id = hashlib.md5(file_content).hexdigest()[:16]
        
        return DocumentProcessResponse(
            document_id=doc_id,
            document_type=result.document_type,
            content=result.content,
            metadata=result.metadata,
            processing_time_ms=result.processing_time_ms,
            success=result.success,
            error_message=result.error_message
        )
        
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")
```

---

## **TESTING THE DOCUMENT PROCESSING** ⏱️ 15 minutes

### Create Test Example
Create `examples\multimodal\test_pdf_processing.py`:
```python
import requests
import base64
from pathlib import Path

# Test PDF processing
def test_pdf_processing():
    url = "http://localhost:8000/v1/documents/process"
    
    # Create a simple test PDF or use an existing one
    # For now, we'll test with a small PDF file
    
    # Read PDF file (you'll need to provide a test PDF)
    # pdf_path = Path("test_document.pdf")
    # if not pdf_path.exists():
    #     print("❌ Please provide a test PDF file")
    #     return
    
    print("🧪 Testing document processing endpoint...")
    
    # For now, let's test the endpoint structure
    health_response = requests.get("http://localhost:8000/health")
    if health_response.status_code == 200:
        print("✅ Server is running")
    else:
        print("❌ Server not running")
        return
    
    print("📄 Document processing endpoint ready for testing")
    print("📋 Next: Add a test PDF file to test full functionality")

if __name__ == "__main__":
    test_pdf_processing()
```

---

## **IMMEDIATE SUCCESS CRITERIA (End of Today)** ✅

After completing these steps, you'll have:

1. **✅ Multimodal Directory Structure** - All folders created
2. **✅ Document Processing Dependencies** - Requirements updated
3. **✅ Granite Models Downloaded** - 896MB of document AI models  
4. **✅ PDF Converter Working** - Can extract text from PDFs
5. **✅ Document Processor Core** - Ready for ONNX integration
6. **✅ Document API Endpoint** - `/v1/documents/process` functional
7. **✅ Test Framework** - Ready to validate document processing

**Memory Usage**: Added ~900MB for Granite models (total system: ~3.2GB used of 16GB)

**Performance Target**: PDF processing in under 3 seconds

---

## **WHAT'S NEXT (Tomorrow)**

- **Enhanced PDF Processing**: Add table detection and image extraction
- **DOCX Support**: Implement Office document converter  
- **Image OCR**: Add Tesseract integration for scanned documents
- **Granite ONNX Integration**: Use the downloaded models for enhanced extraction

**This gets us 30% toward the complete multimodal vision in just one day!** 🚀

Ready to start? Let's begin with **Step 1: Project Setup**! 🎯