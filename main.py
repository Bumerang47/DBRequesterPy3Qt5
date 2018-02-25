#!-*-coding:utf-8-*-
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QDialog
from PyQt5 import uic
from model import ResultTableModel
import json

(Ui_MainWindow, QMainWindow) = uic.loadUiType('window.ui')
sys._excepthook = sys.excepthook

ICO_PATH_FOLDER = 'icons/folder.png'
ICO_PATH_FOLDER_OPEN = 'icons/folder-open.png'


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


class MainWindow(QMainWindow):
    """MainWindow inherits QMainWindow"""

    def __init__(self, parent=None, db_types=list(), settings=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.settings = QSettings(*settings)
        db_connect = self.settings.value('dbConnect', '')

        # Attach DB types set to CBox
        cb = self.ui.comboBoxDBType
        cb.loadItems(db_types)
        cb.previous_choice = cb.currentText()

        # Model table result init
        app_name = self.settings.applicationName()
        t_model = ResultTableModel(self.ui.tableSQLResult, app_name=app_name)
        self.ui.tableSQLResult.setModel(t_model)

        self.restoreDbConnect(db_connect)
        self.statusBar().showMessage('Ready')

    def onCurrentComboDbChange(self, text):
        """
        Event with changed db_type
        @param text: name to db type
        @return: Set path to connection db field
        """
        cb = self.ui.comboBoxDBType
        path = self.ui.pathDBEdit.text()
        cb.savePreviousPath(path)

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

    def onPushPathDb(self):
        """
        Event for opening dialog to selected file SQLite
        @return: set new path for connection file
        """
        filename = self.ui.pathDBEdit.text()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Open File')
        dialog.setNameFilters(['sqlite (*.sqlite3 *.sqlite *.db)',
                               'All files (*)'])
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            filename = dialog.selectedFiles()[0]
        self.ui.pathDBEdit.setText(filename)
        self.ui.pushPathDbButton.setChecked(False)

    def onPushExecuteSQL(self):
        """
        Event for execute SQL request
        @return:  Filling TavleView or Message with error
        """
        type_db = self.ui.comboBoxDBType.currentText()
        path_db = self.ui.pathDBEdit.text()
        sql_text = self.ui.SQLTextEdit.toPlainText()
        try:
            t_model = self.ui.tableSQLResult.model()
            t_model.connect_db(path_db, type_db.lower())
            status_mes = t_model.execute(sql_text)
            self.statusBar().showMessage(status_mes)
        except Exception as e:
            w_title = "Operation Error"
            w_message = e.args[0]
            if 'errno' in dir(e):
                w_title = str(e.errno)
            if 'msg' in dir(e):
                w_message = str(e.msg)
            show_warning(w_title, w_message)
            # raise

    def getSaveDbConnect(self):
        # Data for writing  to memory OS
        return json.dumps(
            {self.ui.comboBoxDBType.currentText(): self.ui.pathDBEdit.text()}
        )

    def restoreDbConnect(self, path):
        # Loading data last db_type connection from path
        if not path:
            return
        parm = json.loads(path)
        if len(parm) > 0:
            type_db = list(parm.keys())[0]
            self.ui.comboBoxDBType.selectText(type_db)
            self.ui.pathDBEdit.setText(parm[type_db])

    def closeEvent(self, event):
        # Event before close, run saving last connection
        db_connect = self.getSaveDbConnect()
        self.settings.setValue('dbConnect', db_connect)
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


# -----------------------------------------------------#
if __name__ == '__main__':
    # create application
    app = QApplication(sys.argv)
    app.setApplicationName("dbSelect")
    db_type_list = ['SQLite', 'PostgreSQL', 'MySql']
    desc_settings = ('NameCompany', 'ToolName')
    # create widget
    w = MainWindow(settings=desc_settings, db_types=db_type_list)
    w.setWindowTitle('Database Requester')
    w.show()
    # execute application
    sys.exit(app.exec_())
