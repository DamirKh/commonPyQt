import logging
from pathlib import Path

from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import QSize, Qt, QThreadPool, pyqtSignal, QModelIndex, QDir

from .book import TheBook
from .node import TreeNode, DATA_JSON


BAD_NODE = 'exclamation-red.png'

class BookModel(QStandardItemModel):
    log = logging.getLogger('BookModel')

    def __init__(self, parent=None, icons_path: Path = None):
        super().__init__(parent)
        self._path = None
        self._icons_path = icons_path
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
        self.setHorizontalHeaderLabels(["Key", "Value"])
        if self._path:  # Check for root before populating
            self._populate_from_node(self.invisibleRootItem(), self._book_node)

    def _populate_from_node(self, parent_item, node: TreeNode | Path):
        path = node if isinstance(node, Path) else node.directory

        if path is None:
            self.log.warning("Path is None. Cannot populate.")
            return

        self.log.debug(f"Populating from path: {path}")

        qdir = QDir(str(path))

        if isinstance(node, TreeNode):
            for child_name, child_node in node.children.items():
                item = QStandardItem(child_name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

                try:
                    icon_name = child_node._icon
                    item.setIcon(QIcon(str(self._icons_path/icon_name)))
                except AttributeError:
                    pass
                    # item.setIcon(QIcon("default_icon.png"))  # Or handle differently

                self._populate_from_node(item, child_node)
                parent_item.appendRow(item)

        # Process "other" files and directories
        for entry in qdir.entryInfoList(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot):
            if entry.isDir():
                entry_path = path / entry.fileName()

                if (entry_path / DATA_JSON).exists():
                    try:
                        child_node = TreeNode.load_from_directory(str(entry_path))
                        if child_node:
                            item = QStandardItem(entry.fileName())
                            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

                            try:  # try to get icon, handle exception for missing field
                                icon_name = child_node._icon
                                item.setIcon(QIcon(str(self._icons_path/icon_name)))
                            except AttributeError:
                                pass
                                # item.setIcon(QIcon("default_icon.png"))  # Or handle differently

                            item.setData(child_node.node_type(), Qt.ItemDataRole.ToolTipRole)
                            self._populate_from_node(item, child_node)
                            parent_item.appendRow(item)
                            continue  # Skip adding as regular directory
                    except Exception as e:
                        self.log.error(f"Error loading TreeNode from {entry_path}: {e}")
                        item = QStandardItem(entry.fileName())
                        item.setIcon(QIcon(str(self._icons_path / BAD_NODE)))

                # If not a TreeNode directory or loading failed, add as a regular directory
                item = QStandardItem(entry.fileName())
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                item.setData("Directory", Qt.ItemDataRole.ToolTipRole)
                self._populate_from_node(item, entry_path)  # recurse for other files in this dir
                parent_item.appendRow(item)

            elif entry.isFile() and str(entry.filePath()) != str(path / DATA_JSON):
                item = QStandardItem(entry.fileName())
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                item.setData("File", Qt.ItemDataRole.ToolTipRole)
                parent_item.appendRow(item)

    def save_book(self):
        if self._book_node:  # Ensure root is TheBook instance
            self._book_node.save_to_directory()
