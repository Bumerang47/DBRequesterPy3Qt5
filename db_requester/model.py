from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from db_requester.db_adapter import DbAdapter


class ResultTableModel(QAbstractTableModel):
    """ Minimal and simple model for show to result SQL requests in QTableView

    """

    def __init__(self, parent, app_name=None):
        QAbstractTableModel.__init__(self, parent)
        self.data = []
        self.headers = []
        self.app_name = app_name
        self.db = None
        self.cur = None
        super().__init__(parent)

    def rowCount(self, index=QModelIndex()):
        if not index.isValid():
            return len(self.data)
        return super().rowCount(index)

    def columnCount(self, index=QModelIndex()):
        if not index.isValid():
            return len(self.headers)
        return super().columnCount(index)

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[col]
        return None

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if index.row() + 1 == len(self.data):
                new_data = self.cur.fetchmany()
                if new_data:
                    old_size = len(self.data)
                    self.beginInsertRows(
                        QModelIndex(),
                        old_size,
                        old_size + len(new_data) - 1
                    )
                    self.data.extend(new_data)
                    self.endInsertRows()
            return self.data[index.row()][index.column()]
        return None

    def data_reload(self):
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(self.rowCount(), self.columnCount())
        )
        self.layoutChanged.emit()
        self.parent().resizeColumnsToContents()

    def connect_db(self, conn_param, conn_type):
        if not conn_param and conn_type.lower() == 'sqlite':
            def_db_name = self.app_name
            conn_param = ('file:{}?mode=memory&cache=shared'.format(def_db_name))
        if self.cur is not None:
            self.cur.close()
        self.db = DbAdapter(conn_param, dbtype=conn_type.lower())
        self.cur = self.db.conn.cursor()
        self.cur.arraysize = 10

    def execute(self, command):
        """ execution at db, analog cur.execute on more high
        abstraction with pre-treatment

        """

        self.cur.execute(command)
        if self.cur.description is not None:
            self.headers = [description[0] for description in self.cur.description]
            self.data = self.cur.fetchmany()
            self.data_reload()
