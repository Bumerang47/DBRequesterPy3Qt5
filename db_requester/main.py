#!-*-coding:utf-8-*-

import sys
import json
from os import path

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QDialog
from PyQt5 import uic
from db_requester.model import ResultTableModel

app_path = path.dirname(__file__)
(Ui_MainWindow, QMainWindow) = uic.loadUiType('/'.join([app_path, 'window.ui']))
sys._excepthook = sys.excepthook

ICO_PATH_FOLDER = 'icons/folder.png'
ICO_PATH_FOLDER_OPEN = 'icons/folder-open.png'


def debug_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = debug_exception_hook


class MainWindow(QMainWindow):
    """MainWindow inherits QMainWindow"""

    def __init__(self, parent=None, db_types=list(), settings=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.settings = QSettings(*settings)
        connect_params = self.settings.value('dbConnect', '')

        # Attach DB types set to CBox
        cb = self.ui.comboBoxDBType
        cb.load_items(db_types)
        cb.previous_choice = cb.currentText()

        self.set_db_params(connect_params)
        self.statusBar().showMessage('Ready')

    def change_currend_database(self, text):
        cb = self.ui.comboBoxDBType
        db_path = self.ui.pathDBEdit.text()
        cb.save_previous_path(db_path)

        if text in cb.combo_db_field_cache:
            self.ui.pathDBEdit.setText(cb.combo_db_field_cache[text])
        else:
            self.ui.pathDBEdit.setText('')
        cb.previous_choice = cb.currentText()

        if cb.currentText().lower() != 'sqlite':
            # For other type connection is not need the file selection
            self.ui.pushPathDbButton.setEnabled(False)
            self.ui.pathDBEdit.setPlaceholderText("")
        else:
            self.ui.pushPathDbButton.setEnabled(True)
            self.ui.pathDBEdit.setPlaceholderText(":memory:")

    def read_file_path_selected(self):
        file_path = self.ui.pathDBEdit.text()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Open File')
        dialog.setNameFilters(['sqlite (*.sqlite3 *.sqlite *.db)', 'All files (*)'])
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            file_path = dialog.selectedFiles()[0]
        self.ui.pathDBEdit.setText(file_path)
        self.ui.pushPathDbButton.setChecked(False)

    def execute_sql(self):
        type_db = self.ui.comboBoxDBType.currentText()
        path_db = self.ui.pathDBEdit.text()
        sql_text = self.ui.SQLTextEdit.toPlainText()
        try:
            # Model table result init
            app_name = self.settings.applicationName()
            model = ResultTableModel(self.ui.tableSQLResult, app_name=app_name)
            model.connect_db(path_db, type_db.lower())
            self.ui.tableSQLResult.setModel(model)
            status_mes = model.execute(sql_text)
            self.statusBar().showMessage(status_mes)
        except Exception as e:
            w_title = "Operation Error"
            w_message = e.args[0]
            if 'errno' in dir(e):
                w_title = str(e.errno)
            if 'msg' in dir(e):
                w_message = str(e.msg)
            show_warning(w_title, w_message)

    @property
    def saved_connection(self):
        """
        connection param for save to memory system
        """

        return json.dumps(
            {self.ui.comboBoxDBType.currentText(): self.ui.pathDBEdit.text()}
        )

    def set_db_params(self, path):
        if not path:
            return
        parm = json.loads(path)
        if len(parm) > 0:
            type_db = list(parm.keys())[0]
            self.ui.comboBoxDBType.setCurrentText(type_db)
            self.ui.pathDBEdit.setText(parm[type_db])

    def closeEvent(self, event):
        # Event before close, run saving last connection
        connect_params = self.saved_connection
        self.settings.setValue('dbConnect', connect_params)
        super(MainWindow, self).closeEvent(event)

    def __del__(self):
        self.ui = None


def show_warning(title, text):
    # # Function to warning an message
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setInformativeText(text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()


def run_application():
    app = QApplication(sys.argv)
    app.setApplicationName("dbSelect")
    db_type_list = ['SQLite', 'PostgreSQL', 'MySql']
    desc_settings = ('NameCompany', 'ToolName')
    w = MainWindow(settings=desc_settings, db_types=db_type_list)
    w.setWindowTitle('Database Requester')
    w.show()
    sys.exit(app.exec_())
