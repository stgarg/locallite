"""
Smart alternative to python-magic using filetype library
Works better on ARM64 Windows without libmagic compilation
"""

try:
    import filetype
    FILETYPE_AVAILABLE = True
except ImportError:
    FILETYPE_AVAILABLE = False

import mimetypes
from pathlib import Path

class SmartMagic:
    """Smart alternative to python-magic.Magic()"""
    
    def __init__(self):
        self.mime_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'txt': 'text/plain',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'tiff': 'image/tiff',
            'tif': 'image/tiff',
            'bmp': 'image/bmp',
            'webp': 'image/webp'
        }
    
    def from_file(self, file_path):
        """Get MIME type from file"""
        if FILETYPE_AVAILABLE:
            # Use filetype library (more accurate)
            kind = filetype.guess(file_path)
            if kind:
                return kind.mime
        
        # Fallback 1: mimetypes module
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        
        # Fallback 2: extension mapping
        ext = Path(file_path).suffix.lower().lstrip('.')
        return self.mime_map.get(ext, 'application/octet-stream')
    
    def from_buffer(self, buffer):
        """Get MIME type from buffer"""
        if FILETYPE_AVAILABLE:
            kind = filetype.guess(buffer)
            if kind:
                return kind.mime
        return 'application/octet-stream'

# Global instance
Magic = SmartMagic

def magic_from_file(file_path):
    """Compatibility function"""
    return SmartMagic().from_file(file_path)
