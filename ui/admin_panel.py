"""
AdminPanel - Question selection and game management screen.
Allows operator to select questions without revealing answers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import logging

from ui.components import ModernButton
from ui.theme import COLORS, FONTS
from services.question_loader import QuestionLoader
from models.question import Question
from config import CONFIG


logger = logging.getLogger(__name__)


class AdminPanel(tk.Frame):
    """
    Admin panel for selecting and starting rounds.
    
    Features:
    - Question list with filtering
    - Category and difficulty filters
    - Preview (without revealing answer)
    - Start round button
    """
    
    def __init__(self, parent, on_start_round: Callable = None, **kwargs):
        """
        Initialize AdminPanel.
        
        Args:
            parent: Parent widget
            on_start_round: Callback when round starts (receives Question)
        """
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        
        self.on_start_round = on_start_round
        self.loader = QuestionLoader(CONFIG.questions_json)
        self.all_questions = self.loader.load_all()
        self.selected_question: Optional[Question] = None
        
        self._build_ui()
        logger.info(f"AdminPanel initialized with {len(self.all_questions)} questions")
    
    def _build_ui(self) -> None:
        """Build UI layout."""
        # Top: Title
        title_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=60)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            title_frame,
            text="Question Selection",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        # Filters
        self._build_filters(title_frame)
        
        # Main content: Left (list) + Right (preview)
        main_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self._build_question_list(main_frame)
        self._build_preview(main_frame)
        
        # Bottom: Action buttons
        self._build_bottom(self)
    
    def _build_filters(self, parent) -> None:
        """Build filter controls."""
        filter_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Category filter
        tk.Label(
            filter_frame,
            text="Category:",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT, padx=5)
        
        categories = ["All"] + list(set(q.category for q in self.all_questions))
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_list())
        
        # Difficulty filter
        tk.Label(
            filter_frame,
            text="Difficulty:",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT, padx=5)
        
        difficulties = ["All"] + list(set(q.difficulty for q in self.all_questions))
        self.difficulty_var = tk.StringVar(value="All")
        self.difficulty_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.difficulty_var,
            values=difficulties,
            state="readonly",
            width=15
        )
        self.difficulty_combo.pack(side=tk.LEFT, padx=5)
        self.difficulty_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_list())
    
    def _build_question_list(self, parent) -> None:
        """Build question list panel."""
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(
            list_frame,
            text="Questions",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        # Scrollbar + Listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.question_listbox = tk.Listbox(
            list_frame,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"],
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=FONTS["body"],
            height=15,
            width=40
        )
        self.question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.question_listbox.bind("<<ListboxSelect>>", self._on_question_select)
        scrollbar.config(command=self.question_listbox.yview)
        
        # Populate list
        self._refresh_list()
    
    def _build_preview(self, parent) -> None:
        """Build question preview panel."""
        preview_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10)
        
        tk.Label(
            preview_frame,
            text="Preview",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        # Info frame
        info_frame = tk.Frame(preview_frame, bg=COLORS["bg_tertiary"])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ID
        tk.Label(
            info_frame,
            text="ID:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_id = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_id.pack(anchor=tk.W, padx=10)
        
        # Category
        tk.Label(
            info_frame,
            text="Category:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_category = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_category.pack(anchor=tk.W, padx=10)
        
        # Difficulty
        tk.Label(
            info_frame,
            text="Difficulty:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_difficulty = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_difficulty.pack(anchor=tk.W, padx=10)
        
        # Answer length
        tk.Label(
            info_frame,
            text="Answer Length:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_length = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_length.pack(anchor=tk.W, padx=10)
        
        # Note
        tk.Label(
            preview_frame,
            text="⚠ Answer is never shown\nfor security reasons",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["warning"],
            justify=tk.CENTER
        ).pack(pady=10)
    
    def _build_bottom(self, parent) -> None:
        """Build bottom action buttons."""
        button_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ModernButton(
            button_frame,
            "Start Round",
            command=self._handle_start,
            bg_color=COLORS["success"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        ModernButton(
            button_frame,
            "Quit",
            command=self._handle_quit,
            bg_color=COLORS["danger"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
    
    def _refresh_list(self) -> None:
        """Refresh question list based on filters."""
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        
        # Filter questions
        filtered = self.all_questions
        
        if category != "All":
            filtered = [q for q in filtered if q.category == category]
        
        if difficulty != "All":
            filtered = [q for q in filtered if q.difficulty == difficulty]
        
        # Update listbox
        self.question_listbox.delete(0, tk.END)
        for q in filtered:
            self.question_listbox.insert(
                tk.END,
                f"[{q.id}] {q.category} ({q.difficulty})"
            )
        
        logger.info(f"Filtered to {len(filtered)} questions")
    
    def _on_question_select(self, event) -> None:
        """Handle question selection."""
        selection = self.question_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        item_text = self.question_listbox.get(index)
        
        # Extract ID from text
        question_id = item_text.split('[')[1].split(']')[0]
        
        # Find question
        self.selected_question = self.loader.get_by_id(question_id)
        
        if self.selected_question:
            # Update preview
            self.preview_id.config(text=self.selected_question.id)
            self.preview_category.config(text=self.selected_question.category)
            self.preview_difficulty.config(text=self.selected_question.difficulty)
            self.preview_length.config(text=str(self.selected_question.answer_length))
            
            logger.info(f"Question selected: {question_id}")
    
    def _handle_start(self) -> None:
        """Start round with selected question."""
        if not self.selected_question:
            messagebox.showwarning("No Selection", "Please select a question first")
            return
        
        logger.info(f"Starting round with question {self.selected_question.id}")
        
        if self.on_start_round:
            self.on_start_round(self.selected_question)
    
    def _handle_quit(self) -> None:
        """Quit admin panel."""
        if messagebox.askyesno("Quit", "Exit application?"):
            self.master.quit()


if __name__ == "__main__":
    print("AdminPanel component - see main.py for usage")
