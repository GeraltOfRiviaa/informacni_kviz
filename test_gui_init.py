#!/usr/bin/env python3
"""Test script for GUI initialization."""

import sys
import traceback

print("=" * 60)
print("GUI INITIALIZATION TEST")
print("=" * 60)

try:
    print("\n[1/3] Importing tkinter...")
    import tkinter as tk
    print("✓ tkinter imported successfully")
    
    print("\n[2/3] Importing QuizApplication from gui module...")
    from gui import QuizApplication
    print("✓ QuizApplication imported successfully")
    
    print("\n[3/3] Initializing GUI...")
    root = tk.Tk()
    app = QuizApplication(root)
    print("✓ GUI initialized successfully")
    
    print("\n" + "=" * 60)
    print("RESULT: ✓ All modules loaded correctly")
    print("=" * 60)
    
    root.destroy()
    sys.exit(0)
    
except ImportError as e:
    print(f"\n✗ IMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n✗ INITIALIZATION ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
