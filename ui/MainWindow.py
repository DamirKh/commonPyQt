# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(714, 444)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/irt.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(parent=self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(5)
        self.splitter.setObjectName("splitter")
        self.treeView = QtWidgets.QTreeView(parent=self.splitter)
        self.treeView.setObjectName("treeView")
        self.textEdit = QtWidgets.QTextEdit(parent=self.splitter)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 714, 19))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuTree = QtWidgets.QMenu(parent=self.menubar)
        self.menuTree.setObjectName("menuTree")
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(parent=MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.actionAdd_Item = QtGui.QAction(parent=MainWindow)
        self.actionAdd_Item.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionAdd_Item.setIcon(icon1)
        self.actionAdd_Item.setObjectName("actionAdd_Item")
        self.actionNew_Subitem = QtGui.QAction(parent=MainWindow)
        self.actionNew_Subitem.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/arrow-branch-270-left.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionNew_Subitem.setIcon(icon2)
        self.actionNew_Subitem.setObjectName("actionNew_Subitem")
        self.actionAdd_Node = QtGui.QAction(parent=MainWindow)
        self.actionAdd_Node.setEnabled(False)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/icons/leaf--plus.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionAdd_Node.setIcon(icon3)
        self.actionAdd_Node.setObjectName("actionAdd_Node")
        self.actionOpen_settings_directory = QtGui.QAction(parent=MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/icons/folder-horizontal-open.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionOpen_settings_directory.setIcon(icon4)
        self.actionOpen_settings_directory.setObjectName("actionOpen_settings_directory")
        self.actionOpen_book = QtGui.QAction(parent=MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/icons/book-open.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionOpen_book.setIcon(icon5)
        self.actionOpen_book.setObjectName("actionOpen_book")
        self.actionClose_book = QtGui.QAction(parent=MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/icons/book--pencil.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionClose_book.setIcon(icon6)
        self.actionClose_book.setObjectName("actionClose_book")
        self.actionAbout = QtGui.QAction(parent=MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/icons/information.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionAbout.setIcon(icon7)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout_Qt = QtGui.QAction(parent=MainWindow)
        icon = QtGui.QIcon.fromTheme("help-about")
        self.actionAbout_Qt.setIcon(icon)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.actionNew_book = QtGui.QAction(parent=MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/icons/book--plus.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionNew_book.setIcon(icon8)
        self.actionNew_book.setObjectName("actionNew_book")
        self.menuFile.addAction(self.actionOpen_book)
        self.menuFile.addAction(self.actionClose_book)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionNew_book)
        self.menuTree.addAction(self.actionAdd_Item)
        self.menuTree.addAction(self.actionNew_Subitem)
        self.menuTree.addAction(self.actionAdd_Node)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionOpen_settings_directory)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTree.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionAdd_Item)
        self.toolBar.addAction(self.actionNew_Subitem)
        self.toolBar.addAction(self.actionAdd_Node)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuTree.setTitle(_translate("MainWindow", "Tree"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionAdd_Item.setText(_translate("MainWindow", "New Item"))
        self.actionNew_Subitem.setText(_translate("MainWindow", "New Subitem"))
        self.actionAdd_Node.setText(_translate("MainWindow", "Add Node"))
        self.actionAdd_Node.setToolTip(_translate("MainWindow", "Add Node"))
        self.actionOpen_settings_directory.setText(_translate("MainWindow", "Open app settings directory"))
        self.actionOpen_settings_directory.setToolTip(_translate("MainWindow", "Open setings directory"))
        self.actionOpen_book.setText(_translate("MainWindow", "Open book..."))
        self.actionClose_book.setText(_translate("MainWindow", "Close book"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionAbout_Qt.setText(_translate("MainWindow", "About Qt"))
        self.actionNew_book.setText(_translate("MainWindow", "New book..."))
