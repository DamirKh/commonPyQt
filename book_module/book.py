import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class TheBook:
    path: Path
    created: datetime = field(default_factory=datetime.now)
    last_save: datetime = field(default_factory=datetime.now)
    name: str = field(init=False)
    # ... other attributes
    log: logging.Logger = field(init=False)  # Add logger as a field

    def __post_init__(self):
        self.name = self.path.name
        self.log = logging.getLogger(f"TheBook({self.name})")  # Initialize logger
        self.load()

    def save(self):
        self.last_save = datetime.now()  # Update last_save before saving
        data_file = self.path / "book_data.pickle"  # Use .pickle extension
        try:
            with open(data_file, "wb") as f:  # "wb" for binary write
                pickle.dump(self, f)  # Pickle the entire object
            self.log.debug(f"Saved book data to {data_file}")
        except OSError as e:
            self.log.error(f"Error saving book data: {e}")
            raise e

    def load(self):
        data_file = self.path / "book_data.pickle"
        if data_file.exists():
            try:
                with open(data_file, "rb") as f:  # "rb" for binary read
                    loaded_book = pickle.load(f)  # Unpickle
                    # Update attributes (important for dataclasses)
                    for key, value in loaded_book.__dict__.items():
                        if hasattr(self, key):
                            setattr(self, key, value)

                self.log.debug(f"Loaded book data from {data_file}")

            except (OSError, pickle.UnpicklingError, AttributeError) as e:
                self.log.warning(f"Error loading book data: {e}")
                raise e