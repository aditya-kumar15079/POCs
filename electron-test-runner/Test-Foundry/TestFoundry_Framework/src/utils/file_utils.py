"""
File handling utilities for TestFoundry Framework
Provides functions for file discovery, validation, and management
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Set
import mimetypes

def get_input_files(input_dir: Path, supported_formats: List[str]) -> List[Path]:
    """Get all supported files from input directory
    
    Args:
        input_dir: Input directory path
        supported_formats: List of supported file extensions (with dots)
        
    Returns:
        List of supported file paths
    """
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
        return []
    
    supported_files = []
    supported_extensions = {ext.lower() for ext in supported_formats}
    
    for file_path in input_dir.rglob('*'):
        if file_path.is_file():
            file_ext = file_path.suffix.lower()
            if file_ext in supported_extensions:
                supported_files.append(file_path)
    
    return sorted(supported_files)

def ensure_output_directory(output_dir: Path) -> Path:
    """Ensure output directory exists and return path
    
    Args:
        output_dir: Output directory path
        
    Returns:
        Path to output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_file_info(file_path: Path) -> dict:
    """Get comprehensive file information
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary containing file information
    """
    stat = file_path.stat()
    
    return {
        'name': file_path.name,
        'stem': file_path.stem,
        'suffix': file_path.suffix.lower(),
        'size': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'modified': stat.st_mtime,
        'mime_type': mimetypes.guess_type(str(file_path))[0],
        'is_readable': file_path.is_file() and os.access(file_path, os.R_OK)
    }

def validate_file(file_path: Path, max_size_mb: Optional[int] = None) -> tuple[bool, str]:
    """Validate if file can be processed
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, "File does not exist"
    
    if not file_path.is_file():
        return False, "Path is not a file"
    
    if not os.access(file_path, os.R_OK):
        return False, "File is not readable"
    
    if max_size_mb:
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File size ({file_size_mb:.1f} MB) exceeds limit ({max_size_mb} MB)"
    
    return True, ""

def safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove multiple consecutive underscores
    while '__' in safe_name:
        safe_name = safe_name.replace('__', '_')
    
    # Remove leading/trailing underscores and dots
    safe_name = safe_name.strip('_.')
    
    # Ensure filename is not empty
    if not safe_name:
        safe_name = "untitled"
    
    return safe_name

def create_backup(file_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """Create a backup of a file
    
    Args:
        file_path: Path to file to backup
        backup_dir: Directory to store backup (optional)
        
    Returns:
        Path to backup file
    """
    if backup_dir is None:
        backup_dir = file_path.parent / "backups"
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create unique backup filename with timestamp
    import time
    timestamp = int(time.time())
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    return backup_path

def get_unique_filename(directory: Path, base_name: str, extension: str) -> Path:
    """Get a unique filename in the directory
    
    Args:
        directory: Target directory
        base_name: Base filename without extension
        extension: File extension (with dot)
        
    Returns:
        Path to unique filename
    """
    counter = 1
    filename = f"{base_name}{extension}"
    file_path = directory / filename
    
    while file_path.exists():
        filename = f"{base_name}_{counter}{extension}"
        file_path = directory / filename
        counter += 1
    
    return file_path

def cleanup_temp_files(temp_dir: Path, max_age_hours: int = 24):
    """Clean up temporary files older than specified age
    
    Args:
        temp_dir: Temporary directory path
        max_age_hours: Maximum age in hours
    """
    if not temp_dir.exists():
        return
    
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in temp_dir.rglob('*'):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                except OSError:
                    pass  # Ignore errors when deleting temp files

def get_directory_size(directory: Path) -> int:
    """Get total size of directory in bytes
    
    Args:
        directory: Directory path
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                total_size += file_path.stat().st_size
            except OSError:
                pass  # Skip files that can't be accessed
    
    return total_size

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"