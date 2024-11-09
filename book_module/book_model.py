import logging
from pathlib import Path

from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import QSize, Qt, QThreadPool, pyqtSignal, QModelIndex, QDir

from .node import Node
from .book import TheBook

class BookModel(QStandardItemModel):
    log = logging.getLogger('BookModel')
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        # self.test_populate_model()
        self._root = None  # Initialize _root


    def setRootPath(self, path: Path):
        if not isinstance(path, Path):
            path = Path(path)
        if not path.exists() or not path.is_dir():
            self.log.error(f"Invalid path: '{str(path)}' - must be an existing directory.")
            return  # Or raise an exception

        self.log.debug(f"Book root set to '{str(path)}'")
        self._root = path
        self.populate_model()  # Populate after setting the root


    def populate_model(self):
        if self._root is None:
            self.log.warning("Root path not set. Cannot populate model.")
            return

        self.clear()  # Clear existing items

        self._populate_from_path(self.invisibleRootItem(), self._root)

    def _populate_from_path(self, parent_item, path: Path):
        self.log.debug(f"Populating: {path.absolute()}")

        for entry in QDir(str(path)).entryInfoList(
                QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot):  # Filters out "." and ".."
            if entry.isFile() or entry.isDir():  # Explicitly check if it's a file or directory
                item_name = entry.fileName()
                item = QStandardItem(item_name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

                if entry.isDir():
                    book = TheBook.load(path / item_name)  # Try to load

                    if book:  # Check if it's a Book directory
                        item.setData("Book", Qt.ItemDataRole.ToolTipRole)
                        item.setIcon(
                            QIcon("book_icon.png"))  # Set the book icon – replace with your actual icon path!
                        # You can also add other Book details to the model here if needed:
                        # item.appendRow(QStandardItem(f"Title: {book.title}"))
                        # item.appendRow(QStandardItem(f"Author: {book.author}"))
                    else:
                        item.setData("Directory", Qt.ItemDataRole.ToolTipRole)

                    self._populate_from_path(item, path / item_name)  # Recursion
                    self.log.debug(f"Added directory: {item_name}")  # Log added directory
                else:
                    item.setData("File", Qt.ItemDataRole.ToolTipRole)
                    # item.setData(entry.size(), Qt.ItemDataRole.SizeHintRole)
                    self.log.debug(f"add item '{entry.fileName()}'")

                parent_item.appendRow(item)

    # def _populate_from_path(self, parent_item, path: Path):
    #     self.log.debug(f"Add subdir '{str(path)}'")
    #     for entry in QDir(str(path)).entryInfoList(
    #             QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot):  # Use QDir for better handling of hidden files and system entries
    #         item = QStandardItem(entry.fileName())
    #         item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
    #
    #         if entry.isDir():
    #             item.setData("Directory", Qt.ItemDataRole.ToolTipRole)
    #             self._populate_from_path(item, path / entry.fileName())  # Recursively populate subdirectories
    #         else:
    #             item.setData("File", Qt.ItemDataRole.ToolTipRole)
    #             # item.setData(entry.size(), Qt.ItemDataRole.SizeHintRole)
    #             self.log.debug(f"add item '{entry.fileName()}'")
    #
    #         parent_item.appendRow(item)
