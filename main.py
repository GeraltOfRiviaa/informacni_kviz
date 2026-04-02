#!/usr/bin/env python3
"""
main.py - Entry point for the Interactive Quiz Application.

Run the Tkinter GUI version of the application.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from gui import main as run_gui


if __name__ == "__main__":
    run_gui()
