"""
Theme settings for Tkinter GUI.
Color schemes (modern), fonts, constants.

Modern color palette inspired by contemporary design:
- Clean, minimalist aesthetic
- Gradient-friendly colors
- Good contrast for accessibility
- Professional appearance
"""

# Modern Color Palette
# Inspired by: Material Design 3, macOS design language, Tailwind CSS
COLORS = {
    "bg_primary": "#0b1324",      # Main background
    "bg_secondary": "#16213a",    # Card/top bar background
    "bg_tertiary": "#223458",     # Surface background
    "fg_primary": "#f1f5f9",      # Main text
    "fg_secondary": "#a9b7d0",    # Secondary text
    "accent": "#38bdf8",          # Cyan accent
    "accent_hover": "#0ea5e9",    # Accent hover
    "success": "#22c55e",         # Green success
    "success_hover": "#16a34a",   # Success hover
    "warning": "#f59e0b",         # Amber warning
    "warning_hover": "#d97706",   # Warning hover
    "danger": "#ef4444",          # Red danger
    "danger_hover": "#dc2626",    # Danger hover
    "cell_hidden": "#1f2937",     # Hidden overlay cells
    "cell_revealed": "#0b1324",   # Revealed cell tint
    "border": "#334155",          # Border color
    "gradient_start": "#0b1324",  # Gradient start
    "gradient_end": "#121f37",    # Gradient end
}

# Modern Fonts
FONTS = {
    "title": ("Bahnschrift", 30, "bold"),
    "heading": ("Bahnschrift", 16, "bold"),
    "body": ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "mono": ("Consolas", 10),
    "timer": ("Bahnschrift", 24, "bold"),
    "score": ("Bahnschrift", 17, "bold"),
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

# Border radius (for rounded corners, pseudocode)
# Tkinter doesn't support native rounded corners, but we can use images or other workarounds
BORDER_RADIUS = 8  # pixels (for reference)

# Shadows (simulated with colors)
SHADOW_COLOR = "#00000020"  # Semi-transparent black
