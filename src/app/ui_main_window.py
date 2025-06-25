# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowjghtrw.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListView,
    QMainWindow, QMenuBar, QProgressBar, QPushButton,
    QSizePolicy, QStatusBar, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 720)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(300, 10, 311, 41))
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 50, 451, 601))
        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 20, 431, 231))
        self.verticalLayoutWidget = QWidget(self.groupBox_2)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(9, 19, 411, 201))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.file_list_view = QListView(self.verticalLayoutWidget)
        self.file_list_view.setObjectName(u"file_list_view")

        self.verticalLayout.addWidget(self.file_list_view)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.add_files_btn = QPushButton(self.verticalLayoutWidget)
        self.add_files_btn.setObjectName(u"add_files_btn")

        self.horizontalLayout_2.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton(self.verticalLayoutWidget)
        self.add_folder_btn.setObjectName(u"add_folder_btn")

        self.horizontalLayout_2.addWidget(self.add_folder_btn)

        self.remove_file_btn = QPushButton(self.verticalLayoutWidget)
        self.remove_file_btn.setObjectName(u"remove_file_btn")

        self.horizontalLayout_2.addWidget(self.remove_file_btn)

        self.clear_files_btn = QPushButton(self.verticalLayoutWidget)
        self.clear_files_btn.setObjectName(u"clear_files_btn")

        self.horizontalLayout_2.addWidget(self.clear_files_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.groupBox_3 = QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(9, 260, 431, 71))
        self.horizontalLayoutWidget_2 = QWidget(self.groupBox_3)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(9, 20, 411, 31))
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.export_path_edit = QLineEdit(self.horizontalLayoutWidget_2)
        self.export_path_edit.setObjectName(u"export_path_edit")

        self.horizontalLayout_3.addWidget(self.export_path_edit)

        self.browse_export_btn = QPushButton(self.horizontalLayoutWidget_2)
        self.browse_export_btn.setObjectName(u"browse_export_btn")

        self.horizontalLayout_3.addWidget(self.browse_export_btn)

        self.groupBox_4 = QGroupBox(self.groupBox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(10, 340, 431, 131))
        self.verticalLayoutWidget_2 = QWidget(self.groupBox_4)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(19, 19, 401, 100))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.preserve_conn = QCheckBox(self.verticalLayoutWidget_2)
        self.preserve_conn.setObjectName(u"preserve_conn")

        self.verticalLayout_2.addWidget(self.preserve_conn)

        self.preserve_formatting = QCheckBox(self.verticalLayoutWidget_2)
        self.preserve_formatting.setObjectName(u"preserve_formatting")

        self.verticalLayout_2.addWidget(self.preserve_formatting)

        self.create_log = QCheckBox(self.verticalLayoutWidget_2)
        self.create_log.setObjectName(u"create_log")

        self.verticalLayout_2.addWidget(self.create_log)

        self.include_data = QCheckBox(self.verticalLayoutWidget_2)
        self.include_data.setObjectName(u"include_data")

        self.verticalLayout_2.addWidget(self.include_data)

        self.begin_migration_btn = QPushButton(self.groupBox)
        self.begin_migration_btn.setObjectName(u"begin_migration_btn")
        self.begin_migration_btn.setGeometry(QRect(14, 480, 421, 41))
        self.progressBar = QProgressBar(self.groupBox)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(20, 530, 411, 31))
        self.progressBar.setValue(0)
        self.progressBar.setInvertedAppearance(False)
        self.groupBox_5 = QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(470, 50, 411, 601))
        self.groupBox_6 = QGroupBox(self.groupBox_5)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(10, 20, 391, 111))
        self.gridLayoutWidget = QWidget(self.groupBox_6)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 20, 371, 81))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.files_processed = QLabel(self.gridLayoutWidget)
        self.files_processed.setObjectName(u"files_processed")

        self.gridLayout.addWidget(self.files_processed, 0, 3, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.files_queued = QLabel(self.gridLayoutWidget)
        self.files_queued.setObjectName(u"files_queued")

        self.gridLayout.addWidget(self.files_queued, 0, 1, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        self.process_time = QLabel(self.gridLayoutWidget)
        self.process_time.setObjectName(u"process_time")

        self.gridLayout.addWidget(self.process_time, 1, 1, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 1, 2, 1, 1)

        self.failures = QLabel(self.gridLayoutWidget)
        self.failures.setObjectName(u"failures")

        self.gridLayout.addWidget(self.failures, 1, 3, 1, 1)

        self.groupBox_7 = QGroupBox(self.groupBox_5)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setGeometry(QRect(10, 140, 391, 451))
        self.output_log = QTextBrowser(self.groupBox_7)
        self.output_log.setObjectName(u"output_log")
        self.output_log.setGeometry(QRect(10, 20, 371, 401))
        self.save_log_btn = QPushButton(self.groupBox_7)
        self.save_log_btn.setObjectName(u"save_log_btn")
        self.save_log_btn.setGeometry(QRect(90, 420, 75, 24))
        self.clear_log_btn = QPushButton(self.groupBox_7)
        self.clear_log_btn.setObjectName(u"clear_log_btn")
        self.clear_log_btn.setGeometry(QRect(10, 420, 75, 24))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Tableau to Power BI Migrator", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Control Panel", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"File Selection", None))
        self.add_files_btn.setText(QCoreApplication.translate("MainWindow", u"Add Files", None))
        self.add_folder_btn.setText(QCoreApplication.translate("MainWindow", u"Add Folder", None))
        self.remove_file_btn.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.clear_files_btn.setText(QCoreApplication.translate("MainWindow", u"Clear All", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Export Settings", None))
        self.browse_export_btn.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Migration Options", None))
        self.preserve_conn.setText(QCoreApplication.translate("MainWindow", u"Preserve Connections", None))
        self.preserve_formatting.setText(QCoreApplication.translate("MainWindow", u"Preserve Formatting", None))
        self.create_log.setText(QCoreApplication.translate("MainWindow", u"Create Log File", None))
        self.include_data.setText(QCoreApplication.translate("MainWindow", u"Include Data", None))
        self.begin_migration_btn.setText(QCoreApplication.translate("MainWindow", u"Begin Migration", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Migration Monitor", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"Info", None))
        self.files_processed.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Files Queued:", None))
        self.files_queued.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Files Processed: ", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Process Time:", None))
        self.process_time.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Failures:", None))
        self.failures.setText("")
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Migration Log", None))
        self.save_log_btn.setText(QCoreApplication.translate("MainWindow", u"Save Log", None))
        self.clear_log_btn.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
    # retranslateUi

