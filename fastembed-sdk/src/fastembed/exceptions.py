"""
FastEmbed SDK Exceptions
Custom exception classes for better error handling
"""

class FastEmbedError(Exception):
    """Base exception for FastEmbed SDK errors"""
    pass


class FastEmbedConnectionError(FastEmbedError):
    """Raised when connection to FastEmbed server fails"""
    pass


class FastEmbedTimeoutError(FastEmbedError):
    """Raised when request times out"""
    pass


class FastEmbedAPIError(FastEmbedError):
    """Raised when API returns an error response"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class FastEmbedValidationError(FastEmbedError):
    """Raised when input validation fails"""
    pass