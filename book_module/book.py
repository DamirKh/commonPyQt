from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from . import node

book_file_name = "TheBook.json"

@dataclass(kw_only=True)
class TheBook(node.Node):
    path: Path
    type: str = 'TheBook'
    store_file: str = book_file_name

    def save(self):  # Override save to use self.path
        super().save(self.path)

    @classmethod
    def load(cls, path: Path):  # Override load method
        filepath = path / book_file_name  # Pass filename as string
        return super().load(filepath)  # Use the overridden load method