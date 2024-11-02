import os
import pickle
import sys
import subprocess
from pathlib import Path
import logging

from PyQt6.QtCore import QDir
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
    QMainWindow,
)

from PyQt6.QtGui import QFileSystemModel
# from PyQt6.QtGui import QIcon
# from PyQt6.QtCore import QSize, Qt, QThreadPool

from tools import get_user_data_path
from ui.MainWindow import Ui_MainWindow
import resources
from book_module.book import TheBook
from book_module.book_model import BookModel
import version
# import PySide6


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

    def setup_book_browser(self):  # New method to set up the file browser
        self.book_model = BookModel()
        self.book_model.setRootPath(self.book.path)

        self.treeView.setModel(self.book_model)
        # self.treeView.setRootIndex(self.book.path)

    def new_book(self):
        self.log.debug(f"Hit 'New book'")

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)  # Set to select directories
        # dialog.setOption(QFileDialog.Option.ReadOnly)  # Set ReadOnly option
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)  # Show only dirs


        if dialog.exec():  # Use exec() instead of exec_() in PyQt6
            folder_path = dialog.selectedFiles()[0]  # Get the selected path
            self.log.debug(f"Selected folder: {folder_path}")
            self.book = TheBook(Path(folder_path))
            self.book.save()
            pass
            # Now you can process the selected folder path
            # ... (e.g., load book_module data, etc.) ...
        else:
            self.log.debug("New book canceled.")

    def open_book(self):
        self.log.debug(f"Hit 'Open book'")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Book Data (book_data.pickle)")  # Filter for the exact filename

        default_book_dir = get_user_data_path() / "Books"
        if default_book_dir.exists():
            dialog.setDirectory(str(default_book_dir))

        if dialog.exec():
            selected_file = dialog.selectedFiles()[0]
            if selected_file:
                try:
                    book_path = Path(selected_file).parent
                    if (book_path / "book_data.pickle").exists():  # redundant check
                        self.book = TheBook(book_path)
                        self.log.debug(f"Opened book: {self.book.name}")
                        self.setup_book_browser()
                    else:
                        raise FileNotFoundError("book_data.pickle not found")  # Raise exception to trigger except block

                except (TypeError, pickle.UnpicklingError, AttributeError, FileNotFoundError) as e:
                    self.log.error(f"Error loading book: {e}")
                    QMessageBox.critical(self, "Error", f"Could not load book: {e}")
            else:
                self.log.debug("No book file selected.")

        else:
            self.log.debug("Open book canceled.")


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
