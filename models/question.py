"""
Question model - Represents a single quiz question.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:
    """
    Represents one quiz question with image and answer.
    
    Attributes:
        id: Unique question ID (e.g., "q001", "q_personality_003")
        image_id: Anonymous image ID (NOT the filename! e.g., "img_087")
        answer_hash: SHA256 hash of normalized answer
        answer_salt: Salt used in hashing
        answer_length: Length of answer (for UI display of answer field)
        difficulty: Difficulty level ("easy", "medium", "hard")
        category: Category of question ("personality", "logo", "hardware", etc.)
        description: Admin description (for internal use only, NOT shown in quiz)
    
    Security Note:
        - answer is NEVER stored in plaintext
        - image_id is randomized (not sequential)
        - hint_letters are generated dynamically at runtime
    """
    
    id: str
    image_id: str
    answer_hash: str
    answer_salt: str
    answer_length: int
    difficulty: str
    category: str
    description: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate question data."""
        if not self.id:
            raise ValueError("Question ID cannot be empty")
        if not self.image_id:
            raise ValueError("Image ID cannot be empty")
        if self.answer_length < 1:
            raise ValueError("Answer length must be at least 1")
        if self.difficulty not in ("easy", "medium", "hard"):
            raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'")
    
    def __str__(self) -> str:
        """String representation of question."""
        return f"Question({self.id}, category={self.category}, difficulty={self.difficulty})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Question(id={self.id!r}, image_id={self.image_id!r}, "
            f"answer_length={self.answer_length}, category={self.category!r})"
        )
