"""
ScoreRecord model - Records scoring details for a round.
"""

from dataclasses import dataclass


@dataclass
class ScoreRecord:
    """
    Records all scoring details for a single round.
    
    Attributes:
        round_number: Round identifier
        base_points: Starting points (usually 120)
        cells_revealed: Number of cells revealed
        penalty_cells: Points deducted for revealing cells
        letters_revealed: Number of letter hints used
        penalty_letters: Points deducted for hints
        wrong_attempts: Number of wrong answer submissions
        penalty_wrong: Points deducted for wrong answers
        final_points: Total points after all penalties (base - all penalties)
        is_correct: Whether the answer was ultimately correct
        time_used: Seconds used in the round
    """
    
    round_number: int
    base_points: int
    cells_revealed: int
    penalty_cells: int
    letters_revealed: int
    penalty_letters: int
    wrong_attempts: int
    penalty_wrong: int
    final_points: int
    is_correct: bool = False
    time_used: int = 0  # in seconds
    
    def __post_init__(self) -> None:
        """Validate score record."""
        if self.round_number < 1:
            raise ValueError("Round number must be >= 1")
        if self.base_points < 0:
            raise ValueError("Base points cannot be negative")
        if self.final_points < 0:
            raise ValueError("Final points cannot be negative")
        if self.cells_revealed < 0:
            raise ValueError("Cells revealed cannot be negative")
    
    def get_penalty_summary(self) -> dict:
        """
        Get summary of all penalties applied.
        
        Returns:
            Dictionary with penalty breakdown
        """
        return {
            "cells_penalty": self.penalty_cells,
            "letters_penalty": self.penalty_letters,
            "wrong_attempts_penalty": self.penalty_wrong,
            "total_penalty": self.penalty_cells + self.penalty_letters + self.penalty_wrong,
            "base_points": self.base_points,
            "final_points": self.final_points,
        }
    
    def __str__(self) -> str:
        """String representation."""
        status = "✓ Correct" if self.is_correct else "✗ Incorrect"
        return f"Round {self.round_number}: {self.final_points} pts [{status}]"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"ScoreRecord(round={self.round_number}, base={self.base_points}, "
            f"final={self.final_points}, cells_revealed={self.cells_revealed}, "
            f"is_correct={self.is_correct})"
        )
