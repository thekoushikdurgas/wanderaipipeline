"""
Comprehensive logging utility for the Places Management System.

This module provides centralized logging configuration with debug capabilities,
performance monitoring, and structured logging for better debugging and monitoring.
"""

import logging
import logging.handlers
import time
import functools
import sys
import os
from typing import Any, Callable, Optional, Dict, Union
from datetime import datetime
from pathlib import Path

from utils.settings import logging_config
# Import configuration
# try:
# except ImportError:
#     # Fallback configuration if config module is not available
#     class FallbackLoggingConfig:
#         log_level = "INFO"
#         debug_mode = False
#         log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#         date_format = "%Y-%m-%d %H:%M:%S"
#         log_to_file = False
#         log_file_path = "logs/app.log"
#         log_max_bytes = 10 * 1024 * 1024
#         log_backup_count = 5
#         log_sql_queries = False
#         log_performance = False
    
#     logging_config = FallbackLoggingConfig()


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds color to log levels for console output."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class PerformanceLogger:
    """Utility class for performance monitoring and timing."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize performance logger.
        
        Args:
            logger: The logger instance to use for performance logs
        """
        self.logger = logger
        self._timers: Dict[str, float] = {}
    
    def start_timer(self, operation_name: str) -> None:
        """
        Start timing an operation.
        
        Args:
            operation_name: Name of the operation being timed
        """
        self._timers[operation_name] = time.time()
        if logging_config.log_performance:
            self.logger.debug(f"⏱️ Started timing operation: {operation_name}")
    
    def end_timer(self, operation_name: str, log_level: int = logging.INFO) -> float:
        """
        End timing an operation and log the duration.
        
        Args:
            operation_name: Name of the operation
            log_level: Log level for the timing message
            
        Returns:
            float: Duration in seconds
        """
        if operation_name not in self._timers:
            self.logger.warning(f"⚠️ Timer '{operation_name}' was not started")
            return 0.0
        
        start_time = self._timers.pop(operation_name)
        duration = time.time() - start_time
        
        if logging_config.log_performance:
            self.logger.log(log_level, f"⏱️ Operation '{operation_name}' completed in {duration:.4f}s")
        
        return duration
    
    def time_operation(self, operation_name: str, log_level: int = logging.INFO):
        """
        Decorator for timing function execution.
        
        Args:
            operation_name: Name of the operation
            log_level: Log level for timing messages
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.start_timer(operation_name)
                try:
                    result = func(*args, **kwargs)
                    self.end_timer(operation_name, log_level)
                    return result
                except Exception as e:
                    self.end_timer(operation_name, logging.ERROR)
                    self.logger.error(f"❌ Operation '{operation_name}' failed: {str(e)}")
                    raise
            return wrapper
        return decorator


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (usually module name)
        """
        self.logger = logging.getLogger(name)
        self.performance = PerformanceLogger(self.logger)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional structured data."""
        # Remove 'message' from kwargs to prevent conflicts
        kwargs.pop('message', None)
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional structured data."""
        # Remove 'message' from kwargs to prevent conflicts
        kwargs.pop('message', None)
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional structured data."""
        # Remove 'message' from kwargs to prevent conflicts
        kwargs.pop('message', None)
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional structured data."""
        # Remove 'message' from kwargs to prevent conflicts
        kwargs.pop('message', None)
        self._log_with_context(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with optional structured data."""
        # Remove 'message' from kwargs to prevent conflicts
        kwargs.pop('message', None)
        self._log_with_context(logging.CRITICAL, message, kwargs)
    
    def log_function_entry(self, func_name: str, **kwargs) -> None:
        """Log function entry with parameters."""
        if logging_config.debug_mode:
            context = f" with params: {kwargs}" if kwargs else ""
            self.debug(f"🚀 Entering function: {func_name}{context}")
    
    def log_function_exit(self, func_name: str, result: Any = None) -> None:
        """Log function exit with optional result."""
        if logging_config.debug_mode:
            result_str = f" returning: {type(result).__name__}" if result is not None else ""
            self.debug(f"✅ Exiting function: {func_name}{result_str}")
    
    def log_database_operation(self, operation: str, table: str, **kwargs) -> None:
        """Log database operations."""
        if logging_config.log_sql_queries:
            context = f" with params: {kwargs}" if kwargs else ""
            self.debug(f"🗄️ Database {operation} on table '{table}'{context}")
    
    def log_user_action(self, action: str, user_id: Optional[str] = None, **kwargs) -> None:
        """Log user actions for audit trail."""
        user_context = f" by user {user_id}" if user_id else ""
        context = f" with data: {kwargs}" if kwargs else ""
        self.info(f"👤 User action: {action}{user_context}{context}")
    
    def log_error_with_traceback(self, message: str, exception: Exception) -> None:
        """Log error with full traceback."""
        self.logger.error(f"❌ {message}", exc_info=exception)
    
    def _log_with_context(self, level: int, message: str, context: Dict[str, Any]) -> None:
        """Log message with structured context."""
        # Remove 'message' from context to avoid conflicts
        context_copy = {k: v for k, v in context.items() if k != 'message'}
        
        if context_copy:
            context_str = " | ".join([f"{k}={v}" for k, v in context_copy.items()])
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        
        self.logger.log(level, full_message)


def setup_logging() -> None:
    """
    Set up logging configuration for the entire application.
    
    This function configures both console and file logging with appropriate
    formatters and handlers based on the configuration settings.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, logging_config.log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if logging_config.debug_mode else logging.INFO)
    
    if sys.stdout.isatty():  # Only use colors if output is a terminal
        console_formatter = ColoredFormatter(
            fmt=logging_config.log_format,
            datefmt=logging_config.date_format
        )
    else:
        console_formatter = logging.Formatter(
            fmt=logging_config.log_format,
            datefmt=logging_config.date_format
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if logging_config.log_to_file:
        # Create logs directory if it doesn't exist
        log_dir = Path(logging_config.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=logging_config.log_file_path,
            maxBytes=logging_config.log_max_bytes,
            backupCount=logging_config.log_backup_count,
            encoding='utf-8'
        )
        
        file_formatter = logging.Formatter(
            fmt=logging_config.log_format,
            datefmt=logging_config.date_format
        )
        
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
    
    # Log the logging setup
    logger = get_logger(__name__)
    logger.info("🔧 Logging system initialized", 
                level=logging_config.log_level,
                debug_mode=logging_config.debug_mode,
                log_to_file=logging_config.log_to_file)


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        StructuredLogger: Configured logger instance
    """
    return StructuredLogger(name)


def log_function_calls(func: Callable) -> Callable:
    """
    Decorator to automatically log function entry and exit.
    
    Args:
        func: Function to decorate
        
    Returns:
        Callable: Decorated function
    """
    logger = get_logger(func.__module__)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log entry
        logger.log_function_entry(func_name, args=len(args), kwargs=list(kwargs.keys()))
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Log successful exit
            logger.log_function_exit(func_name, result)
            
            return result
            
        except Exception as e:
            # Log error exit
            logger.error(f"❌ Function {func_name} failed with error: {str(e)}")
            raise
    
    return wrapper


def log_performance(operation_name: str):
    """
    Decorator to automatically log function performance.
    
    Args:
        operation_name: Name of the operation being timed
    """
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)
        return logger.performance.time_operation(operation_name)(func)
    
    return decorator


# Utility functions for quick logging
def debug(message: str, **kwargs) -> None:
    """Quick debug logging."""
    logger = get_logger("app")
    logger.debug(message, **kwargs)


def info(message: str, **kwargs) -> None:
    """Quick info logging."""
    logger = get_logger("app")
    logger.info(message, **kwargs)


def warning(message: str, **kwargs) -> None:
    """Quick warning logging."""
    logger = get_logger("app")
    logger.warning(message, **kwargs)


def error(message: str, **kwargs) -> None:
    """Quick error logging."""
    logger = get_logger("app")
    logger.error(message, **kwargs)


def critical(message: str, **kwargs) -> None:
    """Quick critical logging."""
    logger = get_logger("app")
    logger.critical(message, **kwargs)


# Initialize logging when module is imported
setup_logging()

# Export commonly used items
__all__ = [
    'get_logger',
    'setup_logging',
    'log_function_calls',
    'log_performance',
    'StructuredLogger',
    'PerformanceLogger',
    'debug',
    'info',
    'warning',
    'error',
    'critical'
]
