"""
Custom Exception Classes

This module defines custom exception classes for the application.
These exceptions provide specific error handling and can be caught
and handled appropriately in different layers of the application.
"""


class BaseException(Exception):
    """Base exception class for the application."""
    pass


class DatabaseError(BaseException):
    """Raised when a database operation fails."""
    pass


class UserNotFoundError(BaseException):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsError(BaseException):
    """Raised when trying to create a user that already exists."""
    pass


class ProductNotFoundError(BaseException):
    """Raised when a product is not found."""
    pass


class ProductAlreadyExistsError(BaseException):
    """Raised when trying to create a product that already exists."""
    pass


class OrderNotFoundError(BaseException):
    """Raised when an order is not found."""
    pass


class InsufficientStockError(BaseException):
    """Raised when there is insufficient stock for an order."""
    
    def __init__(self, message: str, details: list = None):
        super().__init__(message)
        self.details = details or []


class InvalidOrderError(BaseException):
    """Raised when order data is invalid."""
    pass


class PermissionError(BaseException):
    """Raised when user doesn't have permission to perform an action."""
    pass


class AuthenticationError(BaseException):
    """Raised when authentication fails."""
    pass


class ValidationError(BaseException):
    """Raised when data validation fails."""
    pass
