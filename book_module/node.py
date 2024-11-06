import logging
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field, fields
import pickle


@dataclass(kw_only=True)
class Node:
    type: str = 'Node'
    created: datetime = field(default_factory=datetime.now)
    last_save: datetime = field(default_factory=datetime.now)
    store_file: Path = "node.json"

    def to_dict(self):
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Path):  # Handle Path objects
                data[key] = str(value)  # Convert to string
        return data

    def save(self, directory: Path):
        self.last_save = datetime.now()
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / self.store_file
        with open(filepath, "w", encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

    @classmethod
    def load(cls, filepath: Path):
        if filepath.exists():
            try:
                with open(filepath, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    field_names = {f.name for f in fields(cls)}
                    init_data = {k: v for k, v in data.items() if k in field_names}

                    # Convert ISO format strings back to datetime objects:
                    for key, value in init_data.items():  # Iterate and update in place
                        try:  # Important: Use a try-except here
                            init_data[key] = datetime.fromisoformat(value)
                            logging.info(f"[{key}] converted from [{value}]")
                        except ValueError:  # Handle cases where the value is not a valid datetime string
                            logging.debug(f"[{key}[ loaded as is [{value}]")
                            pass  # Or log a warning or raise an exception if needed
                logging.info(f"Successfully loaded {str(cls)} object from file [{str(filepath)}]")
                return cls(**init_data)
            except:
                return None
        else:
            logging.error(f"Object {str(cls)} can't be loaded course of missing file [{str(filepath)}]")
            return None
