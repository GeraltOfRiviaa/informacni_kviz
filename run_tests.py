#!/usr/bin/env python3
"""
Test runner script - spustí testy a vrátí report.
"""

import subprocess
import sys

def main():
    """Run all tests and report results."""
    print("=" * 80)
    print("SPOUŠTĚNÍ TESTŮ - Interaktivní Soutěžní Aplikace")
    print("=" * 80)
    
    # Run pytest on all tests
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd="."
    )
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
