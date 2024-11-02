import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
import pickle

@dataclass
class Chapter:
    type: str = 'Ordinary chapter'
    created: datetime = field(default_factory=datetime.now)
    last_save: datetime = field(default_factory=datetime.now)

    def save_to_directory(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / "chapter.pickle", "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load_from_directory(cls, directory: Path):
        if (directory / "chapter.pickle").exists():
            try:
                with open(directory / "chapter.pickle", "rb") as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, EOFError, FileNotFoundError) as e:
                logging.error(f"Error loading chapter from {directory}: {e}")
                return None  # Or handle the error differently
        return None
