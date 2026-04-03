"""Obrazovka pro výběr obtížnosti hry před spuštěním kola."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Literal
import logging

from ui.theme import COLORS, FONTS
from ui.components import ModernButton

logger = logging.getLogger(__name__)

DifficultyLevel = Literal["easy", "medium", "hard"]

# Popisy obtížností
DIFFICULTY_CONFIGS = {
    "easy": {
        "label": "SNADNÉ",
        "czech_label": "Snadné",
        "description": "Jednoduchý obsah\nIdea pro začátečníky",
        "time_limit": 600,  # 10 minutes
        "color": "#27ae60"
    },
    "medium": {
        "label": "STŘEDNÍ",
        "czech_label": "Střední",
        "description": "Normální úkoly\nPro všechny hráče",
        "time_limit": 600,
        "color": "#f39c12"
    },
    "hard": {
        "label": "TĚŽKÉ",
        "czech_label": "Těžké",
        "description": "Náročné otázky\nVýzva pro experty",
        "time_limit": 600,
        "color": "#e74c3c"
    }
}


class DifficultySelectionScreen(tk.Frame):
    """Obrazovka pro výběr obtížnosti soutěžního kola."""
    
    def __init__(
        self,
        parent,
        team_name: str = "Tým",
        on_difficulty_selected: Optional[Callable[[Optional[DifficultyLevel]], None]] = None,
        **kwargs
    ):
        """Inicializuje obrazovku výběru obtížnosti."""
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        
        self.team_name = team_name
        self.on_difficulty_selected = on_difficulty_selected
        self.selected_difficulty: Optional[DifficultyLevel] = None
        
        self._build_ui()
        logger.info(f"Obrazovka obtížnosti inicializována pro tým: {team_name}")
    
    def _build_ui(self) -> None:
        """Vytvoří rozložení obrazovky."""
        # Top: Title with team name
        title_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=100)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            title_frame,
            text=f"Tým: {self.team_name}",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"]
        ).pack(pady=5)
        
        tk.Label(
            title_frame,
            text="VYBERTE OBTÍŽNOST",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        # Main content
        main_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Center content
        center_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"])
        center_frame.pack(expand=True)
        
        # Tlačítka obtížnosti
        buttons_frame = tk.Frame(center_frame, bg=COLORS["bg_primary"])
        buttons_frame.pack(pady=20)
        
        self.difficulty_buttons = {}
        
        for difficulty in ["easy", "medium", "hard"]:
            config = DIFFICULTY_CONFIGS[difficulty]
            
            button_frame = tk.Frame(buttons_frame, bg=COLORS["bg_primary"])
            button_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
            
            # Tlačítko obtížnosti
            button = tk.Button(
                button_frame,
                text=config["label"],
                command=lambda d=difficulty: self._select_difficulty(d),  # type: ignore
                font=("Helvetica", 16, "bold"),
                width=15,
                height=3,
                bg=config["color"],
                fg="white",
                relief=tk.RAISED,
                bd=2,
                activebackground=self._lighten_color(config["color"]),
                activeforeground="white",
                cursor="hand2"
            )
            button.pack(pady=10)
            self.difficulty_buttons[difficulty] = button
            
            # Description
            desc_label = tk.Label(
                button_frame,
                text=config["description"],
                font=FONTS["small"],
                bg=COLORS["bg_primary"],
                fg=COLORS["fg_secondary"],
                justify=tk.CENTER
            )
            desc_label.pack(pady=10)
        
        # Bottom buttons
        button_frame = tk.Frame(center_frame, bg=COLORS["bg_primary"])
        button_frame.pack(pady=(60, 0))
        
        ModernButton(
            button_frame,
            "Spustit hru",
            command=self._handle_start,
            bg_color=COLORS["success"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        ModernButton(
            button_frame,
            "Zpět",
            command=self._handle_back,
            bg_color=COLORS["danger"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
    
    def _lighten_color(self, color: str) -> str:
        """Zesvětlí hex barvu."""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _select_difficulty(self, difficulty: DifficultyLevel) -> None:
        """Nastaví vybranou obtížnost."""
        self.selected_difficulty = difficulty
        
        # Zvýrazní vybranou obtížnost
        for d, button in self.difficulty_buttons.items():
            if d == difficulty:
                button.config(relief=tk.SUNKEN, bd=4)
            else:
                button.config(relief=tk.RAISED, bd=2)
        
        logger.info(f"Vybraná obtížnost: {difficulty}")
    
    def _handle_start(self) -> None:
        """Spustí hru s vybranou obtížností."""
        if not self.selected_difficulty:
            messagebox.showwarning("Varování", "Prosím vyberte obtížnost")
            return

        logger.info(f"Spouštím hru s obtížností: {self.selected_difficulty}")
        
        if self.on_difficulty_selected:
            self.on_difficulty_selected(self.selected_difficulty)
    
    def _handle_back(self) -> None:
        """Vrátí uživatele zpět na předchozí obrazovku."""
        if messagebox.askyesno("Zpět", "Chcete se vrátit?\nZačnete znovu s registrací týmu?"):
            if self.on_difficulty_selected:
                self.on_difficulty_selected(None)
    
    def get_selected_difficulty(self) -> Optional[DifficultyLevel]:
        """Vrátí aktuálně vybranou obtížnost."""
        return self.selected_difficulty


if __name__ == "__main__":
    print("Komponenta DifficultySelectionScreen - použití viz main.py")
