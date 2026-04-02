"""
RoundManager - Orchestrates game round logic.
Coordinates between all services and models.
"""

import logging
from typing import Optional, Tuple

from models import Question, GameState, Round, Grid, ScoreRecord
from services.score_manager import ScoreManager
from services.answer_checker import AnswerChecker
from services.timer_service import TimerService
from services.hint_system import HintSystem
from config import AppConfig, CONFIG


logger = logging.getLogger(__name__)


class RoundManager:
    """
    Manages a single quiz round.
    
    Responsibilities:
    - Initialize round state
    - Handle cell reveals
    - Handle letter hints
    - Process answer submissions
    - Calculate final score
    - Detect timeout
    
    Example:
        >>> config = CONFIG
        >>> round_mgr = RoundManager(question, team_name="Team A", config=config)
        >>> round_mgr.start()
        >>>
        >>> # Reveal a cell
        >>> round_mgr.reveal_cell(0)  # Cell index 0
        >>>
        >>> # Request hint
        >>> letter = round_mgr.request_hint_random()
        >>>
        >>> # Check answer
        >>> is_correct = round_mgr.check_answer("Steve Jobs")
        >>> round_mgr.finalize(is_correct)
    """
    
    def __init__(
        self,
        question: Question,
        team_name: str,
        answer_hash: Optional[str] = None,
        answer_salt: Optional[str] = None,
        config: Optional[AppConfig] = None,
    ):
        """
        Initialize RoundManager.
        
        Args:
            question: Question for this round
            team_name: Name of competing team
            answer_hash: Hash of correct answer (if known)
            answer_salt: Salt for answer hash
            config: AppConfig instance
        """
        self.question = question
        self.team_name = team_name
        self.answer_hash = answer_hash or question.answer_hash
        self.answer_salt = answer_salt or question.answer_salt
        self.config = config or CONFIG
        
        # Create grid and game state
        self.grid = Grid(size=self.config.game.grid_size)
        self.game_state = GameState(
            question=question,
            grid=self.grid,
            time_remaining=self.config.game.time_per_round,
            base_score=self.config.scoring.base_points,
        )
        
        # Initialize services
        self.score_manager = ScoreManager(self.config.scoring)
        self.answer_checker = AnswerChecker()
        self.timer = TimerService(self.config.game.time_per_round)
        
        # Hint system needs the answer length to work
        # Generate a fake answer for hint purposes (actual answer never stored)
        fake_answer = "x" * self.question.answer_length
        self.hint_system = HintSystem(
            answer=fake_answer,
            max_hints=self.config.hints.hints_per_round
        )
        
        # Round data
        self.round: Optional[Round] = None
        self.is_started = False
        self.is_finished = False
        
        logger.debug(
            f"RoundManager initialized: question={question.id}, "
            f"team={team_name}, time={self.config.game.time_per_round}s"
        )
    
    def start(self) -> None:
        """
        Start the round.
        
        Raises:
            RuntimeError: If round already started
        """
        if self.is_started:
            raise RuntimeError("Round already started")
        
        self.timer.start()
        self.is_started = True
        
        self.round = Round(
            round_number=1,  # TODO: Get from app
            question=self.question,
            grid=self.grid,
            team_name=self.team_name,
        )
        
        logger.info(f"Round started: {self.team_name} - {self.question.id}")
    
    def reveal_cell(self, cell_index: int) -> Tuple[bool, int]:
        """
        Reveal a cell in the grid.
        
        Args:
            cell_index: Index of cell (0-15)
            
        Returns:
            Tuple of (was_new, penalty)
            - was_new: True if cell was just revealed
            - penalty: Points deducted (0, -1, -2, etc.)
            
        Raises:
            ValueError: If cell_index invalid
            RuntimeError: If round not started or finished
        """
        if not self.is_started or self.is_finished:
            raise RuntimeError("Round not active")
        
        # Reveal in grid
        was_new = self.grid.reveal_cell(cell_index)
        
        if not was_new:
            return False, 0  # Already revealed
        
        # Calculate penalty
        cells_revealed = self.grid.get_revealed_count()
        penalty = self.score_manager.get_cell_penalty(cells_revealed)
        
        # Update game state
        self.game_state.add_revealed_cell(abs(penalty))
        
        # Log in history
        if self.round:
            self.round.add_reveal_to_history(cell_index, "cell")
        
        logger.debug(f"Cell revealed: {cell_index}, penalty: {penalty}")
        
        return was_new, penalty
    
    def request_hint_random(self) -> Optional[str]:
        """
        Request a random letter hint.
        
        Returns:
            Revealed letter, or None if all letters revealed
            
        Raises:
            RuntimeError: If round not active or no hints left
        """
        if not self.is_started or self.is_finished:
            raise RuntimeError("Round not active")
        
        if self.hint_system.hints_remaining() <= 0:
            raise RuntimeError("No hints remaining")
        
        try:
            letter = self.hint_system.reveal_random_letter()
            
            # Apply penalty
            penalty = abs(self.config.hints.letter_penalty)
            self.game_state.add_revealed_letter(letter, penalty)
            
            # Log
            if self.round:
                self.round.add_reveal_to_history(ord(letter), "letter")
            
            logger.debug(f"Hint granted: {letter}, penalty: {penalty}")
            
            return letter
        
        except RuntimeError as e:
            logger.warning(f"Hint error: {e}")
            return None
    
    def check_answer(self, user_answer: str) -> bool:
        """
        Check if answer is correct.
        
        Args:
            user_answer: User's answer
            
        Returns:
            True if correct, False if wrong
        """
        if not self.is_started or self.is_finished:
            raise RuntimeError("Round not active")
        
        is_correct = self.answer_checker.verify_answer(
            user_answer,
            self.answer_hash,
            self.answer_salt
        )
        
        if not is_correct:
            # Penalty for wrong answer
            penalty = abs(self.config.scoring.wrong_answer_penalty)
            self.game_state.apply_wrong_attempt_penalty(penalty)
        
        logger.info(f"Answer checked: {is_correct} (attempts: {self.game_state.wrong_attempts})")
        
        return is_correct
    
    def update_time(self, elapsed_seconds: int = 1) -> None:
        """
        Update elapsed time.
        
        Args:
            elapsed_seconds: Seconds passed
        """
        if not self.is_started or self.is_finished:
            return
        
        self.game_state.reduce_time(elapsed_seconds)
        
        if self.game_state.is_time_expired():
            self.finish_timeout()
    
    def finish_timeout(self) -> None:
        """
        Finish round due to timeout.
        """
        if self.is_finished:
            return
        
        self.finalize(is_correct=False)
        logger.warning(f"Round finished: TIMEOUT")
    
    def finalize(self, is_correct: bool) -> ScoreRecord:
        """
        Finalize the round and calculate score.
        
        Args:
            is_correct: Whether answer was correct
            
        Returns:
            ScoreRecord with final results
            
        Raises:
            RuntimeError: If round not started
        """
        if not self.is_started:
            raise RuntimeError("Round not started")
        if self.is_finished:
            raise RuntimeError("Round already finished")
        
        # Stop timer
        self.timer.stop()
        time_used = self.timer.get_elapsed_time()
        
        # Calculate final score
        final_score = self.score_manager.calculate_final_score(
            self.grid.get_revealed_count(),
            self.game_state.get_revealed_letters_sorted().__len__(),
            self.game_state.wrong_attempts
        )
        
        # Create score record
        score_record = ScoreRecord(
            round_number=self.round.round_number if self.round else 1,
            base_points=self.config.scoring.base_points,
            cells_revealed=self.grid.get_revealed_count(),
            penalty_cells=self.score_manager.calculate_cell_penalties(
                self.grid.get_revealed_count()
            ),
            letters_revealed=len(self.game_state.revealed_letters),
            penalty_letters=self.score_manager.calculate_letter_penalties(
                len(self.game_state.revealed_letters)
            ),
            wrong_attempts=self.game_state.wrong_attempts,
            penalty_wrong=self.score_manager.calculate_wrong_attempt_penalties(
                self.game_state.wrong_attempts
            ),
            final_points=final_score,
            is_correct=is_correct,
            time_used=time_used,
        )
        
        # Finalize round
        if self.round:
            self.round.finalize(is_correct=is_correct, score_record=score_record)
        
        self.is_finished = True
        self.game_state.is_active = False
        
        logger.info(
            f"Round finalized: score={final_score}, "
            f"correct={is_correct}, time={time_used}s"
        )
        
        return score_record
    
    def get_current_display(self) -> dict:
        """
        Get current game state for UI display.
        
        Returns:
            Dictionary with display data
        """
        return {
            "score": self.game_state.current_score,
            "time_remaining": self.game_state.time_remaining,
            "time_remaining_formatted": format_time(self.game_state.time_remaining),
            "cells_revealed": self.grid.get_revealed_count(),
            "letters_revealed": self.game_state.get_revealed_letters_sorted(),
            "hint_display": self.hint_system.get_display(),
            "hints_remaining": self.hint_system.hints_remaining(),
            "is_active": self.game_state.is_active,
        }
    
    def __str__(self) -> str:
        """String representation."""
        status = "active" if self.is_started and not self.is_finished else "inactive"
        return f"RoundManager({self.team_name}, {status})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"RoundManager(question={self.question.id}, "
            f"team={self.team_name!r}, "
            f"score={self.game_state.current_score})"
        )


def format_time(seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"
