"""Custom exceptions for LambdaX."""


class LambdaXException(Exception):
    """Base exception for all LambdaX errors."""

    pass


class GuardException(LambdaXException):
    """Raised when a guard encounters an error."""

    pass


class PolicyException(LambdaXException):
    """Raised when policy validation or loading fails."""

    pass


class ValidationException(LambdaXException):
    """Raised when input validation fails."""

    pass


class TimeoutException(LambdaXException):
    """Raised when a guard operation times out."""

    pass
