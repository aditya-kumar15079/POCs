"""
Logger module for LLM Judge Framework.
Configures logging for the application.
"""

import os
import logging
from datetime import datetime
from typing import Dict


class Logger:
    """Handler for configuring and using logging."""

    # Logger instance
    _logger = None

    @classmethod
    def setup(cls, config: Dict[str, str]) -> None:
        """
        Set up logging based on configuration.
        
        Args:
            config: Dict containing logging configuration with 'level' and 'file' keys
        """
        # Create logs directory if it doesn't exist
        log_file = config.get("file", "logs/llm_judge.log")
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Set up logger
        cls._logger = logging.getLogger("llm_judge")
        
        # Set logging level
        level_str = config.get("level", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)
        cls._logger.setLevel(level)
        
        # Clear existing handlers
        if cls._logger.handlers:
            cls._logger.handlers.clear()
        
        # Create file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_with_timestamp = f"{os.path.splitext(log_file)[0]}_{timestamp}.log"
        file_handler = logging.FileHandler(log_file_with_timestamp)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add formatter to handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)
        
        cls._logger.info("Logger initialized")

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Get the logger instance.
        
        Returns:
            Logger instance
        
        Raises:
            RuntimeError: If logger is not initialized
        """
        if cls._logger is None:
            # Set up default logger if not initialized
            cls.setup({"level": "INFO", "file": "logs/llm_judge.log"})
            
        return cls._logger
    
    @classmethod
    def debug(cls, message: str) -> None:
        """Log debug message."""
        cls.get_logger().debug(message)
    
    @classmethod
    def info(cls, message: str) -> None:
        """Log info message."""
        cls.get_logger().info(message)
    
    @classmethod
    def warning(cls, message: str) -> None:
        """Log warning message."""
        cls.get_logger().warning(message)
    
    @classmethod
    def error(cls, message: str) -> None:
        """Log error message."""
        cls.get_logger().error(message)
    
    @classmethod
    def critical(cls, message: str) -> None:
        """Log critical message."""
        cls.get_logger().critical(message)