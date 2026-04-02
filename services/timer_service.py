"""
TimerService - Manages countdown timer for quiz rounds.
Handles time tracking, callbacks, and timeout detection.
"""

import logging
from typing import Callable, Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class TimerService:
    """
    Manages countdown timer for a quiz round.
    
    Features:
    - Start/stop/pause timer
    - Get remaining time
    - Callback on each tick
    - Timeout detection
    - Elapsed time tracking
    
    Example:
        >>> timer = TimerService(duration_seconds=600)
        >>> timer.start()
        >>> timer.get_remaining_time()
        600
        >>> # After 10 seconds...
        >>> timer.get_remaining_time()
        590
    """
    
    def __init__(self, duration_seconds: int, on_tick: Optional[Callable] = None):
        """
        Initialize timer.
        
        Args:
            duration_seconds: Duration in seconds
            on_tick: Optional callback function called on each second
            
        Raises:
            ValueError: If duration_seconds <= 0
        """
        if duration_seconds <= 0:
            raise ValueError("Duration must be > 0")
        
        self.duration_seconds = duration_seconds
        self.remaining_seconds = duration_seconds
        self.on_tick = on_tick
        
        self.start_time: Optional[datetime] = None
        self.pause_time: Optional[datetime] = None
        self.is_running = False
        self.is_paused = False
        
        logger.debug(f"TimerService initialized: {duration_seconds}s")
    
    def start(self) -> None:
        """
        Start the timer.
        
        Raises:
            RuntimeError: If timer already running
        """
        if self.is_running:
            raise RuntimeError("Timer already running")
        
        self.start_time = datetime.now()
        self.is_running = True
        self.is_paused = False
        
        logger.debug("Timer started")
    
    def pause(self) -> None:
        """
        Pause the timer.
        
        Raises:
            RuntimeError: If timer not running
        """
        if not self.is_running or self.is_paused:
            raise RuntimeError("Timer not running or already paused")
        
        self.pause_time = datetime.now()
        self.is_paused = True
        
        logger.debug("Timer paused")
    
    def resume(self) -> None:
        """
        Resume paused timer.
        
        Raises:
            RuntimeError: If timer not paused
        """
        if not self.is_paused:
            raise RuntimeError("Timer not paused")
        
        # Calculate pause duration
        pause_duration = datetime.now() - self.pause_time
        
        # Adjust start time
        self.start_time += pause_duration
        
        self.is_paused = False
        
        logger.debug("Timer resumed")
    
    def stop(self) -> int:
        """
        Stop the timer.
        
        Returns:
            Remaining time at stop
            
        Raises:
            RuntimeError: If timer not running
        """
        if not self.is_running:
            raise RuntimeError("Timer not running")
        
        # Get remaining time BEFORE stopping
        remaining = self.get_remaining_time()
        
        self.is_running = False
        self.is_paused = False
        
        logger.debug(f"Timer stopped: {remaining}s remaining")
        
        return remaining
    
    def get_elapsed_time(self) -> int:
        """
        Get elapsed time in seconds.
        
        Returns:
            Elapsed seconds, or 0 if not started
        """
        if not self.start_time:
            return 0
        
        if self.is_paused:
            # Calculate until pause time
            elapsed = (self.pause_time - self.start_time).total_seconds()
        else:
            # Calculate until now
            elapsed = (datetime.now() - self.start_time).total_seconds()
        
        return int(elapsed)
    
    def get_remaining_time(self) -> int:
        """
        Get remaining time in seconds.
        
        Returns:
            Remaining seconds (0 if expired)
        """
        if not self.is_running:
            return self.duration_seconds
        
        elapsed = self.get_elapsed_time()
        remaining = self.duration_seconds - elapsed
        
        return max(0, int(remaining))
    
    def is_time_expired(self) -> bool:
        """
        Check if time has expired.
        
        Returns:
            True if time is up, False otherwise
        """
        return self.get_remaining_time() <= 0
    
    def get_progress_percentage(self) -> float:
        """
        Get progress as percentage (0-100).
        
        Returns:
            Progress percentage
        """
        elapsed = self.get_elapsed_time()
        progress = (elapsed / self.duration_seconds) * 100
        return min(100.0, max(0.0, progress))
    
    def __call__(self) -> int:
        """
        Call timer to update and trigger callback.
        
        Returns:
            Remaining time in seconds
        """
        if not self.is_running:
            return self.remaining_seconds
        
        remaining = self.get_remaining_time()
        
        # Trigger callback if provided
        if self.on_tick:
            try:
                self.on_tick(remaining)
            except Exception as e:
                logger.error(f"Error in on_tick callback: {e}")
        
        return remaining
    
    def __str__(self) -> str:
        """String representation."""
        remaining = self.get_remaining_time()
        minutes = remaining // 60
        seconds = remaining % 60
        status = "running" if self.is_running else "stopped"
        
        if self.is_paused:
            status = "paused"
        
        return f"Timer({minutes}:{seconds:02d}, {status})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"TimerService(duration={self.duration_seconds}, "
            f"remaining={self.get_remaining_time()}, "
            f"running={self.is_running})"
        )
