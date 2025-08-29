"""
Comprehensive error handling utilities for the Places Management System.

This module provides centralized error handling, custom exceptions, and error
reporting mechanisms with proper logging and user-friendly error messages.
"""

import traceback
import sys
from typing import Any, Callable, Optional, Dict, Union, Type
from functools import wraps
from dataclasses import dataclass
from enum import Enum

# Import logging utilities
try:
    from utils.logger import get_logger
    import streamlit as st
except ImportError:
    # Fallback logger if not available
    class FallbackLogger:
        def debug(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
        def info(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
        def warning(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
        def error(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
        def critical(self, msg, **kwargs): 
            # Fallback logger - no operation implementation
            pass
    
    def get_logger(_name):
        # Fallback function - parameter name ignored
        return FallbackLogger()
    
    # Mock streamlit if not available
    class MockStreamlit:
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
    
    st = MockStreamlit()

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification."""
    
    DATABASE = "database"
    VALIDATION = "validation"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    USER_INPUT = "user_input"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for an error."""
    
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary."""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'operation': self.operation,
            'additional_data': self.additional_data or {}
        }


# Custom Exception Classes
class PlacesAppException(Exception):
    """Base exception for the Places Management application."""
    
    def __init__(
        self, 
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize Places application exception.
        
        Args:
            message: Human-readable error message
            category: Error category for classification
            severity: Error severity level
            context: Additional context information
            original_exception: The original exception if this is a wrapper
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
        self.original_exception = original_exception
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            'type': self.__class__.__name__,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'context': self.context.to_dict(),
            'original_exception': str(self.original_exception) if self.original_exception else None
        }


class DatabaseError(PlacesAppException):
    """Database-related errors."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            context=context,
            original_exception=original_exception
        )


class ValidationError(PlacesAppException):
    """Validation-related errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, context: Optional[ErrorContext] = None):
        if field:
            message = f"Validation error for field '{field}': {message}"
        
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            context=context
        )
        self.field = field


class ConfigurationError(PlacesAppException):
    """Configuration-related errors."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            context=context
        )


class NetworkError(PlacesAppException):
    """Network-related errors."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            original_exception=original_exception
        )


class FileSystemError(PlacesAppException):
    """File system related errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, context: Optional[ErrorContext] = None):
        if file_path:
            message = f"File system error for '{file_path}': {message}"
        
        super().__init__(
            message,
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            context=context
        )
        self.file_path = file_path


class ErrorHandler:
    """Centralized error handling class."""
    
    def __init__(self):
        """Initialize error handler."""
        self.logger = get_logger(__name__)
        self._error_count = 0
        self._error_history = []
    
    def handle_exception(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None,
        show_user_message: bool = True,
        user_message: Optional[str] = None
    ) -> None:
        """
        Handle an exception with proper logging and user notification.
        
        Args:
            exception: The exception to handle
            context: Additional context information
            show_user_message: Whether to show message to user via Streamlit
            user_message: Custom user message (if not provided, will be generated)
        """
        self._error_count += 1
        
        # Determine if this is a custom exception or standard exception
        if isinstance(exception, PlacesAppException):
            error_dict = exception.to_dict()
            error_dict['context'].update(context.to_dict() if context else {})
        else:
            # Wrap standard exception
            wrapped_exception = PlacesAppException(
                message=str(exception),
                category=self._categorize_exception(exception),
                severity=self._determine_severity(exception),
                context=context,
                original_exception=exception
            )
            error_dict = wrapped_exception.to_dict()
        
        # Log the error
        self.logger.error(
            f"Exception handled: {error_dict['type']} - {error_dict['message']}",
            category=error_dict['category'],
            severity=error_dict['severity'],
            context=error_dict['context']
        )
        
        # Log full traceback for debugging
        if self.logger.logger.isEnabledFor(10):  # DEBUG level
            self.logger.error(
                f"Full traceback for {error_dict['type']}",
                exc_info=exception
            )
        
        # Add to error history
        self._error_history.append(error_dict)
        
        # Keep only last 100 errors
        if len(self._error_history) > 100:
            self._error_history.pop(0)
        
        # Show user message if requested
        if show_user_message:
            display_message = user_message or self._generate_user_message(exception)
            self._display_user_message(exception, display_message)
    
    def _categorize_exception(self, exception: Exception) -> ErrorCategory:
        """Categorize a standard exception."""
        exception_type = type(exception).__name__
        
        category_mapping = {
            'ConnectionError': ErrorCategory.NETWORK,
            'TimeoutError': ErrorCategory.NETWORK,
            'DatabaseError': ErrorCategory.DATABASE,
            'OperationalError': ErrorCategory.DATABASE,
            'IntegrityError': ErrorCategory.DATABASE,
            'FileNotFoundError': ErrorCategory.FILE_SYSTEM,
            'PermissionError': ErrorCategory.FILE_SYSTEM,
            'ValueError': ErrorCategory.VALIDATION,
            'TypeError': ErrorCategory.VALIDATION,
            'KeyError': ErrorCategory.CONFIGURATION,
            'AttributeError': ErrorCategory.CONFIGURATION,
        }
        
        return category_mapping.get(exception_type, ErrorCategory.UNKNOWN)
    
    def _determine_severity(self, exception: Exception) -> ErrorSeverity:
        """Determine severity of a standard exception."""
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return ErrorSeverity.HIGH
        elif isinstance(exception, (ValueError, TypeError)):
            return ErrorSeverity.LOW
        elif isinstance(exception, (FileNotFoundError, PermissionError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.MEDIUM
    
    def _generate_user_message(self, exception: Exception) -> str:
        """Generate a user-friendly error message."""
        if isinstance(exception, PlacesAppException):
            return exception.message
        
        # Generate user-friendly messages for common exceptions
        exception_type = type(exception).__name__
        
        user_messages = {
            'ConnectionError': "Unable to connect to the database. Please check your internet connection and try again.",
            'TimeoutError': "The operation timed out. Please try again later.",
            'FileNotFoundError': "A required file was not found. Please contact support.",
            'PermissionError': "Permission denied. Please check your access rights.",
            'ValueError': "Invalid input provided. Please check your data and try again.",
            'TypeError': "Invalid data type provided. Please check your input.",
            'KeyError': "Missing required configuration. Please contact support.",
        }
        
        return user_messages.get(exception_type, 
                               "An unexpected error occurred. Please try again or contact support if the problem persists.")
    
    def _display_user_message(self, exception: Exception, message: str) -> None:
        """Display error message to user via Streamlit."""
        try:
            if isinstance(exception, PlacesAppException):
                if exception.severity == ErrorSeverity.CRITICAL:
                    st.error(f"🚨 Critical Error: {message}")
                elif exception.severity == ErrorSeverity.HIGH:
                    st.error(f"❌ Error: {message}")
                elif exception.severity == ErrorSeverity.MEDIUM:
                    st.warning(f"⚠️ Warning: {message}")
                else:  # LOW
                    st.info(f"ℹ️ Info: {message}")
            else:
                st.error(f"❌ Error: {message}")
        except Exception as display_error:
            # Fallback if Streamlit is not available
            self.logger.error(f"Failed to display user message: {display_error}")
            print(f"ERROR: {message}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        if not self._error_history:
            return {
                'total_errors': 0,
                'by_category': {},
                'by_severity': {},
                'recent_errors': []
            }
        
        by_category = {}
        by_severity = {}
        
        for error in self._error_history:
            category = error.get('category', 'unknown')
            severity = error.get('severity', 'medium')
            
            by_category[category] = by_category.get(category, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_errors': len(self._error_history),
            'by_category': by_category,
            'by_severity': by_severity,
            'recent_errors': self._error_history[-10:]  # Last 10 errors
        }


# Global error handler instance
error_handler = ErrorHandler()


# Decorator functions
def handle_errors(
    show_user_message: bool = True,
    user_message: Optional[str] = None,
    reraise: bool = False,
    default_return: Any = None
):
    """
    Decorator to automatically handle errors in functions.
    
    Args:
        show_user_message: Whether to show error message to user
        user_message: Custom user message
        reraise: Whether to reraise the exception after handling
        default_return: Default value to return if exception occurs and not reraising
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=f"{func.__module__}.{func.__name__}",
                    additional_data={'args_count': len(args), 'kwargs_keys': list(kwargs.keys())}
                )
                
                error_handler.handle_exception(
                    e,
                    context=context,
                    show_user_message=show_user_message,
                    user_message=user_message
                )
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def handle_database_errors(func: Callable) -> Callable:
    """Decorator specifically for database operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = ErrorContext(
                operation=f"database.{func.__name__}",
                additional_data={'function': func.__name__}
            )
            
            # Convert to database error
            db_error = DatabaseError(
                f"Database operation '{func.__name__}' failed: {str(e)}",
                context=context,
                original_exception=e
            )
            
            error_handler.handle_exception(db_error)
            return None  # Default return for failed database operations
    
    return wrapper


def handle_validation_errors(func: Callable) -> Callable:
    """Decorator specifically for validation operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = ErrorContext(
                operation=f"validation.{func.__name__}",
                additional_data={'function': func.__name__}
            )
            
            # Convert to validation error
            validation_error = ValidationError(
                f"Validation '{func.__name__}' failed: {str(e)}",
                context=context
            )
            
            error_handler.handle_exception(validation_error)
            return False  # Default return for failed validation
    
    return wrapper


# Utility functions
def log_and_raise(
    exception_class: Type[PlacesAppException],
    message: str,
    context: Optional[ErrorContext] = None,
    original_exception: Optional[Exception] = None
) -> None:
    """
    Log an error and raise a custom exception.
    
    Args:
        exception_class: The custom exception class to raise
        message: Error message
        context: Additional context
        original_exception: Original exception if available
    """
    exception = exception_class(message, context=context, original_exception=original_exception)
    error_handler.handle_exception(exception, show_user_message=False)
    raise exception


def safe_execute(
    operation: Callable,
    operation_name: str,
    default_return: Any = None,
    context: Optional[ErrorContext] = None
) -> Any:
    """
    Safely execute an operation with error handling.
    
    Args:
        operation: Function to execute
        operation_name: Name of the operation for logging
        default_return: Value to return if operation fails
        context: Additional context
        
    Returns:
        Result of operation or default_return if failed
    """
    try:
        return operation()
    except Exception as e:
        op_context = context or ErrorContext()
        op_context.operation = operation_name
        
        error_handler.handle_exception(e, context=op_context)
        return default_return


def get_error_statistics() -> Dict[str, Any]:
    """Get current error statistics."""
    return error_handler.get_error_statistics()


# Export all error handling utilities
__all__ = [
    'PlacesAppException',
    'DatabaseError',
    'ValidationError',
    'ConfigurationError',
    'NetworkError',
    'FileSystemError',
    'ErrorHandler',
    'ErrorContext',
    'ErrorSeverity',
    'ErrorCategory',
    'handle_errors',
    'handle_database_errors',
    'handle_validation_errors',
    'log_and_raise',
    'safe_execute',
    'get_error_statistics',
    'error_handler'
]
