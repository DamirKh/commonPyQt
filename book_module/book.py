import logging
log = logging.getLogger("book")

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
    node_files = list()

    def save(self):  # Override save to use self.path
        super().save(self.path)

    def register_node_type(self, node_type):
        if issubclass(node_type, node.Node):
            log.info(f"Register node type {str(node_type)}...")
            self.node_files.append(node_type.store_file)
        else:
            log.error(f"Type {str(node_type)} can't be registered")


    @classmethod
    def load(cls, path: Path):  # Override load method
        filepath = path / book_file_name  # Pass filename as string
        return super().load(filepath)  # Use the overridden load method