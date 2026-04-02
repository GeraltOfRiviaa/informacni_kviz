"""
Tests for UI components.
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch

from ui.components import (
    ModernButton, GridButton, TimerWidget, ScoreDisplay,
    HintDisplay, InputField
)
from ui.round_screen import PuzzleGrid, RoundScreen
from ui.admin_panel import AdminPanel
from ui.theme import COLORS, FONTS


class TestModernButton:
    """Test ModernButton widget."""
    
    def test_button_creation(self):
        """Test creating a modern button."""
        root = tk.Tk()
        try:
            button = ModernButton(root, "Test", bg_color="#0078d4")
            assert button.cget("text") == "Test"
            assert button.cget("bg") == "#0078d4"
        finally:
            root.destroy()
    
    def test_button_command(self):
        """Test button command callback."""
        root = tk.Tk()
        callback = Mock()
        try:
            button = ModernButton(root, "Test", command=callback)
            button.invoke()
            callback.assert_called_once()
        finally:
            root.destroy()


class TestGridButton:
    """Test GridButton widget."""
    
    def test_grid_button_creation(self):
        """Test creating a grid button."""
        root = tk.Tk()
        try:
            button = GridButton(root, grid_index=5)
            assert button.grid_index == 5
            assert not button.is_revealed
        finally:
            root.destroy()
    
    def test_grid_button_reveal(self):
        """Test revealing a grid button."""
        root = tk.Tk()
        try:
            button = GridButton(root, grid_index=0)
            button.reveal()
            assert button.is_revealed
            assert button.cget("state") == tk.DISABLED
        finally:
            root.destroy()


class TestTimerWidget:
    """Test TimerWidget."""
    
    def test_timer_creation(self):
        """Test creating timer widget."""
        root = tk.Tk()
        try:
            timer = TimerWidget(root)
            assert timer.label is not None
        finally:
            root.destroy()
    
    def test_timer_update(self):
        """Test updating timer display."""
        root = tk.Tk()
        try:
            timer = TimerWidget(root)
            timer.update_time(150)  # 2:30
            assert timer.label.cget("text") == "02:30"
        finally:
            root.destroy()
    
    def test_timer_color_green(self):
        """Test timer color when time is plenty."""
        root = tk.Tk()
        try:
            timer = TimerWidget(root)
            timer.update_time(300)  # 5:00
            assert timer.label.cget("fg") == "#00aa00"
        finally:
            root.destroy()
    
    def test_timer_color_orange(self):
        """Test timer color when time is low."""
        root = tk.Tk()
        try:
            timer = TimerWidget(root)
            timer.update_time(90)  # 1:30
            assert timer.label.cget("fg") == "#ffaa00"
        finally:
            root.destroy()
    
    def test_timer_color_red(self):
        """Test timer color when time is critical."""
        root = tk.Tk()
        try:
            timer = TimerWidget(root)
            timer.update_time(30)  # 0:30
            assert timer.label.cget("fg") == "#ff0000"
        finally:
            root.destroy()


class TestScoreDisplay:
    """Test ScoreDisplay widget."""
    
    def test_score_creation(self):
        """Test creating score display."""
        root = tk.Tk()
        try:
            score = ScoreDisplay(root)
            assert score.score_label is not None
        finally:
            root.destroy()
    
    def test_score_update(self):
        """Test updating score display."""
        root = tk.Tk()
        try:
            score = ScoreDisplay(root)
            score.update_score(150)
            assert score.score_label.cget("text") == "150"
        finally:
            root.destroy()


class TestHintDisplay:
    """Test HintDisplay widget."""
    
    def test_hint_creation(self):
        """Test creating hint display."""
        root = tk.Tk()
        try:
            hint = HintDisplay(root, answer_length=10)
            text = hint.hint_label.cget("text")
            assert text.count("_") == 10
        finally:
            root.destroy()
    
    def test_hint_update(self):
        """Test updating hint display."""
        root = tk.Tk()
        try:
            hint = HintDisplay(root, answer_length=10)
            hint.update_display("D_n_ld Tr_mp")
            assert hint.hint_label.cget("text") == "D_n_ld Tr_mp"
        finally:
            root.destroy()


class TestInputField:
    """Test InputField widget."""
    
    def test_input_creation(self):
        """Test creating input field."""
        root = tk.Tk()
        try:
            field = InputField(root)
            assert field.entry is not None
        finally:
            root.destroy()
    
    def test_input_get_text(self):
        """Test getting text from input field."""
        root = tk.Tk()
        try:
            field = InputField(root)
            field.entry.insert(0, "Test Answer")
            assert field.get_text() == "Test Answer"
        finally:
            root.destroy()
    
    def test_input_clear(self):
        """Test clearing input field."""
        root = tk.Tk()
        try:
            field = InputField(root)
            field.entry.insert(0, "Test")
            field.clear()
            assert field.get_text() == ""
        finally:
            root.destroy()


class TestPuzzleGrid:
    """Test PuzzleGrid widget."""
    
    def test_grid_creation(self):
        """Test creating puzzle grid."""
        root = tk.Tk()
        try:
            grid = PuzzleGrid(root)
            assert len(grid.cells) == 16
        finally:
            root.destroy()
    
    def test_grid_cell_reveal(self):
        """Test revealing grid cell."""
        root = tk.Tk()
        try:
            grid = PuzzleGrid(root)
            grid.reveal_cell(5)
            assert grid.cells[5].is_revealed
        finally:
            root.destroy()
    
    def test_grid_revealed_count(self):
        """Test counting revealed cells."""
        root = tk.Tk()
        try:
            grid = PuzzleGrid(root)
            grid.reveal_cell(0)
            grid.reveal_cell(1)
            assert grid.get_revealed_count() == 2
        finally:
            root.destroy()
    
    def test_grid_cell_click(self):
        """Test grid cell click callback."""
        root = tk.Tk()
        callback = Mock()
        try:
            grid = PuzzleGrid(root, on_cell_click=callback)
            grid._handle_click(5)
            callback.assert_called_once_with(5)
        finally:
            root.destroy()


class TestTheme:
    """Test theme constants."""
    
    def test_colors_exist(self):
        """Test that required colors are defined."""
        required = [
            "bg_primary", "bg_secondary", "fg_primary",
            "accent", "success", "warning", "danger"
        ]
        for color in required:
            assert color in COLORS
            assert isinstance(COLORS[color], str)
            assert COLORS[color].startswith("#")
    
    def test_fonts_exist(self):
        """Test that required fonts are defined."""
        required = ["title", "heading", "body", "small", "mono"]
        for font in required:
            assert font in FONTS
            assert isinstance(FONTS[font], tuple)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
