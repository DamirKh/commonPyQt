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
        self.beginResetModel()
        self.clear()
        self.setHorizontalHeaderLabels(["Key", "Value"])
        if self._path:  # Check for root before populating
            self._populate_from_node(self.invisibleRootItem(), self._book_node)
        self.endResetModel()

    def _create_item(self, name, node, tooltip="", icon_path=None):
        self.log.debug(f"Creating child node <{name}>")
        item = QStandardItem(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable)
        tt = tooltip if tooltip else node.node_type()
        if hasattr(node, "_icon") and self._icons_path and node._icon:
            icon_path = self._icons_path / node._icon
        elif icon_path:
            pass
        item.setIcon(QIcon(str(icon_path)) if icon_path else QIcon())
        item.setData(tt, Qt.ItemDataRole.ToolTipRole)
        # Store the TreeNode as data:
        item.setData(node, Qt.ItemDataRole.UserRole)

        return item

    def _populate_from_node(self, parent_item, node: TreeNode | Path):
        path = node if isinstance(node, Path) else node.directory

        if path is None:
            self.log.warning("Path is None. Cannot populate.")
            return

        self.log.debug(f"Populating from path: {path}")

        qdir = QDir(str(path))

        if isinstance(node, TreeNode):
        # if issubclass(type(node), TreeNode):
            for child_name, child_node in node.children.items():
                item = self._create_item(child_name, child_node)  # node is passed here
                parent_item.appendRow(item)
                self._populate_from_node(item, child_node)

        # Process ONLY files and directories
        for entry in qdir.entryInfoList(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot):
            entry_path = path / entry.fileName()
            if isinstance(node, TreeNode) and entry.fileName() in node.children:
                continue  # Skip TreeNode children – they've already been added

            if entry.isDir():

                if (entry_path / DATA_JSON).exists():
                    try:
                        child_node = TreeNode.load_from_directory(str(entry_path))
                        if child_node:
                            item = self._create_item(entry.fileName(), child_node)  # node is passed here
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
                item.setData(entry_path, Qt.ItemDataRole.UserRole)
                self._populate_from_node(item, entry_path)  # recurse for other files in this dir
                parent_item.appendRow(item)

            elif entry.isFile() and str(entry.filePath()) != str(path / DATA_JSON):
                item = QStandardItem(entry.fileName())
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable)
                item.setData("File", Qt.ItemDataRole.ToolTipRole)
                parent_item.appendRow(item)

    def save_book(self):
        if self._book_node:  # Ensure root is TheBook instance
            self._book_node.save_to_directory()
