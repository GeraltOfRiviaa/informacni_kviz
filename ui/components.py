"""
Common UI components for Tkinter GUI.
Reusable widgets and dialogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional


class ModernButton(tk.Button):
    """Modern-looking button with hover effects."""
    
    def __init__(self, parent, text: str, command: Callable = None,
                 bg_color: str = "#0078d4", fg_color: str = "white",
                 width: int = 10, height: int = 2, **kwargs):
        """
        Initialize button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Callback function
            bg_color: Background color
            fg_color: Foreground color
            width: Width in characters
            height: Height in lines
        """
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=("Arial", 11, "bold"),
            width=width,
            height=height,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self._lighten_color(bg_color),
            activeforeground=fg_color,
            **kwargs
        )
        
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _lighten_color(self, color: str) -> str:
        """Lighten hex color for hover effect."""
        # Simple lightening: remove '#' and increase values
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.config(bg=self._lighten_color(self.bg_color))
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.config(bg=self.bg_color)


class GridButton(tk.Button):
    """Button for grid cells (4x4 puzzle)."""
    
    def __init__(self, parent, grid_index: int, command: Callable = None,
                 size: int = 80, **kwargs):
        """
        Initialize grid cell button.
        
        Args:
            parent: Parent widget
            grid_index: Cell index (0-15)
            command: Callback on click
            size: Button size in pixels
        """
        super().__init__(
            parent,
            text="?",
            command=lambda: command(grid_index) if command else None,
            width=size,
            height=size,
            bg="#505050",
            fg="white",
            font=("Arial", 16, "bold"),
            relief=tk.RAISED,
            cursor="hand2",
            activebackground="#606060",
        )
        
        self.grid_index = grid_index
        self.is_revealed = False
        self.size = size
    
    def reveal(self) -> None:
        """Mark cell as revealed."""
        self.is_revealed = True
        self.config(bg="#2d2d2d", relief=tk.SUNKEN, state=tk.DISABLED)
    
    def hide(self) -> None:
        """Mark cell as hidden."""
        self.is_revealed = False
        self.config(bg="#505050", relief=tk.RAISED, state=tk.NORMAL)


class TimerWidget(tk.Frame):
    """Display countdown timer."""
    
    def __init__(self, parent, **kwargs):
        """Initialize timer widget."""
        super().__init__(parent, **kwargs)
        
        self.label = tk.Label(
            self,
            text="10:00",
            font=("Arial", 20, "bold"),
            fg="#ff0000"
        )
        self.label.pack()
    
    def update_time(self, remaining_seconds: int) -> None:
        """
        Update displayed time.
        
        Args:
            remaining_seconds: Seconds remaining
        """
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Color based on time remaining
        if remaining_seconds > 120:
            color = "#00aa00"  # Green
        elif remaining_seconds > 60:
            color = "#ffaa00"  # Orange
        else:
            color = "#ff0000"  # Red
        
        self.label.config(text=time_str, fg=color)


class ScoreDisplay(tk.Frame):
    """Display current score."""
    
    def __init__(self, parent, **kwargs):
        """Initialize score display."""
        super().__init__(parent, **kwargs)
        
        tk.Label(
            self,
            text="Score:",
            font=("Arial", 12),
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=5)
        
        self.score_label = tk.Label(
            self,
            text="120",
            font=("Arial", 16, "bold"),
            fg="#00aa00"
        )
        self.score_label.pack(side=tk.LEFT, padx=5)
    
    def update_score(self, score: int) -> None:
        """Update displayed score."""
        self.score_label.config(text=str(score))


class HintDisplay(tk.Frame):
    """Display current answer with hints."""
    
    def __init__(self, parent, answer_length: int = 10, **kwargs):
        """
        Initialize hint display.
        
        Args:
            parent: Parent widget
            answer_length: Length of answer
        """
        super().__init__(parent, **kwargs)
        
        self.answer_length = answer_length
        
        tk.Label(
            self,
            text="Answer:",
            font=("Arial", 11),
            fg="#ffffff"
        ).pack()
        
        self.hint_label = tk.Label(
            self,
            text="_" * answer_length,
            font=("Courier", 14, "bold"),
            fg="#ffaa00"
        )
        self.hint_label.pack(pady=5)
    
    def update_display(self, hint_text: str) -> None:
        """
        Update hint display.
        
        Args:
            hint_text: Text to display (e.g., "S_eve J_bs")
        """
        self.hint_label.config(text=hint_text)


class InputField(tk.Frame):
    """Text input field for answer submission."""
    
    def __init__(self, parent, on_submit: Callable = None, **kwargs):
        """
        Initialize input field.
        
        Args:
            parent: Parent widget
            on_submit: Callback on Enter
        """
        super().__init__(parent, **kwargs)
        
        tk.Label(
            self,
            text="Your Answer:",
            font=("Arial", 11),
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=5)
        
        self.entry = tk.Entry(
            self,
            font=("Arial", 12),
            width=30,
            bg="#3d3d3d",
            fg="#ffffff",
            insertbackground="white"
        )
        self.entry.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        if on_submit:
            self.entry.bind("<Return>", lambda e: on_submit(self.get_text()))
    
    def get_text(self) -> str:
        """Get input text."""
        return self.entry.get().strip()
    
    def clear(self) -> None:
        """Clear input field."""
        self.entry.delete(0, tk.END)
    
    def focus(self) -> None:
        """Focus on input field."""
        self.entry.focus()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Component Test")
    root.config(bg="#1e1e1e")
    
    # Test ModernButton
    ModernButton(root, "Click Me", bg_color="#0078d4").pack(pady=10)
    
    # Test TimerWidget
    timer = TimerWidget(root, bg="#1e1e1e")
    timer.pack(pady=10)
    timer.update_time(145)
    
    # Test ScoreDisplay
    score = ScoreDisplay(root, bg="#1e1e1e")
    score.pack(pady=10)
    score.update_score(95)
    
    root.mainloop()
