import sys
import os
from pathlib import Path


def get_data_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "data"
    else:
        return Path(__file__).parent.parent / "data"


def get_progress_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    else:
        base = Path.home() / ".config"
    progress_dir = base / "ROCAStudyApp"
    progress_dir.mkdir(parents=True, exist_ok=True)
    return progress_dir


def get_progress_file() -> Path:
    return get_progress_dir() / "progress.json"
