"""
Main GUI application for Information Quiz.
Manages screens and game flow.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import logging
import sys
from pathlib import Path
from typing import List, Optional
from threading import Thread
import time

# Ensure root directory is in path for imports
_root_dir = str(Path(__file__).parent)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from app.quiz_app import QuizApp
from ui.admin_panel import AdminPanel
from ui.admin_startup_screen import AdminStartupScreen
from ui.round_screen import RoundScreen
from ui.team_creation_screen import TeamCreationScreen
from ui.difficulty_selection_screen import DifficultySelectionScreen
from ui.theme import COLORS, FONTS, WINDOW_WIDTH, WINDOW_HEIGHT
from models.question import Question
from models.team import Team
from services.round_manager import RoundManager
from services.admin_auth import AdminAuth
from services.question_loader import QuestionLoader
from config import CONFIG


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuizApplication:
    """Main application window managing all screens."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Information Quiz - Admin Panel")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.config(bg=COLORS["bg_primary"])
        
        # Setup styles
        self._setup_styles()
        
        # Game controller
        self.quiz_app = QuizApp()

        # Mode/session state
        self.game_mode = "startup"
        self.player_questions: List[Question] = []
        self.player_question_index: int = -1
        self._active_round_score_recorded = False
        
        # Current game state
        self.difficulty = "medium"  # Default difficulty
        
        # Initialize admin authentication
        # Default password: "admin" (should be changed in production)
        self.admin_auth = self._initialize_admin_auth()
        
        # Current screen state
        self.current_screen: Optional[tk.Frame] = None
        self.current_round_screen: Optional[RoundScreen] = None
        self.timer_thread: Optional[Thread] = None
        self.timer_running = False
        
        # Show startup screen initially (choose between Admin and Play modes)
        self.show_startup_screen()
        
        logger.info("QuizApplication initialized")
    
    def _setup_styles(self) -> None:
        """Setup Tkinter styles."""
        style = tk.ttk.Style()
        style.theme_use('clam')

        # Configure Combobox style with better contrast
        style.configure(
            'TCombobox',
            fieldbackground=COLORS["accent"],  # Blue background
            background=COLORS["accent"],
            foreground=COLORS["fg_primary"],  # White text
            arrowcolor=COLORS["fg_primary"]
        )

        # Hover state
        style.map('TCombobox',
            fieldbackground=[('active', COLORS["accent_hover"])],
            background=[('active', COLORS["accent_hover"])],
            foreground=[('active', COLORS["fg_primary"])]
        )
    
    def _initialize_admin_auth(self) -> AdminAuth:
        """
        Initialize AdminAuth service with default credentials.
        
        Returns:
            AdminAuth: Initialized admin authentication service
        """
        # Generate hash for default password "admin"
        # In production, this should be loaded from secure configuration
        default_password = "admin"
        password_hash, password_salt = AdminAuth.hash_password(default_password)
        
        logger.info("AdminAuth service initialized with default credentials")
        return AdminAuth(password_hash, password_salt)
    
    def show_startup_screen(self) -> None:
        """Show startup screen with Admin/Play mode selection."""
        logger.info("Showing startup screen")
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create startup screen with proper parameters
        self.current_screen = AdminStartupScreen(
            self.root,
            self.admin_auth
        )
        # Show the screen with callbacks
        self.current_screen.show(
            on_admin=self._on_admin_access,
            on_play=self._on_play_access
        )
        
        self.root.title("Information Quiz - Mode Selection")
    
    def _on_admin_access(self) -> None:
        """Handle admin access - show admin panel."""
        logger.info("Admin access granted, showing admin panel")
        self.game_mode = "admin"
        self.show_admin_panel()
    
    def _on_play_access(self) -> None:
        """Handle play access - start player game mode."""
        logger.info("Play mode selected, showing team creation")
        self.game_mode = "player"
        self.show_team_creation()
    
    def show_team_creation(self) -> None:
        """Show team creation screen."""
        logger.info("Showing team creation screen")
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create team creation screen
        self.current_screen = TeamCreationScreen(
            self.root,
            on_team_created=self._on_team_created
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        self.root.title("Information Quiz - Vytvoření týmu")
    
    def _on_team_created(self, team: Optional[Team]) -> None:
        """
        Handle team creation.
        
        Args:
            team: Created Team or None if cancelled
        """
        if team is None:
            logger.info("Team creation cancelled, showing startup screen")
            self.show_startup_screen()
            return
        
        logger.info(f"Team created: {team.name}")
        
        # Add team to quiz app
        self.quiz_app.add_team(team)
        
        # Show difficulty selection
        self.show_difficulty_selection(team.name)
    
    def show_difficulty_selection(self, team_name: str) -> None:
        """
        Show difficulty selection screen.
        
        Args:
            team_name: Name of the team
        """
        logger.info(f"Showing difficulty selection for team: {team_name}")
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create difficulty selection screen
        self.current_screen = DifficultySelectionScreen(
            self.root,
            team_name=team_name,
            on_difficulty_selected=self._on_difficulty_selected
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        self.root.title("Information Quiz - Výběr obtížnosti")
    
    def _on_difficulty_selected(self, difficulty: Optional[str]) -> None:
        """
        Handle difficulty selection.

        Args:
            difficulty: Selected difficulty ('easy', 'medium', 'hard') or None if cancelled
        """
        if difficulty is None:
            logger.info("Difficulty selection cancelled, showing team creation")
            self.show_team_creation()
            return

        logger.info(f"Difficulty selected: {difficulty}")

        # Store difficulty
        self.difficulty = difficulty

        # Load questions and filter by difficulty
        self._start_game_with_difficulty(difficulty)

    def _start_game_with_difficulty(self, difficulty: str) -> None:
        """
        Start game with questions of selected difficulty.
        Automatically selects first matching question.

        Args:
            difficulty: Selected difficulty level
        """
        try:
            loader = QuestionLoader(CONFIG.questions_json)
            all_questions = loader.load_all()

            # Filter questions by difficulty
            filtered_questions = [q for q in all_questions if q.difficulty == difficulty]

            if not filtered_questions:
                messagebox.showerror("Chyba", f"Žádné otázky nenalezeny pro obtížnost '{difficulty}'")
                self.show_difficulty_selection(self.quiz_app.teams[-1].name if self.quiz_app.teams else "Team")
                return

            self.player_questions = filtered_questions
            self.player_question_index = 0

            # Start with first question
            first_question = self.player_questions[self.player_question_index]
            self._start_player_round(first_question)

        except Exception as e:
            logger.error(f"Error starting game: {e}")
            messagebox.showerror("Chyba", f"Nepodařilo se spustit hru: {e}")

    def _start_player_round(self, question: Question) -> None:
        """
        Start a round in player mode.

        Args:
            question: Selected Question object
        """
        logger.info(f"Player starting round with question {question.id}")

        try:
            # Get current team
            current_team = self.quiz_app.get_current_team()

            if not current_team:
                messagebox.showerror("Chyba", "Žádný tým není zaregistrován")
                return

            # Create round through QuizApp
            round_manager = self.quiz_app.start_round(question)

            # Reset round-scoped score display and recording guard
            current_team.reset_round()
            self._active_round_score_recorded = False

            # Start the roundmanager
            round_manager.start()

            # Show round screen
            self.show_round_screen(round_manager, team_total_score=current_team.total_score)

            # Start timer update thread
            self._start_timer_thread(round_manager)

        except Exception as e:
            logger.error(f"Error starting round: {e}")
            messagebox.showerror("Chyba", f"Nepodařilo se spustit kolo: {e}")

    def show_admin_panel(self) -> None:
        """Show admin panel for question selection (admin mode)."""
        logger.info("Showing admin panel")
        self.game_mode = "admin"
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create admin panel
        self.current_screen = AdminPanel(
            self.root,
            on_start_round=self._on_admin_start_round,
            on_back=self._on_admin_panel_back
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        self.root.title("Information Quiz - Admin Panel")
    
    def _on_admin_panel_back(self) -> None:
        """Go back from admin panel to startup screen."""
        self.show_startup_screen()
    
    def _on_admin_start_round(self, question: Question) -> None:
        """
        Start a new round with selected question (admin mode).
        
        Args:
            question: Selected Question object
        """
        logger.info(f"Starting round with question {question.id}")
        
        try:
            # Create round through QuizApp
            round_manager = self.quiz_app.start_round(question)
            self._active_round_score_recorded = False
            
            # Start the roundmanager
            round_manager.start()
            
            # Show round screen
            current_team = self.quiz_app.get_current_team()
            team_total = current_team.total_score if current_team else 0
            self.show_round_screen(round_manager, team_total_score=team_total)
            
            # Start timer update thread
            self._start_timer_thread(round_manager)
            
        except Exception as e:
            logger.error(f"Error starting round: {e}")
            messagebox.showerror("Error", f"Failed to start round: {e}")
    
    def show_round_screen(self, round_manager: RoundManager, team_total_score: int = 0) -> None:
        """
        Show game playing screen.
        
        Args:
            round_manager: Active RoundManager
        """
        logger.info("Showing round screen")
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create round screen
        self.current_round_screen = RoundScreen(
            self.root,
            round_manager,
            on_round_finished=self.show_results,
            team_total_score=team_total_score,
        )
        self.current_screen = self.current_round_screen
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        self.root.title("Information Quiz - Playing")
    
    def _start_timer_thread(self, round_manager: RoundManager) -> None:
        """
        Start background timer update thread.
        
        Args:
            round_manager: Active RoundManager
        """
        self.timer_running = True
        self.timer_thread = Thread(
            target=self._timer_loop,
            args=(round_manager,),
            daemon=True
        )
        self.timer_thread.start()
    
    def _timer_loop(self, round_manager: RoundManager) -> None:
        """
        Background timer update loop.
        
        Args:
            round_manager: Active RoundManager
        """
        logger.info("Timer thread started")
        
        while self.timer_running:
            try:
                # Update manager time
                round_manager.update_time(0.1)  # 100ms
                
                # Get remaining time
                remaining = round_manager.timer.get_remaining_time()
                
                # Update UI
                if self.current_round_screen:
                    self.current_round_screen.update_timer(remaining)
                
                # Check timeout
                if round_manager.timer.is_time_expired():
                    logger.warning("Time expired")
                    self.timer_running = False
                    score_record = round_manager.finalize(is_correct=False)
                    
                    # Schedule UI update on main thread
                    self.root.after(0, self._on_timeout, score_record)
                    break
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Timer loop error: {e}")
                break
    
    def _on_timeout(self, score_record) -> None:
        """
        Handle round timeout.
        
        Args:
            score_record: Final ScoreRecord
        """
        logger.info(f"Round timeout: {score_record}")
        
        messagebox.showinfo(
            "Time's Up!",
            f"Time expired!\nFinal score: {score_record.final_points}"
        )
        
        self.show_results(score_record)

    def _record_active_round_score_once(self, score_record) -> int:
        """Record active round score to current team once and return team total."""
        team = self.quiz_app.get_current_team()
        if team is None:
            return 0

        if not self._active_round_score_recorded:
            team.add_round_score(score_record.final_points)
            self._active_round_score_recorded = True

        return team.total_score

    def _advance_player_question_if_available(self, score_record) -> bool:
        """Advance to next player question if available. Returns True when advanced."""
        total_after_round = self._record_active_round_score_once(score_record)

        next_index = self.player_question_index + 1
        if next_index >= len(self.player_questions):
            return False

        self.player_question_index = next_index
        next_question = self.player_questions[self.player_question_index]

        self._show_between_questions_screen(score_record, total_after_round, next_question)
        return True

    def _show_between_questions_screen(self, score_record, total_after_round: int, next_question: Question) -> None:
        """Show in-app transition screen between player questions (no popup)."""
        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = tk.Frame(self.root, bg=COLORS["bg_primary"])
        self.current_screen.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self.current_screen,
            text="Otázka Dokončena",
            font=FONTS["title"],
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"],
        ).pack(pady=24)

        card = tk.Frame(self.current_screen, bg=COLORS["bg_secondary"])
        card.pack(fill=tk.BOTH, expand=True, padx=70, pady=30)

        tk.Label(
            card,
            text=f"Skóre kola: {score_record.final_points}",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"],
        ).pack(pady=18)

        tk.Label(
            card,
            text=f"Celkové skóre: {total_after_round}",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["accent"],
        ).pack(pady=10)

        tk.Label(
            card,
            text=f"Další otázka: {self.player_question_index + 1}/{len(self.player_questions)}",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"],
        ).pack(pady=12)

        tk.Button(
            self.current_screen,
            text="Pokračovat",
            command=lambda: self._start_player_round(next_question),
            bg=COLORS["accent"],
            fg=COLORS["fg_primary"],
            font=FONTS["body"],
            width=20,
            height=2,
        ).pack(pady=20)

        self.root.title("Information Quiz - Další otázka")
    
    def show_results(self, score_record) -> None:
        """
        Show results screen.
        
        Args:
            score_record: Final ScoreRecord
        """
        logger.info(f"Showing results: {score_record}")
        
        # Stop timer
        self.timer_running = False

        # Player mode: automatically continue to next question when available.
        if self.game_mode == "player" and self._advance_player_question_if_available(score_record):
            return

        total_after_round = self._record_active_round_score_once(score_record)
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Simple results frame
        self.current_screen = tk.Frame(
            self.root,
            bg=COLORS["bg_primary"]
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        is_player_set_finished = self.game_mode == "player"

        # Title
        tk.Label(
            self.current_screen,
            text="Výsledky",
            font=FONTS["title"],
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=20)
        
        # Results
        results_frame = tk.Frame(
            self.current_screen,
            bg=COLORS["bg_secondary"]
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        cell_penalty = getattr(score_record, "penalty_cells", getattr(score_record, "cell_penalty", 0))
        letter_penalty = getattr(score_record, "penalty_letters", getattr(score_record, "letter_penalty", 0))
        wrong_penalty = getattr(score_record, "penalty_wrong", getattr(score_record, "wrong_penalty", 0))
        current_team = self.quiz_app.get_current_team()
        team_name = current_team.name if current_team else "-"
        player_name = current_team.members[0] if current_team and current_team.members else "-"

        if is_player_set_finished:
            tk.Label(
                results_frame,
                text="Sada Dokončena",
                font=FONTS["heading"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["fg_primary"],
            ).pack(pady=10)

            identity_frame = tk.Frame(
                results_frame,
                bg=COLORS["accent"],
            )
            identity_frame.pack(fill=tk.X, padx=80, pady=(8, 12))

            tk.Label(
                identity_frame,
                text=f"Tým: {team_name}",
                font=FONTS["heading"],
                bg=COLORS["accent"],
                fg=COLORS["bg_primary"],
            ).pack(pady=(10, 4))

            tk.Label(
                identity_frame,
                text=f"Hráč: {player_name}",
                font=FONTS["body"],
                bg=COLORS["accent"],
                fg=COLORS["bg_primary"],
            ).pack(pady=(0, 10))
        else:
            question_id = getattr(score_record, "question_id", None)
            if question_id is None and self.current_round_screen:
                question_id = self.current_round_screen.round_manager.question.id
            if question_id is None:
                question_id = "-"

            tk.Label(
                results_frame,
                text=f"Otázka: {question_id}",
                font=FONTS["heading"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["fg_primary"],
            ).pack(pady=10)

            tk.Label(
                results_frame,
                text=f"Správně: {'ANO' if score_record.is_correct else 'NE'}",
                font=FONTS["heading"],
                bg=COLORS["bg_secondary"],
                fg=COLORS["success"] if score_record.is_correct else COLORS["danger"],
            ).pack(pady=10)
        
        tk.Label(
            results_frame,
            text=f"Skóre kola: {score_record.final_points}",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=20)

        tk.Label(
            results_frame,
            text=f"Celkové skóre týmu: {total_after_round}",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["accent"],
        ).pack(pady=6)
        
        # Details
        details_text = (
            f"Odhalená políčka: {score_record.cells_revealed}\n"
            f"Penalizace políček: {cell_penalty}\n"
            f"Odhalená písmena: {score_record.letters_revealed}\n"
            f"Penalizace písmen: {letter_penalty}\n"
            f"Špatné pokusy: {score_record.wrong_attempts}\n"
            f"Penalizace špatných pokusů: {wrong_penalty}"
        )
        
        tk.Label(
            results_frame,
            text=details_text,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"],
            justify=tk.LEFT
        ).pack(pady=10)
        
        # Back button
        if self.game_mode == "player":
            back_text = "Zpět na úvod"
            back_command = self.show_startup_screen
        else:
            back_text = "Zpět do adminu"
            back_command = self._on_back_to_admin

        tk.Button(
            self.current_screen,
            text=back_text,
            command=back_command,
            bg=COLORS["accent"],
            fg=COLORS["fg_primary"],
            font=FONTS["body"],
            width=20,
            height=2
        ).pack(pady=20)
        
        self.root.title("Information Quiz - Výsledky")
    
    def _on_back_to_admin(self) -> None:
        """Return to admin panel."""
        logger.info("Returning to admin panel")
        self.show_admin_panel()


def main():
    """Main entry point."""
    logger.info("Starting Information Quiz Application")
    
    root = tk.Tk()
    app = QuizApplication(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted")
    finally:
        app.timer_running = False
        logger.info("Application closed")


if __name__ == "__main__":
    main()
