"""
Configuration module - Centralized settings for the quiz application.
"""

from dataclasses import dataclass


@dataclass
class ScoringConfig:
    """Scoring system configuration."""
    
    base_points: int = 120
    """Initial points for each round."""
    
    cell_reveal_penalties: list = None
    """Penalties for revealing cells (index = cell number - 1).
    
    Default: [0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15]
    Meaning:
        - 1st cell revealed: 0 penalty (free)
        - 2nd cell revealed: -1 point
        - 3rd cell revealed: -2 points
        - etc.
    """
    
    wrong_answer_penalty: int = -20
    """Penalty for submitting wrong answer."""
    
    def __post_init__(self):
        """Initialize default cell penalties if not provided."""
        if self.cell_reveal_penalties is None:
            # Linearly increasing penalty: 0, -1, -2, -3, ..., -15
            self.cell_reveal_penalties = [i for i in range(16)]
            self.cell_reveal_penalties[0] = 0
            for i in range(1, 16):
                self.cell_reveal_penalties[i] = -i
    
    def get_cell_penalty(self, cell_number: int) -> int:
        """
        Get penalty for revealing N-th cell.
        
        Args:
            cell_number: Which cell (1-16)
            
        Returns:
            Penalty points (usually negative)
            
        Raises:
            ValueError: If cell_number out of range
        """
        if cell_number < 1 or cell_number > 16:
            raise ValueError("Cell number must be 1-16")
        return self.cell_reveal_penalties[cell_number - 1]


@dataclass
class GameConfig:
    """Game mechanics configuration."""
    
    time_per_round: int = 600
    """Default time limit per round in seconds (600 = 10 minutes)."""
    
    grid_size: int = 4
    """Grid dimension (4 = 4x4 grid = 16 cells)."""
    
    total_rounds: int = 5
    """Total number of rounds in a complete game."""
    
    min_team_members: int = 1
    """Minimum team members."""
    
    max_team_members: int = 3
    """Maximum team members."""


@dataclass
class HintConfig:
    """Hint/letter reveal configuration."""
    
    letter_penalty: int = -1
    """Penalty for revealing one letter."""
    
    hints_per_round: int = 10
    """Maximum hints available per round (can reveal up to 10 letters)."""


@dataclass
class AppConfig:
    """Complete application configuration."""
    
    scoring: ScoringConfig = None
    game: GameConfig = None
    hints: HintConfig = None
    
    # Paths
    data_dir: str = "data"
    """Directory containing quiz data files."""
    
    questions_json: str = "data/questions.json"
    """Path to questions JSON file."""
    
    answers_hash_json: str = "data/answers_hash.json"
    """Path to answers hash file."""
    
    config_json: str = "data/config.json"
    """Path to config JSON file."""
    
    images_dir: str = "assets/images"
    """Path to directory containing image files."""
    
    # Debug/Admin
    debug_mode: bool = False
    """Enable debug output."""
    
    def __post_init__(self):
        """Initialize sub-configs if not provided."""
        if self.scoring is None:
            self.scoring = ScoringConfig()
        if self.game is None:
            self.game = GameConfig()
        if self.hints is None:
            self.hints = HintConfig()

    @property
    def images_archive(self) -> str:
        """Backward-compatible alias for older code paths."""
        return self.images_dir
    
    @staticmethod
    def get_default() -> "AppConfig":
        """Get default configuration."""
        return AppConfig()


# Global config instance
CONFIG = AppConfig.get_default()
