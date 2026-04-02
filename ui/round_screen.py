"""
RoundScreen - Main game playing screen.
Displays puzzle grid, image, hint system, and answer input.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import logging

from ui.components import (
    ModernButton, GridButton, TimerWidget, ScoreDisplay,
    HintDisplay, InputField
)
from ui.theme import COLORS, FONTS, GRID_SIZE, CELL_SIZE, PADDING
from services.round_manager import RoundManager


logger = logging.getLogger(__name__)


class PuzzleGrid(tk.Frame):
    """4x4 grid of puzzle cells."""
    
    def __init__(self, parent, on_cell_click: Callable = None, **kwargs):
        """
        Initialize puzzle grid.
        
        Args:
            parent: Parent widget
            on_cell_click: Callback when cell clicked (receives index)
        """
        super().__init__(parent, bg=COLORS["bg_secondary"], **kwargs)
        
        self.cells: list[GridButton] = []
        self.on_cell_click = on_cell_click
        
        # Create 4x4 grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                index = row * GRID_SIZE + col
                cell = GridButton(
                    self,
                    grid_index=index,
                    command=self._handle_click,
                    size=CELL_SIZE
                )
                cell.grid(row=row, column=col, padx=2, pady=2)
                self.cells.append(cell)
    
    def _handle_click(self, index: int) -> None:
        """Handle cell click."""
        if self.on_cell_click:
            self.on_cell_click(index)
    
    def reveal_cell(self, index: int) -> None:
        """Reveal a cell."""
        if 0 <= index < len(self.cells):
            self.cells[index].reveal()
    
    def get_revealed_count(self) -> int:
        """Get count of revealed cells."""
        return sum(1 for cell in self.cells if cell.is_revealed)


class RoundScreen(tk.Frame):
    """
    Main game playing screen.
    
    Layout:
    ┌─────────────────────────────────────┐
    │ Timer       Score       Difficulty   │
    ├────────────┬──────────────┬─────────┤
    │            │              │         │
    │ Grid 4x4   │   Image      │ Hints   │
    │            │              │ & Timer │
    │            │              │         │
    ├────────────┴──────────────┴─────────┤
    │ Answer Input | Submit | Hint | Quit │
    └─────────────────────────────────────┘
    """
    
    def __init__(self, parent, round_manager: RoundManager, **kwargs):
        """
        Initialize RoundScreen.
        
        Args:
            parent: Parent widget
            round_manager: RoundManager instance for this round
        """
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        
        self.round_manager = round_manager
        self.question = round_manager.question
        
        # Track game state
        self.current_score = 120
        self.cells_revealed = 0
        self.wrong_attempts = 0
        
        # Build UI
        self._build_top_bar()
        self._build_main_area()
        self._build_bottom_bar()
        
        logger.info(f"RoundScreen initialized for question {self.question.id}")
    
    def _build_top_bar(self) -> None:
        """Build top information bar."""
        top_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=60)
        top_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Timer
        tk.Label(
            top_frame,
            text="Time:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT, padx=10)
        
        self.timer_widget = TimerWidget(
            top_frame,
            bg=COLORS["bg_secondary"]
        )
        self.timer_widget.pack(side=tk.LEFT, padx=10)
        
        # Score
        self.score_widget = ScoreDisplay(
            top_frame,
            bg=COLORS["bg_secondary"]
        )
        self.score_widget.pack(side=tk.LEFT, padx=20)
        
        # Question category
        tk.Label(
            top_frame,
            text=f"Category: {self.question.category}",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"]
        ).pack(side=tk.LEFT, padx=10)
    
    def _build_main_area(self) -> None:
        """Build main gaming area."""
        main_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Left: Grid
        left_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"])
        left_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH)
        
        tk.Label(
            left_frame,
            text="Puzzle Grid",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        self.grid = PuzzleGrid(
            left_frame,
            on_cell_click=self._handle_cell_click
        )
        self.grid.pack()
        
        # Center: Image placeholder
        center_frame = tk.Frame(main_frame, bg=COLORS["bg_secondary"])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(
            center_frame,
            text="Image",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        self.image_frame = tk.Label(
            center_frame,
            text="[Image will be displayed here]",
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"],
            width=40,
            height=20,
            font=FONTS["body"]
        )
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right: Hint display
        right_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"])
        right_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH)
        
        tk.Label(
            right_frame,
            text="Answer",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        self.hint_display = HintDisplay(
            right_frame,
            answer_length=self.question.answer_length,
            bg=COLORS["bg_primary"]
        )
        self.hint_display.pack(pady=20)
        
        # Stats
        stats_frame = tk.Frame(right_frame, bg=COLORS["bg_secondary"])
        stats_frame.pack(fill=tk.X, padx=5, pady=10)
        
        tk.Label(
            stats_frame,
            text=f"Cells: {self.cells_revealed}/16",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"]
        ).pack(pady=5)
        
        tk.Label(
            stats_frame,
            text=f"Wrong: {self.wrong_attempts}",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["danger"] if self.wrong_attempts > 0 else COLORS["fg_secondary"]
        ).pack(pady=5)
    
    def _build_bottom_bar(self) -> None:
        """Build bottom control bar."""
        bottom_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=80)
        bottom_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        # Input field
        self.input_field = InputField(
            bottom_frame,
            on_submit=self._handle_answer_submit,
            bg=COLORS["bg_secondary"]
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(bottom_frame, bg=COLORS["bg_secondary"])
        button_frame.pack(side=tk.LEFT, padx=10)
        
        ModernButton(
            button_frame,
            "Submit",
            command=self._handle_submit_button,
            bg_color=COLORS["success"],
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            button_frame,
            "Hint",
            command=self._handle_hint_button,
            bg_color=COLORS["warning"],
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            button_frame,
            "Quit",
            command=self._handle_quit_button,
            bg_color=COLORS["danger"],
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
    
    def _handle_cell_click(self, index: int) -> None:
        """Handle grid cell click."""
        logger.debug(f"Cell clicked: {index}")
        
        # Reveal in manager
        was_new, penalty = self.round_manager.reveal_cell(index)
        
        if was_new:
            # Update UI
            self.grid.reveal_cell(index)
            self.cells_revealed += 1
            self.current_score += penalty  # penalty is negative
            
            self.score_widget.update_score(self.current_score)
            logger.info(f"Cell {index} revealed, penalty: {penalty}, score: {self.current_score}")
    
    def _handle_hint_button(self) -> None:
        """Handle hint button click."""
        logger.debug("Hint button clicked")
        
        letter = self.round_manager.request_hint_random()
        
        # Update UI
        display_text = self.round_manager.hint_system.get_display()
        self.hint_display.update_display(display_text)
        
        # Update score (penalty)
        self.current_score -= 1
        self.score_widget.update_score(self.current_score)
        
        logger.info(f"Hint revealed: {letter}, score: {self.current_score}")
    
    def _handle_answer_submit(self, answer: str) -> None:
        """Handle answer submission (Enter key)."""
        self._submit_answer(answer)
    
    def _handle_submit_button(self) -> None:
        """Handle submit button click."""
        answer = self.input_field.get_text()
        if answer:
            self._submit_answer(answer)
    
    def _submit_answer(self, answer: str) -> None:
        """Submit an answer."""
        logger.info(f"Answer submitted: {answer}")
        
        is_correct = self.round_manager.check_answer(answer)
        
        if is_correct:
            logger.info("Correct answer!")
            # Update score (win penalty)
            score_record = self.round_manager.finalize(is_correct=True)
            # Show success and quit
            tk.messagebox.showinfo(
                "Correct!",
                f"Right answer!\nFinal score: {score_record.final_points}"
            )
            self._on_round_complete(score_record)
        else:
            logger.warning("Wrong answer!")
            self.wrong_attempts += 1
            self.current_score -= 20  # Wrong penalty
            self.score_widget.update_score(self.current_score)
            self.input_field.clear()
            self.input_field.focus()
            tk.messagebox.showwarning("Wrong!", "Try again...")
    
    def _handle_quit_button(self) -> None:
        """Handle quit button."""
        if tk.messagebox.askyesno("Quit?", "End this round?"):
            score_record = self.round_manager.finalize(is_correct=False)
            self._on_round_complete(score_record)
    
    def _on_round_complete(self, score_record) -> None:
        """Called when round is complete."""
        logger.info(f"Round complete: {score_record}")
        # Trigger callback to parent
        self.master.show_results(score_record)
    
    def update_timer(self, remaining_seconds: int) -> None:
        """Update timer display."""
        self.timer_widget.update_time(remaining_seconds)


if __name__ == "__main__":
    # Test RoundScreen requires RoundManager setup
    print("RoundScreen component - see main.py for usage")
