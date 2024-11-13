import logging
from pathlib import Path

from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import QSize, Qt, QThreadPool, pyqtSignal, QModelIndex, QDir

from .book import TheBook
from .node import TreeNode


class BookModel(QStandardItemModel):
    log = logging.getLogger('BookModel')

    def __init__(self, parent=None):
        super().__init__(parent)
        self._path = None
        self._book_node = None
        self.setHorizontalHeaderLabels(["Key", "Value"])

    def setRootPath(self, path: str | Path):  # Takes str or Path
        path = Path(path) if isinstance(path, str) else path  # Ensure Path object
        if not path.exists() or not path.is_dir():
            self.log.error(f"Invalid path: '{path}' - must be an existing directory.")
            return
        self._path = path
        self._book_node = TheBook.load_from_directory(self._path)
        self.log.debug(f"Book root set to '{self._path}'")
        self.populate_model()

    def create_new_book(self, directory: str):
        new_book = TheBook(directory=directory)
        new_book.save_to_directory()
        self._book_node = new_book
        self.log.info(f"Created new book at: {directory}")

    def populate_model(self):
        self.clear()
        if self._path:  # Check for root before populating
            self._populate_from_node(self.invisibleRootItem(), self._book_node)

    def _populate_from_node(self, parent_item, node: TreeNode):
        self.log.debug(f"Populating from node: {node}")

        for child_name, child_node in node.children.items():
            item = QStandardItem(child_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            # HERE!
            if isinstance(child_node, TheBook):
                item.setData("Book", Qt.ItemDataRole.ToolTipRole)
                item.setIcon(QIcon("book_icon.png"))  # Replace with your icon path
            else:  # Generic TreeNode or other subclasses
                item.setData(child_node.node_type(), Qt.ItemDataRole.ToolTipRole)

            self._populate_from_node(item, child_node)  # Recursion on children
            parent_item.appendRow(item)  # Add child after recursive call

        for filename, is_dir in node.get_other_files_and_dirs():
            item = QStandardItem(filename)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            item.setData("File" if not is_dir else "Directory", Qt.ItemDataRole.ToolTipRole)
            parent_item.appendRow(item)

    def save_book(self):
        if self._tree.root and isinstance(self._tree.root, TheBook):  # Ensure root is TheBook instance
            self._tree.root.save_to_directory()