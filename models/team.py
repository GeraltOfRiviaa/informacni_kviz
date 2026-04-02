"""
Team model - Represents a competing team.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Team:
    """
    Represents a team participating in the quiz.
    
    Attributes:
        name: Team name (e.g., "Team A", "Superstars")
        members: List of team member names
        total_score: Accumulated score across all rounds
        current_round_score: Score in current round (reset each round)
        rounds_played: Number of completed rounds
    """
    
    name: str
    members: List[str] = field(default_factory=list)
    total_score: int = 0
    current_round_score: int = 0
    rounds_played: int = 0
    
    def __post_init__(self) -> None:
        """Validate team data."""
        if not self.name:
            raise ValueError("Team name cannot be empty")
        if len(self.members) > 3:
            raise ValueError("Team cannot have more than 3 members")
    
    def add_round_score(self, round_score: int) -> None:
        """
        Add score from a completed round.
        
        Args:
            round_score: Points earned in the round
            
        Raises:
            ValueError: If round_score is invalid
        """
        if round_score < 0:
            raise ValueError("Round score cannot be negative")
        
        self.total_score += round_score
        self.current_round_score = round_score
        self.rounds_played += 1
    
    def reset_round(self) -> None:
        """Reset current round score for next round."""
        self.current_round_score = 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Team({self.name}, total_score={self.total_score})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Team(name={self.name!r}, members={self.members!r}, "
            f"total_score={self.total_score}, rounds_played={self.rounds_played})"
        )
