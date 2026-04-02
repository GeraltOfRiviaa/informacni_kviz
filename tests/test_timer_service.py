"""
Unit tests for TimerService.
"""

import pytest
import time
from services.timer_service import TimerService


class TestTimerService:
    """Tests for TimerService."""
    
    def test_initialization(self):
        """Test timer initialization."""
        timer = TimerService(600)
        
        assert timer.duration_seconds == 600
        assert timer.remaining_seconds == 600
        assert timer.is_running is False
    
    def test_invalid_duration(self):
        """Test that invalid durations raise error."""
        with pytest.raises(ValueError):
            TimerService(0)
        
        with pytest.raises(ValueError):
            TimerService(-10)
    
    def test_start_timer(self):
        """Test starting timer."""
        timer = TimerService(600)
        timer.start()
        
        assert timer.is_running is True
        assert timer.start_time is not None
    
    def test_start_already_running(self):
        """Test that starting running timer raises error."""
        timer = TimerService(600)
        timer.start()
        
        with pytest.raises(RuntimeError):
            timer.start()
    
    def test_get_remaining_time(self):
        """Test getting remaining time."""
        timer = TimerService(10)
        
        # Before start
        assert timer.get_remaining_time() == 10
        
        # After start (no time elapsed yet)
        timer.start()
        remaining = timer.get_remaining_time()
        assert 9 <= remaining <= 10
    
    def test_elapsed_time(self):
        """Test elapsed time calculation."""
        timer = TimerService(10)
        timer.start()
        
        elapsed1 = timer.get_elapsed_time()
        time.sleep(0.1)
        elapsed2 = timer.get_elapsed_time()
        
        # Should increase
        assert elapsed2 >= elapsed1
    
    def test_time_expired(self):
        """Test expiration detection."""
        timer = TimerService(1)  # 1 second
        
        assert timer.is_time_expired() is False
        
        timer.start()
        time.sleep(1.2)
        
        assert timer.is_time_expired() is True
        assert timer.get_remaining_time() == 0
    
    def test_stop_timer(self):
        """Test stopping timer."""
        timer = TimerService(600)
        timer.start()
        time.sleep(1)  # Wait 1 second
        
        remaining = timer.stop()
        
        assert timer.is_running is False
        assert 598 <= remaining <= 599  # Should be around 599
    
    def test_pause_resume(self):
        """Test pausing and resuming."""
        timer = TimerService(10)
        timer.start()
        time.sleep(0.5)
        
        timer.pause()
        remaining_paused = timer.get_remaining_time()
        
        time.sleep(0.3)  # Wait
        remaining_still = timer.get_remaining_time()
        
        # Should be same (timer paused)
        assert remaining_paused == remaining_still
        
        timer.resume()
        time.sleep(0.5)
        
        remaining_resumed = timer.get_remaining_time()
        # Should be less now
        assert remaining_resumed <= remaining_still
    
    def test_callback(self):
        """Test callback on tick."""
        calls = []
        
        def on_tick(remaining):
            calls.append(remaining)
        
        timer = TimerService(2, on_tick=on_tick)
        timer.start()
        
        # Call timer multiple times
        timer()
        timer()
        
        # Callback should have been called
        assert len(calls) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
