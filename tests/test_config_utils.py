"""
Unit tests for configuration and utility modules.
"""

import pytest
from pathlib import Path
import tempfile

from config import ScoringConfig, GameConfig, HintConfig, AppConfig
from utils import (
    format_time_remaining, format_score, normalize_team_name,
    normalize_member_name,
    clamp, validate_file_exists, validate_directory_exists,
    ensure_directory_exists
)


class TestScoringConfig:
    """Tests for ScoringConfig."""
    
    def test_scoring_config_defaults(self):
        """Test default scoring values."""
        config = ScoringConfig()
        assert config.base_points == 120
        assert config.wrong_answer_penalty == -20
        assert len(config.cell_reveal_penalties) == 16
    
    def test_get_cell_penalty(self):
        """Test getting cell penalties."""
        config = ScoringConfig()
        
        # First cell free
        assert config.get_cell_penalty(1) == 0
        
        # Second cell -1
        assert config.get_cell_penalty(2) == -1
        
        # Third cell -2
        assert config.get_cell_penalty(3) == -2
        
        # Last cell -15
        assert config.get_cell_penalty(16) == -15
    
    def test_invalid_cell_number(self):
        """Test that invalid cell numbers raise error."""
        config = ScoringConfig()
        
        with pytest.raises(ValueError):
            config.get_cell_penalty(0)
        
        with pytest.raises(ValueError):
            config.get_cell_penalty(17)


class TestGameConfig:
    """Tests for GameConfig."""
    
    def test_game_config_defaults(self):
        """Test default game settings."""
        config = GameConfig()
        assert config.time_per_round == 600
        assert config.grid_size == 4
        assert config.total_rounds == 5
        assert config.max_team_members == 3


class TestHintConfig:
    """Tests for HintConfig."""
    
    def test_hint_config_defaults(self):
        """Test default hint settings."""
        config = HintConfig()
        assert config.letter_penalty == -1
        assert config.hints_per_round == 10


class TestAppConfig:
    """Tests for AppConfig."""
    
    def test_app_config_default(self):
        """Test default app configuration."""
        config = AppConfig.get_default()
        assert config.scoring is not None
        assert config.game is not None
        assert config.hints is not None
    
    def test_app_config_paths(self):
        """Test configuration paths."""
        config = AppConfig.get_default()
        assert config.data_dir == "data"
        assert "questions.json" in config.questions_json
        assert "answers_hash.json" in config.answers_hash_json


class TestUtilsFormatting:
    """Tests for formatting utility functions."""
    
    def test_format_time_remaining(self):
        """Test time formatting."""
        assert format_time_remaining(125) == "2:05"
        assert format_time_remaining(45) == "0:45"
        assert format_time_remaining(600) == "10:00"
        assert format_time_remaining(0) == "0:00"
    
    def test_format_score(self):
        """Test score formatting."""
        assert format_score(100) == "100 pts"
        assert format_score(0) == "0 pts"
        assert format_score(1000) == "1000 pts"


class TestUtilsNormalization:
    """Tests for normalization utility functions."""
    
    def test_normalize_team_name(self):
        """Test team name normalization."""
        assert normalize_team_name("team alpha") == "Team Alpha"
        assert normalize_team_name("  The Wizards  ") == "The Wizards"
    
    def test_normalize_member_name(self):
        """Test member name normalization."""
        assert normalize_member_name("alice") == "Alice"
        assert normalize_member_name("  bob smith  ") == "Bob Smith"


class TestUtilsClamp:
    """Tests for clamp function."""
    
    def test_clamp_within_range(self):
        """Test clamping within valid range."""
        assert clamp(50, 0, 100) == 50
    
    def test_clamp_below_min(self):
        """Test clamping below minimum."""
        assert clamp(-10, 0, 100) == 0
    
    def test_clamp_above_max(self):
        """Test clamping above maximum."""
        assert clamp(150, 0, 120) == 120


class TestUtilsFileOperations:
    """Tests for file/directory utility functions."""
    
    def test_validate_file_exists(self):
        """Test file existence validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")
            
            assert validate_file_exists(str(test_file)) is True
            assert validate_file_exists(str(test_file.parent / "nonexistent.txt")) is False
    
    def test_validate_directory_exists(self):
        """Test directory existence validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert validate_directory_exists(tmpdir) is True
            assert validate_directory_exists(str(Path(tmpdir) / "nonexistent")) is False
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_dir" / "subdir"
            
            assert ensure_directory_exists(str(new_dir)) is True
            assert new_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
