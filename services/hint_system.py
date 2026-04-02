"""
HintSystem - Manages letter hints and reveals during a round.
Tracks which letters are revealed and handles hint penalties.
"""

import logging
import secrets
from typing import List, Set


logger = logging.getLogger(__name__)


class HintSystem:
    """
    Manages letter hints (nápovědy) during a quiz round.
    
    Features:
    - Track revealed letters
    - Reveal random letters
    - Check if specific letter is revealed
    - Get display string with revealed/hidden letters
    
    Example:
        >>> hint = HintSystem(answer="Steve Jobs", max_hints=10)
        >>> hint.get_all_letters()
        ['S', 'T', 'E', 'V', 'O', 'B', 'J']
        >>>
        >>> hint.reveal_letter('S')
        True
        >>> hint.get_display()
        'S_____ _____'
        >>>
        >>> hint.reveal_random_letter()
        'T'
        >>> hint.get_display()
        'ST____ _____'
    """
    
    def __init__(self, answer: str, max_hints: int = 10):
        """
        Initialize HintSystem.
        
        Args:
            answer: The answer (NORMALIZED - lowercase, no spaces, no diacritics)
            max_hints: Maximum hints available in round
            
        Raises:
            ValueError: If answer is empty or max_hints <= 0
        """
        if not answer:
            raise ValueError("Answer cannot be empty")
        if max_hints <= 0:
            raise ValueError("max_hints must be > 0")
        
        self.answer = answer.lower()
        self.answer_with_spaces = self._reconstruct_from_normalized(answer)
        self.max_hints = max_hints
        self.hint_count = 0
        
        # Get unique letters in answer
        self.all_letters: Set[str] = set(c.lower() for c in self.answer if c.isalpha())
        self.revealed_letters: Set[str] = set()
        
        logger.debug(f"HintSystem initialized: answer_len={len(answer)}, max_hints={max_hints}")
    
    @staticmethod
    def _reconstruct_from_normalized(normalized: str) -> str:
        """
        Reconstruct original answer with spaces if possible.
        For now, just returns the normalized version.
        """
        return normalized
    
    def get_all_letters(self) -> List[str]:
        """
        Get all unique letters in the answer.
        
        Returns:
            Sorted list of letters (a-z)
        """
        return sorted(list(self.all_letters))
    
    def get_revealed_letters(self) -> List[str]:
        """
        Get revealed letters.
        
        Returns:
            Sorted list of revealed letters
        """
        return sorted(list(self.revealed_letters))
    
    def get_hidden_letters(self) -> List[str]:
        """
        Get letters not yet revealed.
        
        Returns:
            Sorted list of hidden letters
        """
        hidden = self.all_letters - self.revealed_letters
        return sorted(list(hidden))
    
    def reveal_letter(self, letter: str) -> bool:
        """
        Reveal a specific letter.
        
        Args:
            letter: Letter to reveal (uppercase or lowercase)
            
        Returns:
            True if newly revealed, False if already revealed
            
        Raises:
            ValueError: If letter not in answer
        """
        letter = letter.upper()
        letter_lower = letter.lower()
        
        if letter_lower not in self.all_letters:
            raise ValueError(f"Letter '{letter}' not in answer")
        
        if letter_lower in self.revealed_letters:
            return False  # Already revealed
        
        self.revealed_letters.add(letter_lower)
        self.hint_count += 1
        
        logger.debug(f"Letter revealed: {letter} ({self.hint_count}/{self.max_hints})")
        
        return True
    
    def reveal_random_letter(self) -> str:
        """
        Reveal a random unrevealed letter.
        
        Returns:
            The revealed letter
            
        Raises:
            RuntimeError: If all letters already revealed
        """
        hidden = self.get_hidden_letters()
        
        if not hidden:
            raise RuntimeError("All letters already revealed")
        
        letter = secrets.choice(hidden)
        self.reveal_letter(letter)
        
        logger.debug(f"Random letter revealed: {letter}")
        
        return letter.upper()
    
    def is_letter_revealed(self, letter: str) -> bool:
        """
        Check if a letter is revealed.
        
        Args:
            letter: Letter to check
            
        Returns:
            True if revealed, False otherwise
        """
        return letter.lower() in self.revealed_letters
    
    def get_display(self) -> str:
        """
        Get display string with revealed/hidden letters.
        
        Format: Revealed letters shown, hidden letters as underscores.
        
        Returns:
            Display string
            
        Example:
            >>> hint = HintSystem("Steve Jobs")
            >>> hint.reveal_letter('S')
            >>> hint.reveal_letter('E')
            >>> hint.get_display()
            'S_e_e Jo__'
        """
        display = ""
        for char in self.answer_with_spaces:
            if char.isalpha():
                if char.lower() in self.revealed_letters:
                    display += char
                else:
                    display += "_"
            else:
                display += char
        
        return display
    
    def is_completed(self) -> bool:
        """
        Check if all letters are revealed.
        
        Returns:
            True if answer is fully revealed
        """
        return self.revealed_letters == self.all_letters
    
    def hints_remaining(self) -> int:
        """
        Get remaining hints available.
        
        Returns:
            Remaining hints (max - used)
        """
        return max(0, self.max_hints - self.hint_count)
    
    def __str__(self) -> str:
        """String representation."""
        revealed_count = len(self.revealed_letters)
        total_count = len(self.all_letters)
        return f"HintSystem({revealed_count}/{total_count} revealed, {self.hints_remaining()} hints left)"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"HintSystem(answer_len={len(self.answer)}, "
            f"revealed={len(self.revealed_letters)}, "
            f"hint_count={self.hint_count}/{self.max_hints})"
        )
