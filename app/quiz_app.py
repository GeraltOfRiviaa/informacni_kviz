"""
QuizApp - Main application controller class.
Coordinates between UI, Services, and Models layers.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

# Ensure root directory is in path for imports
_root_dir = str(Path(__file__).parent.parent)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from config import AppConfig, CONFIG
from models import Question, Team, GameState, Round
from services.round_manager import RoundManager
from utils import setup_logging

logger = logging.getLogger("quiz_app")


class QuizApp:
    """
    Main application controller.
    
    Responsibilities:
    - Initialize the application
    - Manage game flow (rounds, teams, scoring)
    - Coordinate between UI, services, and models
    - Handle transitions between game states
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize the QuizApp.
        
        Args:
            config: AppConfig instance (uses default if None)
        """
        self.config = config or CONFIG
        self.logger = setup_logging(debug=self.config.debug_mode)
        
        # Game state
        self.teams: List[Team] = []
        self.current_team_index: int = 0
        self.current_round_number: int = 0
        self.current_game_state: Optional[GameState] = None
        self.current_round: Optional[Round] = None
        
        # Questions (loaded from JSON)
        self.questions: List[Question] = []
        
        self.logger.info("QuizApp initialized")
    
    def add_team(self, team: Team) -> None:
        """
        Add a team to the game.
        
        Args:
            team: Team object
            
        Raises:
            ValueError: If team already exists
        """
        if any(t.name == team.name for t in self.teams):
            raise ValueError(f"Team '{team.name}' already exists")
        
        self.teams.append(team)
        self.logger.info(f"Added team: {team.name}")
    
    def get_current_team(self) -> Optional[Team]:
        """Get the currently playing team."""
        if self.current_team_index < len(self.teams):
            return self.teams[self.current_team_index]
        return None
    
    def next_team(self) -> bool:
        """
        Move to next team.
        
        Returns:
            True if moved to next team, False if no more teams
        """
        self.current_team_index += 1
        if self.current_team_index >= len(self.teams):
            return False
        return True
    
    def start_round(self, question: Question) -> RoundManager:
        """
        Start a new round with full game orchestration.
        
        Uses RoundManager to handle all round logic:
        - Cell reveals with penalties
        - Letter hints
        - Answer verification
        - Scoring
        
        Args:
            question: Question for this round
            
        Returns:
            RoundManager instance for round control
            
        Raises:
            ValueError: If no team is available
            
        Example:
            >>> app = QuizApp()
            >>> app.add_team(Team("Team A"))
            >>> manager = app.start_round(question)
            >>> manager.start()
            >>> manager.reveal_cell(0)
            >>> manager.check_answer("The Answer")
            >>> score = manager.finalize(is_correct=True)
        """
        current_team = self.get_current_team()
        if not current_team:
            raise ValueError("No team available for round")
        
        self.current_round_number += 1
        
        # Create RoundManager which handles all round logic
        round_manager = RoundManager(
            question=question,
            team_name=current_team.name,
            config=self.config
        )
        
        # Store game state reference for tracking
        # (round will be created when manager.start() is called)
        self.current_game_state = round_manager.game_state
        
        self.logger.info(
            f"Round {self.current_round_number} started: "
            f"{current_team.name} ({question.id}) with RoundManager"
        )
        
        return round_manager
    
    def is_game_complete(self) -> bool:
        """Check if all rounds are completed."""
        return self.current_round_number >= self.config.game.total_rounds
    
    def get_total_teams(self) -> int:
        """Get number of teams."""
        return len(self.teams)
    
    def get_rounds_remaining(self) -> int:
        """Get remaining rounds."""
        return max(0, self.config.game.total_rounds - self.current_round_number)
    
    def get_scores_summary(self) -> List[tuple]:
        """
        Get teams sorted by score (descending).
        
        Returns:
            List of (team_name, total_score) tuples
        """
        return sorted(
            [(team.name, team.total_score) for team in self.teams],
            key=lambda x: x[1],
            reverse=True
        )
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"QuizApp(teams={len(self.teams)}, "
            f"round={self.current_round_number}/{self.config.game.total_rounds})"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        current_team = self.get_current_team()
        return (
            f"QuizApp(teams={[t.name for t in self.teams]}, "
            f"current_team={current_team.name if current_team else None}, "
            f"round={self.current_round_number})"
        )
