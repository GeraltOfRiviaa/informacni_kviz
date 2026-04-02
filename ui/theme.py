"""
Theme settings for Tkinter GUI.
Color schemes, fonts, constants.
"""

# Colors
COLORS = {
    "bg_primary": "#1e1e1e",      # Dark background
    "bg_secondary": "#2d2d2d",    # Slightly lighter
    "bg_tertiary": "#3d3d3d",     # Even lighter
    "fg_primary": "#ffffff",      # White text
    "fg_secondary": "#e0e0e0",    # Light gray text
    "accent": "#0078d4",          # Blue accent
    "success": "#107c10",         # Green (correct answer)
    "warning": "#ffb900",         # Yellow (hint)
    "danger": "#e81123",          # Red (wrong)
    "cell_hidden": "#505050",     # Gray (hidden cell)
    "cell_revealed": "#2d2d2d",   # Dark (revealed cell)
}

# Fonts
FONTS = {
    "title": ("Arial", 24, "bold"),
    "heading": ("Arial", 16, "bold"),
    "body": ("Arial", 12),
    "small": ("Arial", 10),
    "mono": ("Courier", 10),
    "timer": ("Arial", 20, "bold"),
    "score": ("Arial", 14, "bold"),
}

# Dimensions
GRID_SIZE = 4
CELL_SIZE = 80  # pixels
CELL_PADDING = 5
GRID_WIDTH = GRID_SIZE * (CELL_SIZE + CELL_PADDING) + CELL_PADDING
GRID_HEIGHT = GRID_SIZE * (CELL_SIZE + CELL_PADDING) + CELL_PADDING

# Window dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
PADDING = 20

# Button sizing
BUTTON_WIDTH = 10
BUTTON_HEIGHT = 2

# Animation
ANIMATION_DURATION = 200  # ms
