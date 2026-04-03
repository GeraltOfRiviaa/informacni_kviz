"""
RoundScreen - Main game playing screen.
Displays puzzle grid, revealed letters, answer input, and game info.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
import logging

from PIL import ImageTk

from ui.theme import COLORS, FONTS
from services.round_manager import RoundManager
from services.image_handler import ImageHandler


logger = logging.getLogger(__name__)

# Game constants
GRID_SIZE = 4
CELL_PIXEL_SIZE = 80
CELL_GAP = 5


class GridCell(tk.Button):
    """Single grid cell for puzzle."""

    def __init__(self, parent, index: int, on_click=None, **kwargs):
        super().__init__(
            parent,
            text="?",
            width=4,
            height=1,
            font=FONTS["heading"],
            bg=COLORS["cell_hidden"],
            fg=COLORS["fg_primary"],
            activebackground=COLORS["cell_hidden"],
            activeforeground=COLORS["fg_primary"],
            relief=tk.RAISED,
            bd=1,
            cursor="hand2",
            command=lambda: on_click(index) if on_click else None,
            **kwargs
        )
        self.index = index
        self.is_revealed = False

    def reveal(self):
        """Mark cell as revealed."""
        self.is_revealed = True
        self.place_forget()


class RoundScreen(tk.Frame):
    """
    Main game playing screen.

    Layout:
    ┌──────────────────────────────────────────────────────────┐
    │ Body: 104        Nápověda       Poslední tah: -3  Čas: 06:23 │
    ├────────────────────────────────────────────────────────────┤
    │                                                            │
    │               [4x4 GRID]                                  │
    │                                                            │
    ├────────────────────────────────────────────────────────────┤
    │         [REVEALED LETTERS DISPLAY]                        │
    ├────────────────────────────────────────────────────────────┤
    │ [Answer Input]           [Submit Button]                  │
    ├────────────────────────────────────────────────────────────┤
    │ Nápovědy: 1. free  2. -1  3. -2  | Wrong: -20             │
    └──────────────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        parent,
        round_manager: RoundManager,
        on_round_finished: Optional[Callable] = None,
        team_total_score: int = 0,
        **kwargs,
    ):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)

        self.round_manager = round_manager
        self.on_round_finished = on_round_finished
        self.question = round_manager.question
        self.image_handler = ImageHandler(images_archive=self.round_manager.config.images_dir)
        self.image_label: Optional[tk.Label] = None
        self.image_stage: Optional[tk.Frame] = None
        self._image_preview_ref = None
        self.wrong_overlay_label: Optional[tk.Label] = None
        self._wrong_overlay_after_id: Optional[str] = None

        self.team_total_score_start = team_total_score
        self.current_score = self.round_manager.config.scoring.base_points
        self.cells_revealed = 0
        self.wrong_attempts = 0
        self.last_penalty = 0

        # Build UI
        self._build_top_bar()
        self._build_image_panel()
        self._build_grid()
        self._build_answer_section()
        self._build_info_bar()

        logger.info(f"RoundScreen initialized for question {self.question.id}")

    def _build_top_bar(self):
        """Build top information bar."""
        top_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=78)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        top_frame.pack_propagate(False)

        # Left: Score
        left_frame = tk.Frame(top_frame, bg=COLORS["bg_secondary"])
        left_frame.pack(side=tk.LEFT, padx=20, pady=15)

        tk.Label(
            left_frame,
            text="Skóre:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT)

        self.score_label = tk.Label(
            left_frame,
            text=str(self.current_score),
            font=FONTS["score"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["accent"]
        )
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.total_score_label = tk.Label(
            left_frame,
            text=f"Celkem: {self.team_total_score_start + self.current_score}",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"],
        )
        self.total_score_label.pack(side=tk.LEFT, padx=16)

        # Center: Hint label
        center_frame = tk.Frame(top_frame, bg=COLORS["bg_secondary"])
        center_frame.pack(side=tk.LEFT, expand=True)

        tk.Label(
            center_frame,
            text="Odhaluj obrázek po částech a tipni odpověď",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack()

        # Center-Right: Last penalty
        right_center = tk.Frame(top_frame, bg=COLORS["bg_secondary"])
        right_center.pack(side=tk.LEFT, padx=20)

        tk.Label(
            right_center,
            text="Poslední tah:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT)

        self.penalty_label = tk.Label(
            right_center,
            text="0 bodu",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["danger"]
        )
        self.penalty_label.pack(side=tk.LEFT, padx=10)

        # Right: Timer
        timer_frame = tk.Frame(top_frame, bg=COLORS["bg_secondary"])
        timer_frame.pack(side=tk.RIGHT, padx=20, pady=15)

        tk.Label(
            timer_frame,
            text="Čas:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT)

        round_time = self.round_manager.config.game.time_per_round
        minutes = round_time // 60
        seconds = round_time % 60

        self.timer_label = tk.Label(
            timer_frame,
            text=f"{minutes:02d}:{seconds:02d}",
            font=FONTS["timer"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["success"]
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)

    def _refresh_score_labels(self):
        """Refresh round and total score labels."""
        round_score = max(0, self.current_score)
        self.score_label.config(text=str(round_score))
        self.total_score_label.config(text=f"Celkem: {self.team_total_score_start + round_score}")

    def _build_grid(self):
        """Build 4x4 reveal grid directly over the image stage."""
        if not self.image_stage:
            return

        self.grid_buttons = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                idx = row * GRID_SIZE + col
                btn = GridCell(
                    self.image_stage,
                    idx,
                    on_click=self._handle_cell_click
                )
                btn.place(
                    relx=col / GRID_SIZE,
                    rely=row / GRID_SIZE,
                    relwidth=1 / GRID_SIZE,
                    relheight=1 / GRID_SIZE,
                )
                self.grid_buttons.append(btn)

    def _build_image_panel(self):
        """Build image panel showing masked image with progressively revealed cells."""
        image_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        image_frame.pack(pady=6)

        tk.Label(
            image_frame,
            text="Obrázek",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"],
        ).pack(pady=(0, 5))

        self.image_stage = tk.Frame(
            image_frame,
            bg=COLORS["border"],
            width=920,
            height=460,
            relief=tk.SOLID,
            bd=2,
        )
        self.image_stage.pack()
        self.image_stage.pack_propagate(False)

        self.image_label = tk.Label(
            self.image_stage,
            text="Načítám obrázek...",
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"],
        )
        self.image_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.wrong_overlay_label = tk.Label(
            self.image_stage,
            text="Špatná odpověď",
            font=FONTS["title"],
            bg="#7f1d1d",
            fg="#ffffff",
            padx=24,
            pady=12,
            relief=tk.SOLID,
            bd=2,
        )
        self.wrong_overlay_label.place_forget()

        self._update_image_preview()

    def _show_wrong_answer_overlay(self) -> None:
        """Show centered wrong-answer overlay over image for 5 seconds."""
        if not self.wrong_overlay_label:
            return

        if self._wrong_overlay_after_id:
            self.after_cancel(self._wrong_overlay_after_id)
            self._wrong_overlay_after_id = None

        self.wrong_overlay_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.wrong_overlay_label.lift()
        self._wrong_overlay_after_id = self.after(5000, self._hide_wrong_answer_overlay)

    def _hide_wrong_answer_overlay(self) -> None:
        """Hide wrong-answer overlay label."""
        if self.wrong_overlay_label:
            self.wrong_overlay_label.place_forget()
        self._wrong_overlay_after_id = None

    def _update_image_preview(self):
        """Render image preview and keep overlay grid in sync."""
        if not self.image_label:
            return

        try:
            image = self.image_handler.load_image(self.question.image_id)
            preview = image.copy()
            preview.thumbnail((920, 460))

            self._image_preview_ref = ImageTk.PhotoImage(preview)
            self.image_label.config(image=self._image_preview_ref, text="")
        except Exception as exc:
            logger.warning(f"Image preview failed for {self.question.image_id}: {exc}")
            self.image_label.config(
                image="",
                text=f"Obrázek {self.question.image_id} se nepodařilo načíst",
            )

    def _build_answer_section(self):
        """Build answer display and input section."""
        # Revealed letters display
        answer_display_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        answer_display_frame.pack(pady=10)

        # Create letter boxes for answer (use answer_length, not plaintext)
        self.letter_boxes = []
        answer_length = self.question.answer_length

        for i in range(answer_length):
            box = tk.Label(
                answer_display_frame,
                text="_",
                font=FONTS["heading"],
                width=3,
                height=1,
                bg="#e2e8f0",
                fg=COLORS["fg_secondary"],
                relief=tk.SOLID,
                bd=2
            )
            box.pack(side=tk.LEFT, padx=3)
            self.letter_boxes.append(box)

        # Input section
        input_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        input_frame.pack(pady=10, fill=tk.X, padx=20)

        self.entry = tk.Entry(
            input_frame,
            font=FONTS["body"],
            width=40,
            bg="white",
            fg=COLORS["fg_secondary"],
            insertbackground="black"
        )
        self.entry.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        self.entry.bind("<Return>", lambda e: self._handle_submit())
        self.entry.bind("<KeyRelease>", self._update_input_visualization)
        self.entry.insert(0, "Zadej odpověď")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)

        tk.Button(
            input_frame,
            text="Odeslat",
            font=FONTS["heading"],
            bg=COLORS["warning"],
            fg="white",
            width=15,
            height=1,
            command=self._handle_submit,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.LEFT, padx=5)

        self._update_input_visualization()

    def _clear_placeholder(self, event):
        """Clear placeholder text on focus."""
        if self.entry.get() == "Zadej odpověď":
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#000000")
            self._update_input_visualization()

    def _restore_placeholder(self, event):
        """Restore placeholder if empty."""
        if self.entry.get() == "":
            self.entry.insert(0, "Zadej odpověď")
            self.entry.config(fg="#999999")
        self._update_input_visualization()

    def _update_input_visualization(self, _event=None):
        """Mirror typed input into answer boxes as uppercase visualization."""
        raw_text = self.entry.get()
        if raw_text == "Zadej odpověď":
            raw_text = ""

        visual_text = raw_text.upper()

        for i, box in enumerate(self.letter_boxes):
            if i < len(visual_text):
                box.config(text=visual_text[i], fg="#000000")
            else:
                box.config(text="_", fg=COLORS["fg_secondary"])

    def _build_info_bar(self):
        """Build bottom information bar."""
        bottom_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=50)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        bottom_frame.pack_propagate(False)

        tk.Label(
            bottom_frame,
            text="Nápovědy:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(
            bottom_frame,
            text="1. políčko zdarma, další postupně body dolů. Písmeno: -1.",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"]
        ).pack(side=tk.LEFT, padx=5)

        # Right side: wrong penalty
        self.wrong_label = tk.Label(
            bottom_frame,
            text="",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["danger"],
            relief=tk.SOLID,
            bd=2,
            padx=10,
            pady=5
        )
        self.wrong_label.pack(side=tk.RIGHT, padx=10)

    def _handle_cell_click(self, index: int):
        """Handle grid cell click."""
        logger.debug(f"Cell clicked: {index}")

        if self.grid_buttons[index].is_revealed:
            return

        was_new, penalty = self.round_manager.reveal_cell(index)

        if was_new:
            self.grid_buttons[index].reveal()
            self.cells_revealed += 1
            self.current_score += penalty
            self.current_score = max(0, self.current_score)
            self.last_penalty = penalty

            # Update displays
            self._refresh_score_labels()
            self.penalty_label.config(text=f"{penalty} bodu" if penalty != 0 else "0 bodu")

            logger.info(f"Cell {index} revealed, penalty: {penalty}, score: {self.current_score}")

    def _handle_submit(self):
        """Handle answer submission."""
        answer = self.entry.get().strip()

        if not answer or answer == "Zadej odpověď":
            messagebox.showwarning("Chyba", "Prosím zadejte odpověď")
            return

        logger.info(f"Answer submitted: {answer}")

        is_correct = self.round_manager.check_answer(answer)

        if is_correct:
            logger.info("Correct answer!")
            score_record = self.round_manager.finalize(is_correct=True)
            if self.on_round_finished:
                self.on_round_finished(score_record)
            elif hasattr(self.master, "show_results"):
                self.master.show_results(score_record)
        else:
            logger.warning("Wrong answer!")
            self.wrong_attempts += 1
            wrong_penalty = abs(self.round_manager.config.scoring.wrong_answer_penalty)
            self.current_score -= wrong_penalty
            self.current_score = max(0, self.current_score)
            self._refresh_score_labels()
            self.wrong_label.config(text=f"Ztráta bodů: -{wrong_penalty}")
            self._show_wrong_answer_overlay()

            self.entry.delete(0, tk.END)
            self.entry.insert(0, "Zadej odpověď")
            self.entry.config(fg="#999999")
            self._update_input_visualization()
            self.entry.focus()

    def update_timer(self, remaining_seconds: int):
        """Update timer display."""
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        # Color based on time
        if remaining_seconds > 180:
            color = COLORS["success"]
        elif remaining_seconds > 60:
            color = COLORS["warning"]
        else:
            color = COLORS["danger"]

        self.timer_label.config(text=time_str, fg=color)
