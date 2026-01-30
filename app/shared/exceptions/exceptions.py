from fastapi import HTTPException
from typing import Any, Dict, Optional


class BaseAppException(HTTPException):
    """Base exception class for application-specific errors"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationError(BaseAppException):
    """Exception for validation errors"""

    def __init__(self, detail: str = "Validation error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(status_code=400, detail=detail, error_code=error_code)


class AuthenticationError(BaseAppException):
    """Exception for authentication errors"""

    def __init__(self, detail: str = "Authentication failed", error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(status_code=401, detail=detail, error_code=error_code)


class AuthorizationError(BaseAppException):
    """Exception for authorization errors"""

    def __init__(self, detail: str = "Insufficient permissions", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(status_code=403, detail=detail, error_code=error_code)


class NotFoundError(BaseAppException):
    """Exception for resource not found errors"""

    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(status_code=404, detail=detail, error_code=error_code)


class ConflictError(BaseAppException):
    """Exception for conflict errors"""

    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT"):
        super().__init__(status_code=409, detail=detail, error_code=error_code)


class InternalServerError(BaseAppException):
    """Exception for internal server errors"""

    def __init__(self, detail: str = "Internal server error", error_code: str = "INTERNAL_ERROR"):
        super().__init__(status_code=500, detail=detail, error_code=error_code)