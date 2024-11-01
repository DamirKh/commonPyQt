import os
import sys
import subprocess
from pathlib import Path

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
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt, QThreadPool

from tools import get_user_data_path
from ui.MainWindow import Ui_MainWindow
import resources


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        # self.pushButtonAddTab.clicked.connect(self.onAddTab)
        # self.actionLoad.triggered.connect(self.load_config)
        # self.actionSave.triggered.connect(self.save_config)
        # self.actionRead_Timer.triggered.connect(self.on_read_timer_conf)
        # self.actionEnable_writing_to_PLC.triggered.connect(self.on_write_enable)
        self.actionOpen_settings_directory.triggered.connect(self.open_settings_folder)
        self.actionOpen_project.triggered.connect(self.open_project)
        # self.actionShow_log.triggered.connect(self.show_log)

    def open_project(self):
        pass


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

if __name__ == '__main__':
    # Get the data path
    data_path = get_user_data_path()

    # Create the directory if it doesn't exist
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
