# Document Processing System - Complete Architecture

This document contains the full specification for a local, CLI-based document processing system that converts mixed-format files to well-structured Markdown with optional embedding pipeline.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [CLI Interface](#cli-interface)
3. [Configuration](#configuration)
4. [Implementation Guide](#implementation-guide)
5. [Dependencies](#dependencies)
6. [Examples](#examples)

## Architecture Overview

### Design Philosophy
- **Local-first**: No external APIs, completely offline processing
- **CLI-focused**: Simple, scriptable commands, no background services
- **Quality routing**: Best tool per file type with intelligent fallbacks
- **Idempotent**: Content hashing and caching for efficient re-runs
- **Extensible**: Plugin-based converter system

### Core Modules
```
DocumentProcessor/
├── cli/                    # Command-line interface
├── core/
│   ├── router.py          # File type detection + converter selection
│   ├── converter_base.py  # Abstract converter interface
│   ├── cache_manager.py   # Content hashing + SQLite state
│   └── config.py          # Configuration management
├── converters/            # Format-specific adapters
│   ├── pdf_converter.py   # PDF → Markdown (pdfminer.six + fallbacks)
│   ├── docx_converter.py  # DOCX → Markdown (pandoc primary)
│   ├── image_converter.py # Image OCR → Markdown (tesseract)
│   ├── audio_converter.py # Audio STT → Markdown (whisper.cpp)
│   ├── code_converter.py  # Code → Markdown with syntax
│   └── table_converter.py # CSV/JSON → Markdown tables
├── embedding/
│   ├── chunker.py         # Text chunking strategies
│   ├── embedder.py        # ONNX + fastembed integration
│   └── indexer.py         # SQLite vector index
└── utils/
    ├── file_utils.py      # MIME detection, validation
    └── markdown_utils.py  # Output formatting, front matter
```

### Data Flow
```
Input Files → Router → Converter → Markdown → [Optional] Chunker → Embedder → SQLite Index
     ↓           ↓          ↓          ↓                    ↓          ↓
Cache Check → Select → Transform → Validate → [Optional] Chunk → Embed → Store
```

## CLI Interface

### Commands

#### convert
Primary conversion command that processes input directory to markdown.

```bash
doc-processor convert [OPTIONS]

Options:
  --input, -i PATH          Input directory [required]
  --output, -o PATH         Output directory [required]
  --recurse / --no-recurse  Process subdirectories [default: true]
  --include TEXT            Include file patterns (glob)
  --exclude TEXT            Exclude file patterns (glob)
  --concurrency INTEGER     Number of parallel workers [default: 4]
  --overwrite / --no-overwrite  Overwrite existing outputs [default: false]
  --cache / --no-cache      Use caching [default: true]
  --dry-run                 Show what would be processed
  --front-matter [minimal|full|none]  Front matter detail level [default: full]
  --ocr / --no-ocr         Enable OCR for images [default: false]
  --stt / --no-stt         Enable speech-to-text [default: false]
  --max-file-size TEXT     Maximum file size to process [default: 100MB]
  --fail-fast / --continue-on-error  Stop on first error [default: continue]
  --embed / --no-embed     Generate embeddings [default: false]
  --index-path PATH        SQLite index path for embeddings
```

#### embed
Generate embeddings for existing markdown files.

```bash
doc-processor embed [OPTIONS]

Options:
  --md-root PATH           Markdown files root directory [required]
  --index-path PATH        SQLite index file path [required]
  --chunk-size INTEGER     Text chunk size in tokens [default: 512]
  --chunk-overlap INTEGER  Overlap between chunks [default: 50]
  --model TEXT             Embedding model path [default: all-MiniLM-L6-v2]
  --batch-size INTEGER     Embedding batch size [default: 32]
  --overwrite / --no-overwrite  Rebuild existing embeddings [default: false]
```

#### index
Inspect and manage the embedding index.

```bash
doc-processor index [OPTIONS] COMMAND

Commands:
  stats     Show index statistics
  search    Search the index
  repair    Check and repair index integrity
  export    Export embeddings to file
```

#### clean
Remove outputs and cache files.

```bash
doc-processor clean [OPTIONS]

Options:
  --outputs / --keep-outputs    Remove output files [default: false]
  --cache / --keep-cache        Remove cache files [default: false]
  --index / --keep-index        Remove index files [default: false]
  --confirm / --no-confirm      Confirm before deletion [default: true]
```

#### doctor
Check system dependencies and configuration.

```bash
doc-processor doctor [OPTIONS]

Options:
  --fix / --no-fix         Attempt to fix issues [default: false]
  --verbose / --quiet      Detailed output [default: false]
```

### Example Commands

```bash
# 1. Basic conversion
doc-processor convert --input ./documents --output ./markdown

# 2. Convert with OCR and speech-to-text
doc-processor convert \
  --input ./mixed-docs \
  --output ./converted \
  --ocr --stt \
  --include "*.pdf,*.docx,*.jpg,*.mp3"

# 3. Build searchable knowledge base
doc-processor convert \
  --input ./company-docs \
  --output ./kb-markdown \
  --embed \
  --index-path ./knowledge-base.db \
  --chunk-size 256

# 4. Large file processing
doc-processor convert \
  --input ./archives \
  --output ./processed \
  --max-file-size 1GB \
  --concurrency 2 \
  --exclude "*.tmp,*.bak"

# 5. Dry run to preview processing
doc-processor convert \
  --input ./test-docs \
  --output ./preview \
  --dry-run \
  --front-matter minimal
```

## Configuration

### config.yaml
```yaml
# Converter priorities and settings
converters:
  pdf:
    primary: "pdfminer"
    fallbacks: ["pdfplumber", "ocrmypdf"]
    ocr_threshold: 0.8
    extract_images: true
  
  docx:
    primary: "pandoc"
    fallbacks: ["python-docx", "markitdown"]
    preserve_comments: false
  
  html:
    primary: "pandoc"
    fallbacks: ["beautifulsoup"]
    clean_html: true
  
  images:
    primary: "tesseract"
    fallbacks: ["easyocr"]
    languages: ["eng", "spa", "fra"]
    dpi: 300
  
  audio:
    primary: "whisper-cpp"
    model: "base.en"
    max_duration: 3600
    include_timestamps: true
  
  code:
    preserve_syntax: true
    extract_docstrings: true
    highlight_language: true

# Output formatting
output:
  preserve_structure: true
  front_matter: "full"  # minimal|full|none
  asset_folder: "_assets"
  markdown_dialect: "github"  # github|commonmark|pandoc
  line_ending: "lf"  # lf|crlf|auto
  
# Embedding configuration
embeddings:
  enabled: false
  model_path: "models/all-MiniLM-L6-v2"
  model_type: "sentence-transformers"  # sentence-transformers|onnx
  chunk_size: 512
  chunk_overlap: 50
  batch_size: 32
  similarity_threshold: 0.7

# Performance settings
processing:
  concurrency: 4
  max_file_size: "100MB"
  memory_limit: "2GB"
  timeout_per_file: 300  # seconds
  
# Caching
cache:
  enabled: true
  directory: ".doc-processor-cache"
  max_size: "1GB"
  ttl_days: 30

# Logging
logging:
  level: "INFO"  # DEBUG|INFO|WARNING|ERROR|CRITICAL
  file: "doc-processor.log"
  max_size: "10MB"
  backup_count: 5

# File patterns
ignore:
  - "*.tmp"
  - "*.bak"
  - ".git/**"
  - "node_modules/**"
  - "__pycache__/**"
  - ".DS_Store"

include_by_default:
  - "*.pdf"
  - "*.docx"
  - "*.doc"
  - "*.html"
  - "*.htm"
  - "*.txt"
  - "*.md"
  - "*.csv"
  - "*.json"
  - "*.xml"
  - "*.png"
  - "*.jpg"
  - "*.jpeg"
  - "*.gif"
  - "*.mp3"
  - "*.wav"
  - "*.m4a"
  - "*.py"
  - "*.js"
  - "*.ts"
  - "*.java"
  - "*.cpp"
  - "*.c"
  - "*.h"
```

### CLI Flag Override
Command-line flags override configuration file settings:
```bash
# Config has concurrency: 4, this sets it to 8
doc-processor convert --input ./docs --output ./md --concurrency 8

# Config has cache.enabled: true, this disables it
doc-processor convert --input ./docs --output ./md --no-cache
```

## Implementation Guide

### File Type Routing Matrix

| Extension | Primary Tool | Fallback 1 | Fallback 2 | Confidence Threshold |
|-----------|--------------|------------|------------|---------------------|
| .pdf | pdfminer.six | pdfplumber | ocrmypdf+tesseract | text_coverage > 0.8 |
| .docx | pandoc | python-docx | markitdown | exit_code == 0 |
| .html | pandoc | beautifulsoup4 | html2text | valid_structure |
| .jpg/.png | tesseract | easyocr | - | confidence > 0.6 |
| .mp3/.wav | whisper.cpp | faster-whisper | - | duration < 3600s |
| .py/.js | pygments | plain_text | - | valid_syntax |
| .csv | pandas | plain_text | - | valid_parse |
| .json | json.loads | plain_text | - | valid_json |

### Output Conventions

#### Directory Structure Preservation
```
Input:                     Output:
documents/                 markdown/
├── reports/              ├── reports/
│   ├── q1.pdf           │   ├── q1.md
│   └── charts/          │   └── charts/
│       └── sales.png    │       └── sales.md
└── meetings/             ├── meetings/
    └── notes.docx        │   └── notes.md
                          └── _assets/
                              ├── q1/
                              │   ├── chart1.png
                              │   └── table1.csv
                              └── sales/
                                  └── sales-original.png
```

#### Markdown Front Matter
```yaml
---
# Required fields
source_path: "documents/reports/annual-report.pdf"
original_filename: "annual-report.pdf"
content_hash: "sha256:a1b2c3d4e5f6..."
converter: "pdfminer.six"
converted_at: "2025-09-21T10:30:00Z"

# File metadata
file_size: 2547890
mime_type: "application/pdf"

# Format-specific metadata
pages: 45                    # PDF
word_count: 5420            # Text documents
duration_seconds: 180       # Audio files
dimensions: "1920x1080"     # Images
language: "en"              # OCR/STT detected

# Extraction details
extraction_notes: "2 tables converted, 1 chart OCR'd"
confidence_score: 0.92
fallback_used: false

# Optional document metadata
metadata:
  title: "Annual Report 2023"
  author: "Finance Team"
  created: "2023-12-15"
  subject: "Financial Performance"
  keywords: ["revenue", "growth", "analysis"]
---
```

### Caching Strategy

#### Content Hashing
```python
def get_file_hash(filepath: Path) -> str:
    """Generate SHA-256 hash of file content"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_config_hash(config: dict) -> str:
    """Generate hash of converter configuration"""
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode()).hexdigest()
```

#### Cache Database Schema
```sql
-- SQLite cache database
CREATE TABLE file_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    output_path TEXT,
    converter_used TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    processing_time_ms INTEGER,
    file_size INTEGER,
    UNIQUE(source_path, content_hash, config_hash)
);

CREATE INDEX idx_source_path ON file_cache(source_path);
CREATE INDEX idx_content_hash ON file_cache(content_hash);
CREATE INDEX idx_processed_at ON file_cache(processed_at);
```

### Error Handling

#### Error Categories
```python
class ConversionError(Exception):
    """Base class for conversion errors"""
    pass

class UnsupportedFormatError(ConversionError):
    """File format not supported by any converter"""
    pass

class ConverterFailedError(ConversionError):
    """Primary converter failed, trying fallback"""
    pass

class AllConvertersFailedError(ConversionError):
    """All converters failed for this file"""
    pass

class FileSizeError(ConversionError):
    """File exceeds maximum size limit"""
    pass

class PermissionError(ConversionError):
    """Cannot read input or write output file"""
    pass
```

#### Error Recovery
```python
def process_with_fallbacks(file_path: Path, converters: list) -> ConversionResult:
    """Try converters in order until one succeeds"""
    errors = []
    
    for converter in converters:
        try:
            result = converter.convert(file_path)
            if result.success:
                return result
        except Exception as e:
            errors.append(f"{converter.name}: {str(e)}")
            logger.warning(f"Converter {converter.name} failed for {file_path}: {e}")
    
    # All converters failed
    error_summary = "; ".join(errors)
    return ConversionResult(
        success=False,
        error=f"All converters failed: {error_summary}"
    )
```

## Dependencies

### System Requirements
- **Python**: 3.8+
- **Operating System**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space for models and cache

### System Dependencies

#### Windows (PowerShell as Administrator)
```powershell
# Chocolatey package manager (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install dependencies
choco install tesseract pandoc ffmpeg poppler

# Add to PATH if needed
$env:PATH += ";C:\Program Files\Tesseract-OCR"
```

#### macOS
```bash
# Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install tesseract pandoc ffmpeg poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    pandoc \
    ffmpeg \
    poppler-utils \
    python3-dev \
    python3-pip
```

### Python Dependencies
```bash
# Core requirements
pip install click>=8.0.0
pip install pyyaml>=6.0
pip install requests>=2.28.0

# Document processing
pip install pdfminer.six>=20220524
pip install pdfplumber>=0.7.0
pip install python-docx>=0.8.11
pip install beautifulsoup4>=4.11.0
pip install html2text>=2020.1.16
pip install pandas>=1.5.0
pip install tabulate>=0.9.0

# OCR and images
pip install Pillow>=9.0.0
pip install pytesseract>=0.3.10
pip install opencv-python>=4.6.0

# Audio processing
pip install whisper-cpp-python>=0.1.0
# Alternative: pip install faster-whisper>=0.8.0

# Embeddings (ONNX)
pip install sentence-transformers>=2.2.0
pip install onnxruntime>=1.19.0
# For your FastEmbed integration
pip install fastembed>=0.1.0

# Utilities
pip install tqdm>=4.64.0
pip install rich>=12.0.0  # Better CLI output
pip install watchdog>=2.1.0  # File watching
```

### Optional Dependencies
```bash
# Better OCR (requires PyTorch)
pip install easyocr>=1.6.0

# Microsoft MarkItDown
pip install markitdown>=0.1.0

# Advanced PDF processing
pip install pymupdf>=1.21.0  # PyMuPDF for complex layouts

# Code syntax highlighting
pip install pygments>=2.13.0
```

## Examples

### Basic Usage Walkthrough

#### 1. Setup and Doctor Check
```bash
# Install the tool
pip install doc-processor

# Check system readiness
doc-processor doctor
```

Expected output:
```
✅ Python 3.9.7 found
✅ Tesseract 5.2.0 found
✅ Pandoc 2.19.2 found
✅ FFmpeg 5.1.1 found
❌ Whisper.cpp not found - install for audio processing
✅ All required Python packages installed
✅ Write permissions in current directory

Status: Ready (1 optional dependency missing)
```

#### 2. Process Mixed Document Folder
```bash
# Sample input folder
test-docs/
├── financial-report.pdf     # 12-page PDF with tables
├── presentation.docx        # PowerPoint export
├── customer-data.csv        # 1000 rows of data
├── architecture-diagram.png # Technical diagram
├── meeting-recording.mp3    # 15-minute audio
└── analysis.py             # Python script with docstrings

# Convert everything
doc-processor convert \
  --input ./test-docs \
  --output ./converted \
  --ocr --stt \
  --front-matter full \
  --concurrency 3
```

Expected output:
```
Processing 6 files in test-docs/...

✅ financial-report.pdf → financial-report.md (pdfminer.six, 2.3s)
✅ presentation.docx → presentation.md (pandoc, 0.8s)
✅ customer-data.csv → customer-data.md (pandas, 0.1s)
✅ architecture-diagram.png → architecture-diagram.md (tesseract, 1.2s)
✅ meeting-recording.mp3 → meeting-recording.md (whisper.cpp, 45.3s)
✅ analysis.py → analysis.md (pygments, 0.1s)

Summary:
  Processed: 6 files
  Success: 6 files
  Failed: 0 files
  Total time: 49.8s
  Cache hits: 0
```

#### 3. Generated Output Structure
```
converted/
├── financial-report.md
├── presentation.md
├── customer-data.md
├── architecture-diagram.md
├── meeting-recording.md
├── analysis.md
└── _assets/
    ├── financial-report/
    │   ├── chart1.png
    │   ├── chart2.png
    │   └── table1.csv
    ├── architecture-diagram/
    │   └── architecture-diagram-original.png
    └── meeting-recording/
        └── meeting-recording.wav
```

#### 4. Sample Generated Markdown

**financial-report.md**:
```markdown
---
source_path: "test-docs/financial-report.pdf"
original_filename: "financial-report.pdf"
content_hash: "sha256:f4a3b2c1d5e6..."
converter: "pdfminer.six"
converted_at: "2025-09-21T15:30:45Z"
file_size: 3247891
pages: 12
extraction_notes: "5 tables extracted, 3 charts converted to images"
confidence_score: 0.95
metadata:
  title: "Q3 2023 Financial Report"
  author: "Finance Department"
  created: "2023-10-01"
  subject: "Quarterly Financial Analysis"
---

# Q3 2023 Financial Report

## Executive Summary

Revenue for Q3 2023 reached $4.2M, representing a 15% increase over Q2 2023 and a 23% year-over-year growth.

## Revenue Breakdown

| Product Line | Q2 2023 | Q3 2023 | Growth |
|--------------|---------|---------|---------|
| SaaS Platform | $2.1M | $2.4M | +14.3% |
| Professional Services | $1.2M | $1.5M | +25.0% |
| Hardware Sales | $0.4M | $0.3M | -25.0% |

![Revenue Chart](_assets/financial-report/chart1.png)

## Key Metrics

- Customer acquisition cost: $142 (down from $156)
- Monthly recurring revenue: $1.8M (up 18%)
- Churn rate: 2.1% (improved from 2.8%)

[Additional tables and charts extracted to _assets/financial-report/]
```

**architecture-diagram.md**:
```markdown
---
source_path: "test-docs/architecture-diagram.png"
original_filename: "architecture-diagram.png"
content_hash: "sha256:a8b9c7d2e1f0..."
converter: "tesseract"
converted_at: "2025-09-21T15:31:20Z"
file_size: 245760
dimensions: "1920x1080"
ocr_confidence: 0.87
language: "en"
---

# System Architecture Diagram

## OCR Extracted Text

### Components Identified
- **User Interface Layer**
  - Web Frontend (React)
  - Mobile App (React Native)
  - Admin Dashboard

- **API Gateway**
  - Authentication Service
  - Rate Limiting
  - Request Routing

- **Microservices**
  - User Service
  - Payment Service
  - Notification Service
  - Analytics Service

- **Data Layer**
  - PostgreSQL (Primary DB)
  - Redis (Cache)
  - S3 (File Storage)

- **Infrastructure**
  - Kubernetes Cluster
  - Load Balancer
  - Monitoring (Prometheus)

![Original Architecture Diagram](_assets/architecture-diagram/architecture-diagram-original.png)

*Note: This text was extracted via OCR. Refer to the original image for complete accuracy.*
```

#### 5. Build Searchable Knowledge Base
```bash
# Convert with embeddings
doc-processor convert \
  --input ./company-docs \
  --output ./knowledge-base \
  --embed \
  --index-path ./company-kb.db \
  --chunk-size 256 \
  --chunk-overlap 50
```

Expected output:
```
Processing 45 files in company-docs/...

✅ 45 files converted to markdown
✅ 342 text chunks generated
✅ Embeddings created using all-MiniLM-L6-v2
✅ SQLite index built: company-kb.db (15.2MB)

Knowledge base ready for search!
```

#### 6. Search the Knowledge Base
```bash
# Search for information
doc-processor index search \
  --index-path ./company-kb.db \
  --query "quarterly revenue growth" \
  --limit 5
```

Expected output:
```
Top 5 results for "quarterly revenue growth":

1. financial-report.md (score: 0.92)
   "Revenue for Q3 2023 reached $4.2M, representing a 15% increase over Q2..."
   
2. board-presentation.md (score: 0.85)
   "Our quarterly growth trajectory shows consistent improvement across all..."
   
3. investor-update.md (score: 0.78)
   "Key performance indicators demonstrate strong revenue momentum with..."

[Additional results...]
```

### Advanced Usage Examples

#### Large File Processing
```bash
# Process large archive with size limits and streaming
doc-processor convert \
  --input ./archive-2023 \
  --output ./processed-archive \
  --max-file-size 500MB \
  --concurrency 2 \
  --exclude "*.backup,*.tmp" \
  --fail-fast \
  --verbose
```

#### Selective Processing
```bash
# Only process specific file types
doc-processor convert \
  --input ./mixed-content \
  --output ./filtered-output \
  --include "*.pdf,*.docx" \
  --exclude "*confidential*,*draft*" \
  --dry-run
```

#### Configuration-driven Processing
```bash
# Use custom configuration
doc-processor convert \
  --input ./documents \
  --output ./markdown \
  --config ./custom-config.yaml \
  --overwrite
```

This completes the comprehensive documentation for the document processing system. The architecture provides a solid foundation for local, offline document conversion with optional embedding capabilities integrated with your existing FastEmbed infrastructure.