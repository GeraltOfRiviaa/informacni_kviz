"""
Main GUI application for Information Quiz.
Manages screens and game flow.
"""

import tkinter as tk
from tkinter import messagebox
import logging
from typing import Optional
from threading import Thread
import time

from app.quiz_app import QuizApp
from ui.admin_panel import AdminPanel
from ui.round_screen import RoundScreen
from ui.theme import COLORS, FONTS, WINDOW_WIDTH, WINDOW_HEIGHT
from models.question import Question
from services.round_manager import RoundManager


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
        
        # Current screen state
        self.current_screen: Optional[tk.Frame] = None
        self.current_round_screen: Optional[RoundScreen] = None
        self.timer_thread: Optional[Thread] = None
        self.timer_running = False
        
        # Show admin panel initially
        self.show_admin_panel()
        
        logger.info("QuizApplication initialized")
    
    def _setup_styles(self) -> None:
        """Setup Tkinter styles."""
        style = tk.ttk.Style()
        style.theme_use('clam')
        
        # Configure Combobox style
        style.configure(
            'TCombobox',
            fieldbackground=COLORS["bg_tertiary"],
            background=COLORS["bg_tertiary"],
            foreground=COLORS["fg_primary"]
        )
    
    def show_admin_panel(self) -> None:
        """Show admin panel for question selection."""
        logger.info("Showing admin panel")
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create admin panel
        self.current_screen = AdminPanel(
            self.root,
            on_start_round=self._on_start_round
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        self.root.title("Information Quiz - Admin Panel")
    
    def _on_start_round(self, question: Question) -> None:
        """
        Start a new round with selected question.
        
        Args:
            question: Selected Question object
        """
        logger.info(f"Starting round with question {question.id}")
        
        try:
            # Create round through QuizApp
            round_manager = self.quiz_app.start_round(question)
            
            # Start the roundmanager
            round_manager.start()
            
            # Show round screen
            self.show_round_screen(round_manager)
            
            # Start timer update thread
            self._start_timer_thread(round_manager)
            
        except Exception as e:
            logger.error(f"Error starting round: {e}")
            messagebox.showerror("Error", f"Failed to start round: {e}")
    
    def show_round_screen(self, round_manager: RoundManager) -> None:
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
            round_manager
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
                remaining = round_manager.timer_service.get_remaining_time()
                
                # Update UI
                if self.current_round_screen:
                    self.current_round_screen.update_timer(remaining)
                
                # Check timeout
                if round_manager.timer_service.is_time_expired():
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
    
    def show_results(self, score_record) -> None:
        """
        Show results screen.
        
        Args:
            score_record: Final ScoreRecord
        """
        logger.info(f"Showing results: {score_record}")
        
        # Stop timer
        self.timer_running = False
        
        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
        
        # Simple results frame
        self.current_screen = tk.Frame(
            self.root,
            bg=COLORS["bg_primary"]
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            self.current_screen,
            text="Round Complete",
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
        
        tk.Label(
            results_frame,
            text=f"Question: {score_record.question_id}",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        tk.Label(
            results_frame,
            text=f"Correct: {'✓' if score_record.is_correct else '✗'}",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["success"] if score_record.is_correct else COLORS["danger"]
        ).pack(pady=10)
        
        tk.Label(
            results_frame,
            text=f"Final Score: {score_record.final_points}",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=20)
        
        # Details
        details_text = (
            f"Cells revealed: {score_record.cells_revealed}\n"
            f"Cell penalty: {score_record.cell_penalty}\n"
            f"Letters revealed: {score_record.letters_revealed}\n"
            f"Letter penalty: {score_record.letter_penalty}\n"
            f"Wrong attempts: {score_record.wrong_attempts}\n"
            f"Wrong penalty: {score_record.wrong_penalty}"
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
        tk.Button(
            self.current_screen,
            text="Back to Admin",
            command=self._on_back_to_admin,
            bg=COLORS["accent"],
            fg=COLORS["fg_primary"],
            font=FONTS["body"],
            width=20,
            height=2
        ).pack(pady=20)
        
        self.root.title("Information Quiz - Results")
    
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
