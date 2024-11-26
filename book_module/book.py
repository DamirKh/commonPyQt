import logging
from typing import Optional

log = logging.getLogger("TheBook")

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from .node import TreeNode
# log = logging.getLogger(__name__)  # Use __name__ for more informative logging

@TreeNode.register_node_type('TheBook')
@dataclass(kw_only=True)
class TheBook(TreeNode):
    """This class represents the book (Entire project)"""
    Title: str = "Untitled"
    BackCover: str = "User can write any comments here"
    _created: datetime = field(default_factory=datetime.now)
    _last_save: datetime = field(default_factory=datetime.now)
    _icon: str = field(default='book.png')

    def save_to_directory(self, directory: Optional[str] = None):
        self._last_save = datetime.now()
        super().save_to_directory(directory=directory)
        log.info(f"Saved TheBook '{self.Title}' to {self.directory}")  # Log the save event

    def __str__(self) -> str:
        created_str = self._created.strftime("%Y-%m-%d %H:%M:%S")  # Or your preferred format
        last_save_str = self._last_save.strftime("%Y-%m-%d %H:%M:%S")
        return f"The Book: {self.Title} (created {created_str}, saved: {last_save_str})"
