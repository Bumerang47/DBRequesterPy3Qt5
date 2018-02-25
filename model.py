from PyQt5.QtCore import QAbstractTableModel, Qt
from db_adapter import DbAdap
from time import time, gmtime, strftime
import re


class ResultTableModel(QAbstractTableModel):
    """
    Minimal and simple model for show to result SQL requests in QTableView
    """

    def __init__(self, parent, data_list=None, header=None, app_name=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.data_list = data_list if data_list is not None else [[]]
        self.header = header if header is not None else []
        self.parent = parent
        self.app_name = app_name
        self.db = None
        self.cur = None

    def rowCount(self, parent=None):
        return len(self.data_list)

    def columnCount(self, parent):
        if len(self.data_list):
            return len(self.data_list[0])
        return 0;

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def data(self, index, role):
        if not index.isValid():
            return None
        value = self.data_list[index.row()][index.column()]
        if role in (Qt.EditRole, Qt.DisplayRole):
            return value

    def set_data_list(self, new_data, new_header=None):
        # Set new data and header
        if not isinstance(new_data, list):
            return

        self.data_list = new_data
        if new_header:
            self.header = new_header

        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()
        self.parent.resizeColumnsToContents()

    def connect_db(self, conn_param, conn_type):
        """
        Method for attachment bd to this model
        @param conn_param: path or config for connection database
        @param conn_type: type db connection
        @return: None. Created are db and cursor in object this model
        """
        if len(conn_param) == 0 and conn_type.lower() == 'sqlite':
            def_db_name = self.app_name
            conn_param = 'file:{}?mode=memory&cache=shared'.format(def_db_name)

        self.db = DbAdap(conn_param, dbtype=conn_type.lower())
        self.cur = self.db.conn.cursor()

    def execute(self, command):
        """execution at db, analog cur.execute on more high  abstraction with pre-treatment
        @command (str): Text for execute
        """

        if re.match(r'INSERT|UPDATE|DELETE|DROP', command):
            exec_sql = """SELECT * FROM ({com}) LIMIT 4000""".format(com=command)
        else:
            exec_sql = command
        self.cur.execute(exec_sql)
        if self.cur.description is not None:
            # Without results be not filling
            start_time = time()
            results = self.cur.fetchall()
            delta_time = round(time() - start_time, 3)

            count_res = 0
            if results is not None or len(results) != 0:
                header = [description[0] for description in self.cur.description]
                self.set_data_list(results, header)
                count_res = len(results)
            res = ("Results {} row(s) --- lead time: {} seconds --- "
                   .format(delta_time, count_res))
        else:
            res = ("Executed successfully --- time now: {} ---"
                   .format(strftime("%H:%M:%S", gmtime())))
            self.db.complete()
        self.db.close()
        return res
