"""Obrazovka registrace týmu a hráče před začátkem hry."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable
import logging

from ui.theme import COLORS, FONTS
from ui.components import ModernButton
from models.team import Team

logger = logging.getLogger(__name__)


class TeamCreationScreen(tk.Frame):
    """Formulář pro vytvoření soutěžního týmu."""
    
    def __init__(self, parent, on_team_created: Optional[Callable] = None, **kwargs):
        """Inicializuje registrační obrazovku týmu."""
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        
        self.on_team_created = on_team_created
        self.created_team: Optional[Team] = None
        
        self._build_ui()
        logger.info("Obrazovka TeamCreationScreen byla inicializována")
    
    def _build_ui(self) -> None:
        """Vytvoří rozhraní registrační obrazovky."""
        # Top: Title
        title_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=80)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            title_frame,
            text="TÝM - REGISTRACE",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Center in middle
        center_frame = tk.Frame(main_frame, bg=COLORS["bg_primary"])
        center_frame.pack(expand=True)
        
        # Jméno týmu
        tk.Label(
            center_frame,
            text="Jméno týmu:",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"]
        ).pack(anchor=tk.W, pady=(20, 10))
        
        self.team_name_var = tk.StringVar()
        team_name_entry = tk.Entry(
            center_frame,
            textvariable=self.team_name_var,
            font=FONTS["body"],
            width=40,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"],
            insertbackground=COLORS["accent"]
        )
        team_name_entry.pack(pady=10, ipady=8)
        team_name_entry.focus()
        
        # Jméno hráče
        tk.Label(
            center_frame,
            text="Vaše jméno:",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["fg_primary"]
        ).pack(anchor=tk.W, pady=(40, 10))
        
        self.player_name_var = tk.StringVar()
        player_name_entry = tk.Entry(
            center_frame,
            textvariable=self.player_name_var,
            font=FONTS["body"],
            width=40,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"],
            insertbackground=COLORS["accent"]
        )
        player_name_entry.pack(pady=10, ipady=8)
        
        # Bottom buttons
        button_frame = tk.Frame(center_frame, bg=COLORS["bg_primary"])
        button_frame.pack(pady=(60, 0))
        
        ModernButton(
            button_frame,
            "Pokračovat",
            command=self._handle_submit,
            bg_color=COLORS["success"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        ModernButton(
            button_frame,
            "Zrušit",
            command=self._handle_cancel,
            bg_color=COLORS["danger"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
    
    def _handle_submit(self) -> None:
        """Zpracuje odeslání formuláře."""
        team_name = self.team_name_var.get().strip()
        player_name = self.player_name_var.get().strip()
        
        # Validace
        if not team_name:
            messagebox.showerror("Chyba", "Prosím zadejte jméno týmu")
            return
        
        if not player_name:
            messagebox.showerror("Chyba", "Prosím zadejte své jméno")
            return
        
        # Vytvoření týmu s jedním hráčem
        try:
            team = Team(name=team_name, members=[player_name])
            self.created_team = team

            logger.info(f"Vytvořen tým: {team.name}, hráč: {player_name}")
            
            if self.on_team_created:
                self.on_team_created(team)
        
        except ValueError as e:
            messagebox.showerror("Chyba", str(e))
            logger.error(f"Chyba při vytváření týmu: {e}")
    
    def _handle_cancel(self) -> None:
        """Zpracuje zrušení registrace."""
        if messagebox.askyesno("Zrušit", "Chcete zrušit vytvoření týmu?"):
            # Informuje callback o zrušení registrace
            if self.on_team_created:
                self.on_team_created(None)
    
    def get_team(self) -> Optional[Team]:
        """Vrátí vytvořený tým."""
        return self.created_team


if __name__ == "__main__":
    print("Komponenta TeamCreationScreen - použití viz main.py")
