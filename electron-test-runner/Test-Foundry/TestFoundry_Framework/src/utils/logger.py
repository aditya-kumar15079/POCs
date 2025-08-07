"""
Logger configuration for TestFoundry Framework
Provides comprehensive logging with file and console output
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any

def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """Setup logger with configuration
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("TestFoundry")
    logger.setLevel(getattr(logging, config.get('level', 'INFO')))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if config.get('console_enabled', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if config.get('file_enabled', True):
        log_file = logs_dir / "testfoundry.log"
        
        # Parse max file size
        max_size = _parse_size(config.get('max_file_size', '10MB'))
        backup_count = config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.get('level', 'INFO')))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def _parse_size(size_str: str) -> int:
    """Parse size string to bytes
    
    Args:
        size_str: Size string (e.g., '10MB', '1GB')
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            number = size_str[:-len(suffix)]
            try:
                return int(float(number) * multiplier)
            except ValueError:
                break
    
    # Default to 10MB if parsing fails
    return 10 * 1024 * 1024

class ContextualLogger:
    """Logger with contextual information"""
    
    def __init__(self, logger: logging.Logger, context: str):
        """Initialize contextual logger
        
        Args:
            logger: Base logger instance
            context: Context string to prepend to messages
        """
        self.logger = logger
        self.context = context
    
    def debug(self, message: str):
        """Log debug message with context"""
        self.logger.debug(f"[{self.context}] {message}")
    
    def info(self, message: str):
        """Log info message with context"""
        self.logger.info(f"[{self.context}] {message}")
    
    def warning(self, message: str):
        """Log warning message with context"""
        self.logger.warning(f"[{self.context}] {message}")
    
    def error(self, message: str):
        """Log error message with context"""
        self.logger.error(f"[{self.context}] {message}")
    
    def critical(self, message: str):
        """Log critical message with context"""
        self.logger.critical(f"[{self.context}] {message}")

def get_contextual_logger(base_logger: logging.Logger, context: str) -> ContextualLogger:
    """Get a contextual logger
    
    Args:
        base_logger: Base logger instance
        context: Context string for the logger
        
    Returns:
        Contextual logger instance
    """
    return ContextualLogger(base_logger, context)