"""
Round model - Represents a single round of the quiz.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

from .question import Question
from .grid import Grid
from .score import ScoreRecord


@dataclass
class Round:
    """
    Represents a single round of the quiz.
    
    Attributes:
        round_number: Round identifier (1, 2, 3, ...)
        question: Question object for this round
        grid: 4x4 grid state
        start_time: When round started
        end_time: When round ended (None if still active)
        team_name: Name of competing team
        score_record: Scoring details (None until round ends)
        is_completed: Whether round is finished
        is_correct: Whether answer was correct
        reveal_history: Log of cell reveals for audit trail
    """
    
    round_number: int
    question: Question
    grid: Grid
    team_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    score_record: Optional[ScoreRecord] = None
    is_completed: bool = False
    is_correct: bool = False
    reveal_history: List[Dict] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate round data."""
        if self.round_number < 1:
            raise ValueError("Round number must be >= 1")
        if not self.question:
            raise ValueError("Question cannot be None")
        if not self.team_name:
            raise ValueError("Team name cannot be empty")
    
    def get_duration_seconds(self) -> int:
        """
        Get round duration in seconds.
        
        Returns:
            Duration from start to end (or now if still active)
        """
        end = self.end_time or datetime.now()
        return int((end - self.start_time).total_seconds())
    
    def add_reveal_to_history(self, cell_index: int, reveal_type: str = "cell") -> None:
        """
        Log a cell reveal to history.
        
        Args:
            cell_index: Index of revealed cell
            reveal_type: Type of reveal ("cell", "letter", etc.)
        """
        self.reveal_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": reveal_type,
            "cell_index": cell_index,
        })
    
    def finalize(self, is_correct: bool, score_record: ScoreRecord) -> None:
        """
        Mark round as completed.
        
        Args:
            is_correct: Whether answer was correct
            score_record: Final scoring record
        """
        self.end_time = datetime.now()
        self.is_correct = is_correct
        self.score_record = score_record
        self.is_completed = True
    
    def __str__(self) -> str:
        """String representation."""
        status = "completed" if self.is_completed else "in progress"
        return f"Round {self.round_number} ({self.team_name}) [{status}]"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Round(number={self.round_number}, team={self.team_name!r}, "
            f"completed={self.is_completed}, correct={self.is_correct})"
        )
