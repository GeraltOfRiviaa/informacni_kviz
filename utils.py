"""
Utility functions for the quiz application.
"""

import logging
from typing import Optional
from pathlib import Path


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    debug: bool = False
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        debug: If True, set to DEBUG level
        
    Returns:
        Configured logger instance
    """
    if debug:
        level = logging.DEBUG
    
    logger = logging.getLogger("quiz_app")
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).exists() and Path(file_path).is_file()


def validate_directory_exists(dir_path: str) -> bool:
    """
    Validate that a directory exists.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        True if directory exists, False otherwise
    """
    return Path(dir_path).exists() and Path(dir_path).is_dir()


def ensure_directory_exists(dir_path: str) -> bool:
    """
    Create directory if it doesn't exist.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        True if directory exists (created or already present), False on error
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {dir_path}: {e}")
        return False


def format_time_remaining(seconds: int) -> str:
    """
    Format time remaining for display.
    
    Args:
        seconds: Seconds remaining
        
    Returns:
        Formatted string (MM:SS)
        
    Example:
        >>> format_time_remaining(125)
        '2:05'
        >>> format_time_remaining(45)
        '0:45'
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def format_score(score: int) -> str:
    """
    Format score for display.
    
    Args:
        score: Score value
        
    Returns:
        Formatted string
        
    Example:
        >>> format_score(100)
        '100 pts'
    """
    return f"{score} pts"


def normalize_team_name(name: str) -> str:
    """
    Normalize team name (strip whitespace, capitalize).
    
    Args:
        name: Team name
        
    Returns:
        Normalized name
    """
    return name.strip().title()


def normalize_member_name(name: str) -> str:
    """
    Normalize team member name.
    
    Args:
        name: Member name
        
    Returns:
        Normalized name
    """
    return name.strip().title()


def clamp(value: int, min_val: int, max_val: int) -> int:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
        
    Example:
        >>> clamp(150, 0, 120)
        120
    """
    return max(min_val, min(value, max_val))
