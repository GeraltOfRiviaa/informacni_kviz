"""
GameState model - Manages the current state of a running round.
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional

from .question import Question
from .grid import Grid


@dataclass
class GameState:
    """
    Manages the current state of a running game round.
    This is the 'snapshot' of what's happening RIGHT NOW.
    
    Attributes:
        question: Current question
        grid: Current grid state (which cells revealed)
        revealed_letters: Set of revealed letters in answer
        time_remaining: Seconds left in round
        current_score: Points earned so far in round
        cells_revealed_count: Number of cells revealed
        wrong_attempts: Number of incorrect answer submissions
        is_active: Whether round is still running
        user_answer_input: What user typed so far (for input field)
    """
    
    question: Question
    grid: Grid
    time_remaining: int  # in seconds
    base_score: int = 120
    revealed_letters: Set[str] = field(default_factory=set)
    cells_revealed_count: int = 0
    wrong_attempts: int = 0
    is_active: bool = True
    user_answer_input: str = ""
    current_score: int = field(init=False)
    
    def __post_init__(self) -> None:
        """Initialize current_score from base_score."""
        self.current_score = self.base_score
        if self.time_remaining < 0:
            raise ValueError("Time remaining cannot be negative")
        if self.base_score < 0:
            raise ValueError("Base score cannot be negative")
    
    def add_revealed_cell(self, penalty: int) -> None:
        """
        Register a revealed cell and apply penalty.
        
        Args:
            penalty: Points deducted for this reveal
        """
        if penalty < 0:
            raise ValueError("Penalty cannot be negative")
        self.cells_revealed_count += 1
        self.current_score = max(0, self.current_score - penalty)
    
    def add_revealed_letter(self, letter: str, penalty: int) -> None:
        """
        Register a revealed letter hint.
        
        Args:
            letter: The revealed letter
            penalty: Points deducted for this hint
        """
        if not letter:
            raise ValueError("Letter cannot be empty")
        if penalty < 0:
            raise ValueError("Penalty cannot be negative")
        
        self.revealed_letters.add(letter.upper())
        self.current_score = max(0, self.current_score - penalty)
    
    def apply_wrong_attempt_penalty(self, penalty: int) -> None:
        """
        Apply penalty for wrong answer submission.
        
        Args:
            penalty: Points deducted
        """
        if penalty < 0:
            raise ValueError("Penalty cannot be negative")
        self.wrong_attempts += 1
        self.current_score = max(0, self.current_score - penalty)
    
    def reduce_time(self, seconds: int) -> None:
        """
        Reduce remaining time.
        
        Args:
            seconds: Seconds to subtract
        """
        if seconds < 0:
            raise ValueError("Cannot reduce by negative seconds")
        self.time_remaining = max(0, self.time_remaining - seconds)
        
        if self.time_remaining == 0:
            self.is_active = False
    
    def is_time_expired(self) -> bool:
        """Check if time has run out."""
        return self.time_remaining <= 0
    
    def update_user_input(self, text: str) -> None:
        """
        Update the user's answer input.
        
        Args:
            text: New input text
        """
        self.user_answer_input = text
    
    def get_revealed_letters_sorted(self) -> List[str]:
        """Get revealed letters in sorted order."""
        return sorted(list(self.revealed_letters))
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"GameState(score={self.current_score}, time={self.time_remaining}s, "
            f"cells_revealed={self.cells_revealed_count}, active={self.is_active})"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"GameState(current_score={self.current_score}, "
            f"time_remaining={self.time_remaining}, "
            f"cells_revealed={self.cells_revealed_count}, "
            f"revealed_letters={sorted(self.revealed_letters)}, "
            f"is_active={self.is_active})"
        )
