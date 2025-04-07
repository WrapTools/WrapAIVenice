# /handlers/base_handlers.py

from pathlib import Path

def register():
    return {
        ".txt": lambda path: path.read_text(encoding="utf-8").strip()
    }
