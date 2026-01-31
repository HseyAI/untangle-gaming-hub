"""
UNTANGLE - Custom Exception Classes
"""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str, status_code: int = 500):
        """
        Initialize application exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            status_code: HTTP status code
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str = None):
        """
        Initialize not found exception.

        Args:
            resource: Name of the resource that wasn't found
            identifier: Optional identifier of the resource
        """
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, "NOT_FOUND", 404)


class ConflictException(AppException):
    """Exception raised when there's a resource conflict (e.g., duplicate mobile number)."""

    def __init__(self, message: str, field: str = None):
        """
        Initialize conflict exception.

        Args:
            message: Description of the conflict
            field: Optional field name that caused the conflict
        """
        self.field = field
        super().__init__(message, "CONFLICT", 409)


class UnauthorizedException(AppException):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication required"):
        """
        Initialize unauthorized exception.

        Args:
            message: Authentication error message
        """
        super().__init__(message, "UNAUTHORIZED", 401)


class ForbiddenException(AppException):
    """Exception raised when user lacks permission."""

    def __init__(self, message: str = "Access denied", required_role: str = None):
        """
        Initialize forbidden exception.

        Args:
            message: Authorization error message
            required_role: Optional role that is required
        """
        self.required_role = required_role
        if required_role:
            message += f". Required role: {required_role}"
        super().__init__(message, "FORBIDDEN", 403)


class ValidationException(AppException):
    """Exception raised for custom validation errors."""

    def __init__(self, message: str, field: str = None):
        """
        Initialize validation exception.

        Args:
            message: Validation error message
            field: Optional field name that failed validation
        """
        self.field = field
        super().__init__(message, "VALIDATION_ERROR", 400)
