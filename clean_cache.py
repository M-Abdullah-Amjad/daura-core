#!/usr/bin/env python3
"""
Clean up Python cache files and directories.
Run this script to remove __pycache__ directories and .pyc files.
"""

import os
import shutil
import sys
from pathlib import Path


def clean_pycache(root_dir: str = ".") -> None:
    """Remove all __pycache__ directories and .pyc files."""
    root_path = Path(root_dir)

    # Remove __pycache__ directories
    pycache_dirs = list(root_path.rglob("__pycache__"))
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"Removed: {pycache_dir}")
        except Exception as e:
            print(f"Error removing {pycache_dir}: {e}")

    # Remove .pyc files
    pyc_files = list(root_path.rglob("*.pyc"))
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"Removed: {pyc_file}")
        except Exception as e:
            print(f"Error removing {pyc_file}: {e}")

    # Remove .pyo files
    pyo_files = list(root_path.rglob("*.pyo"))
    for pyo_file in pyo_files:
        try:
            pyo_file.unlink()
            print(f"Removed: {pyo_file}")
        except Exception as e:
            print(f"Error removing {pyo_file}: {e}")

    print("Cache cleanup completed!")


if __name__ == "__main__":
    # Default to current directory
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    clean_pycache(root_dir)