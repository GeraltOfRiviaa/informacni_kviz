"""
ScoreManager - Manages scoring logic and calculations.
Responsible for calculating penalties and final scores.
"""

import logging
from typing import List
from config import ScoringConfig


logger = logging.getLogger(__name__)


class ScoreManager:
    """
    Manages all scoring calculations for the quiz game.
    
    Scoring System:
    - Base points: 120 per round
    - Cell penalty: 0, -1, -2, -3, ..., -15 (linear decrease)
    - Letter hint penalty: -1 per hint
    - Wrong answer penalty: -20 per wrong submission
    - Final score: max(0, base - all_penalties)
    """
    
    def __init__(self, config: ScoringConfig = None):
        """
        Initialize ScoreManager.
        
        Args:
            config: ScoringConfig instance (uses default if None)
        """
        if config is None:
            config = ScoringConfig()
        
        self.config = config
        self.base_points = config.base_points
        logger.debug(f"ScoreManager initialized with base_points={self.base_points}")
    
    def get_cell_penalty(self, cell_number: int) -> int:
        """
        Get penalty for revealing N-th cell.
        
        Args:
            cell_number: Cell number (1-16)
            
        Returns:
            Penalty points (0, -1, -2, ..., -15)
            
        Raises:
            ValueError: If cell_number out of range
            
        Example:
            >>> sm = ScoreManager()
            >>> sm.get_cell_penalty(1)  # First cell
            0
            >>> sm.get_cell_penalty(2)  # Second cell
            -1
            >>> sm.get_cell_penalty(16) # Last cell
            -15
        """
        return self.config.get_cell_penalty(cell_number)
    
    def calculate_cell_penalties(self, cells_revealed: int) -> int:
        """
        Calculate total penalty for revealed cells.
        
        Args:
            cells_revealed: Number of cells revealed (1-16)
            
        Returns:
            Total penalty (0, -1, -3, -6, -10, ...)
            
        Example:
            >>> sm = ScoreManager()
            >>> sm.calculate_cell_penalties(1)   # 0
            0
            >>> sm.calculate_cell_penalties(2)   # 0 + -1
            -1
            >>> sm.calculate_cell_penalties(3)   # 0 + -1 + -2
            -3
            >>> sm.calculate_cell_penalties(5)   # 0 + -1 + -2 + -3 + -4
            -10
        """
        if cells_revealed < 0 or cells_revealed > 16:
            raise ValueError("Cells revealed must be 0-16")
        
        total = 0
        for i in range(1, cells_revealed + 1):
            total += self.get_cell_penalty(i)
        
        return total
    
    def get_letter_hint_penalty(self) -> int:
        """
        Get penalty for one letter hint.
        
        Returns:
            Penalty for one hint (-1)
        """
        return getattr(self.config, 'letter_penalty', -1)
    
    def calculate_letter_penalties(self, letters_revealed: int) -> int:
        """
        Calculate total penalty for revealed letters.
        
        Args:
            letters_revealed: Number of letters revealed
            
        Returns:
            Total penalty (-letters_revealed)
            
        Example:
            >>> sm = ScoreManager()
            >>> sm.calculate_letter_penalties(0)
            0
            >>> sm.calculate_letter_penalties(3)
            -3
        """
        if letters_revealed < 0:
            raise ValueError("Letters revealed cannot be negative")
        
        penalty = self.get_letter_hint_penalty()
        return penalty * letters_revealed
    
    def get_wrong_answer_penalty(self) -> int:
        """
        Get penalty for one wrong answer submission.
        
        Returns:
            Penalty for wrong answer (-20)
        """
        return self.config.wrong_answer_penalty
    
    def calculate_wrong_attempt_penalties(self, wrong_attempts: int) -> int:
        """
        Calculate total penalty for wrong answer submissions.
        
        Args:
            wrong_attempts: Number of wrong answers submitted
            
        Returns:
            Total penalty (-20 * wrong_attempts)
            
        Example:
            >>> sm = ScoreManager()
            >>> sm.calculate_wrong_attempt_penalties(0)
            0
            >>> sm.calculate_wrong_attempt_penalties(1)
            -20
            >>> sm.calculate_wrong_attempt_penalties(2)
            -40
        """
        if wrong_attempts < 0:
            raise ValueError("Wrong attempts cannot be negative")
        
        penalty = self.get_wrong_answer_penalty()
        return penalty * wrong_attempts
    
    def calculate_final_score(
        self,
        cells_revealed: int,
        letters_revealed: int,
        wrong_attempts: int
    ) -> int:
        """
        Calculate final score for a round.
        
        Args:
            cells_revealed: Number of cells revealed (0-16)
            letters_revealed: Number of letter hints used (0+)
            wrong_attempts: Number of wrong answer submissions (0+)
            
        Returns:
            Final score (min 0, typically 0-120)
            
        Raises:
            ValueError: If any parameter is invalid
            
        Example:
            >>> sm = ScoreManager()
            >>> sm.calculate_final_score(0, 0, 0)  # Perfect!
            120
            >>> sm.calculate_final_score(1, 0, 0)  # Revealed 1 cell
            120  # First cell free
            >>> sm.calculate_final_score(2, 0, 0)  # Revealed 2 cells
            119  # 120 + -1
            >>> sm.calculate_final_score(5, 3, 1)  # 5 cells, 3 letters, 1 wrong
            89   # 120 + -10 + -3 + -20 = 87
        """
        cell_penalty = self.calculate_cell_penalties(cells_revealed)
        letter_penalty = self.calculate_letter_penalties(letters_revealed)
        wrong_penalty = self.calculate_wrong_attempt_penalties(wrong_attempts)
        
        total_penalty = cell_penalty + letter_penalty + wrong_penalty
        final_score = self.base_points + total_penalty
        
        # Never go below 0
        return max(0, final_score)
    
    def get_scoring_summary(
        self,
        cells_revealed: int,
        letters_revealed: int,
        wrong_attempts: int
    ) -> dict:
        """
        Get detailed scoring breakdown.
        
        Args:
            cells_revealed: Number of cells revealed
            letters_revealed: Number of letters revealed
            wrong_attempts: Number of wrong attempts
            
        Returns:
            Dictionary with scoring breakdown
            
        Example:
            >>> sm = ScoreManager()
            >>> summary = sm.get_scoring_summary(5, 2, 1)
            >>> summary['base_points']
            120
            >>> summary['cell_penalty']
            -10
            >>> summary['letter_penalty']
            -2
            >>> summary['wrong_penalty']
            -20
            >>> summary['final_score']
            88
        """
        cell_penalty = self.calculate_cell_penalties(cells_revealed)
        letter_penalty = self.calculate_letter_penalties(letters_revealed)
        wrong_penalty = self.calculate_wrong_attempt_penalties(wrong_attempts)
        final_score = self.calculate_final_score(
            cells_revealed, letters_revealed, wrong_attempts
        )
        
        return {
            "base_points": self.base_points,
            "cells_revealed": cells_revealed,
            "cell_penalty": cell_penalty,
            "letters_revealed": letters_revealed,
            "letter_penalty": letter_penalty,
            "wrong_attempts": wrong_attempts,
            "wrong_penalty": wrong_penalty,
            "total_penalty": cell_penalty + letter_penalty + wrong_penalty,
            "final_score": final_score,
        }
