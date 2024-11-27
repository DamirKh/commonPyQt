import os
import sys
import subprocess
from pathlib import Path
import logging

from PyQt6.QtCore import QDir, Qt, QModelIndex
from PyQt6.QtGui import QStandardItem, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QCheckBox,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QSizePolicy,
    QLineEdit,
    QMessageBox,
    QDialog,
    QMainWindow, QInputDialog,
)

from tools import get_user_data_path
from ui.MainWindow import Ui_MainWindow
import resources
from book_module.book import TheBook
from book_module.book_model import BookModel
from book_module.node import DATA_JSON as book_file_name, TreeNode
from book_module.node import BaseIntNode
import version

# import PySide6

BASE_DIR = Path(os.path.dirname(__file__))
ICON_DIR = BASE_DIR / 'user_icons'


class MainWindow(QMainWindow, Ui_MainWindow):
    log = logging.getLogger('MainWindow')

    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.book = None

    def connectSignalsSlots(self):
        self.actionOpen_settings_directory.triggered.connect(self.open_settings_folder)
        self.actionOpen_book.triggered.connect(self.open_book)
        self.actionNew_book.triggered.connect(self.new_book)

        self.actionAbout.triggered.connect(self.about)
        self.actionAbout_Qt.triggered.connect(self.about_pyqt)

        self.actionAdd_Node.triggered.connect(self.add_node)
        self.actionNew_Subitem.triggered.connect(self.add_subfolder)

    def on_selection_changed(self, selected, deselected):
        if selected:
            self.log.debug(f"  Selected: {selected}")
            # self.log.debug(f"Type of selected node: {str(parent_node)}")
            # self.log.debug(f"Type of selected item: {str(parent_item)}")
        if deselected:
            self.log.debug(f"Deselected: {deselected}")

    def add_subfolder(self):
        self.log.debug("Hit 'New Subitem'")

        selected_indexes = self.treeView.selectionModel().selectedIndexes()
        if not selected_indexes:
            self.log.info("No item selected. Adding new subfolder to root.")
            parent_node = self.book
            parent_path = self.book.directory  # Use book's directory as parent path
        else:
            parent_index = selected_indexes[0]
            parent_item = self.book_model.itemFromIndex(parent_index)
            parent_node = parent_item.data(Qt.ItemDataRole.UserRole)
            parent_path = parent_node if isinstance(parent_node, Path) else parent_node.directory

        if parent_path is None:  # Check if the parent path is valid.
            self.log.error("Parent path is None. Cannot add subfolder.")
            QMessageBox.critical(self, "Error", "Cannot add subfolder: Parent path is invalid.")
            return

        name, ok = QInputDialog.getText(self, "New Subfolder", "Enter subfolder name:")
        if ok and name:
            new_folder_path = parent_path / name
            try:
                new_folder_path.mkdir(exist_ok=False)  # exist_ok should be False to catch duplication
                self.log.info(f"Created subfolder: {new_folder_path}")

                # if isinstance(parent_node, TreeNode):  # save ordering for TreeNode objects
                #     parent_node.save_directory_info()
                # else:  # Save ordering for Path objects
                #     save_directory_info(parent_path)

                self.book_model.populate_model()  # update view
            except FileExistsError:
                QMessageBox.warning(self, "Error", f"Folder '{name}' already exists.")
            except OSError as e:  # catch file system errors
                QMessageBox.critical(self, "Error", f"Could not create folder: {e}")
        else:
            self.log.debug("New subfolder canceled.")

    def setup_book_browser(self):  # New method to set up the file browser
        self.book_model = BookModel(icons_path=ICON_DIR.absolute())
        self.book_model.setRootPath(self.book.directory)

        self.treeView.setModel(self.book_model)
        self.selection_model = self.treeView.selectionModel()
        self.selection_model.selectionChanged.connect(self.on_selection_changed)

        self.treeView.expanded.connect(self.on_item_expanded)
        self.treeView.collapsed.connect(self.on_item_collapsed)

        self.actionAdd_Item.setEnabled(True)
        self.actionNew_Subitem.setEnabled(True)
        self.actionAdd_Node.setEnabled(True)

    def on_item_expanded(self, index: QModelIndex):
        item = self.book_model.itemFromIndex(index)
        self.update_item_icon(item, expanded=True)

    def on_item_collapsed(self, index: QModelIndex):
        item = self.book_model.itemFromIndex(index)
        self.update_item_icon(item, expanded=False)

    def update_item_icon(self, item: QStandardItem, expanded: bool):
        if item is None:  # Check for valid item
            return

        node_or_path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(node_or_path, Path) and node_or_path.is_dir(): # Check if dir
            icon_name = "folder-horizontal-open.png" if expanded else "folder-horizontal.png"  # Use your desired names
            icon_path = self.book_model._icons_path / icon_name
            if icon_path.exists(): # Check if icon file exists
                item.setIcon(QIcon(str(icon_path)))

    def new_book(self):
        self.log.debug(f"Hit 'New book'")

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)  # Set to select directories
        # dialog.setOption(QFileDialog.Option.ReadOnly)  # Set ReadOnly option
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)  # Show only dirs

        if dialog.exec():  # Use exec() instead of exec_() in PyQt6
            folder_path = dialog.selectedFiles()[0]  # Get the selected path
            self.log.debug(f"Selected folder: {folder_path}")

            book_path = Path(folder_path)
            self.book = TheBook(directory=book_path)
            self.book.save_to_directory()  # Correct saving
            self.setup_book_browser()

        else:
            self.log.debug("New book canceled.")

    def open_book(self):
        self.log.debug(f"Hit 'Open book'")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter(f"Book Data ({book_file_name})")  # Filter for the exact filename

        default_book_dir = get_user_data_path() / "Books"
        if default_book_dir.exists():
            dialog.setDirectory(str(default_book_dir))

        if dialog.exec():
            selected_file = dialog.selectedFiles()[0]
            if selected_file:
                try:
                    book_path = Path(selected_file).parent
                    book = TheBook.load_from_directory(book_path)
                    if not book.node_type() == 'TheBook':
                        raise TypeError(f"Incorrect Book object in file {selected_file}\nTry to select parent folder")
                    else:
                        self.book = book
                    self.log.debug(f"Opened book: {self.book}")
                    self.setup_book_browser()
                # except (AttributeError, FileNotFoundError) as e:
                except (TypeError, AttributeError, FileNotFoundError) as e:
                    self.log.error(f"Error loading book: {e}")
                    QMessageBox.critical(self, "Error", f"Could not load book: {e}")
            else:
                self.log.debug("No book file selected.")
        else:
            self.log.debug("Open book canceled.")

    def add_node(self):
        self.log.debug(f"Hit 'Add Node'")
        # Get the selected item (parent node)
        selected_indexes = self.treeView.selectionModel().selectedIndexes()
        if not selected_indexes:
            self.log.info("No item selected. Add new node to root.")
            parent_node = self.book
            parent_path = self.book.directory
            parent_item = self.book_model.invisibleRootItem()
        else:
            parent_index = selected_indexes[0]  # Get the first selected item
            parent_item = self.book_model.itemFromIndex(parent_index)
            parent_node = parent_item.data(Qt.ItemDataRole.UserRole)  # TreeNode or Path was stored as data
            parent_path = parent_node if isinstance(parent_node, Path) else parent_node.directory

        # Get node name/value using QInputDialog:
        name, ok = QInputDialog.getText(self, "Add Node", "Enter node name:")
        if not ok or not name:
            return  # User cancelled or entered empty name
        # here we shoud check if entered name already exist

        if (parent_path / name).exists(): # Check for already existing file or directory with the same name
            QMessageBox.warning(self, "Error", f"Item with name '{name}' already exists in this directory.")
            return

        value, ok_pressed = QInputDialog.getInt(
            self, "Get integer", "Value:", 0, 0, 100, 1)
        if ok_pressed:
            # print(value) # Check if value = number
            new_node = BaseIntNode(value=value)  # Initialize with 0 or a default value
        else:
            return # User cancelled


        if issubclass(type(parent_node), TreeNode):
            self.log.info("Selected item represents a TreeNode subclass.")
            try:
                parent_node.add_child(new_node, dir_name=name)
            except (TypeError, ValueError) as e:
                self.log.error(f"Error adding new node: {e}")
                QMessageBox.critical(self, "Error", f"Could not create new node: {e}")
                return
        else:  # Handle case where the data is a Path (regular directory)
            try:
                new_node_dir = parent_node / name
                new_node.save_to_directory(new_node_dir)
            except Exception as e:  # Catch potential saving errors
                self.log.error(f"Error saving new node to directory: {e}")
                QMessageBox.critical(self, "Error", str(e))
                return
        self.book_model._populate_from_node(parent_item, new_node)
        # self.book_model.populate_model()  # Refresh the view

    def open_settings_folder(self):
        directory_path: Path = get_user_data_path()
        # print(f"Opening folder {directory_path}")
        if sys.platform == "win32":
            os.startfile(directory_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", directory_path])
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", directory_path])
        else:
            QMessageBox.warning(self, "Error", f"Unsupported platform: {sys.platform}")

    def about(self):
        QMessageBox.about(
            self,
            "About Qt Skeleton ",
            f"<p>By using this Skeleton, </p>"
            f"<p>you can significantly improve the quality, reliability, and development speed of your Qt programs</p>"
            f"<p> - PyQt6</p>"
            f"<p> - Qt Designer6</p>"
            f"<p> - Python3.12</p>"
            f"System: {os.name}"
        )

    def about_pyqt(self):
        QMessageBox.aboutQt(self)


if __name__ == '__main__':
    # Get the data path
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    log.info(f"Start application '{version.app_name}' {version.rev}")
    data_path = get_user_data_path()

    # Create the directory if it doesn't exist
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle(version.app_name)
    window.show()
    sys.exit(app.exec())
