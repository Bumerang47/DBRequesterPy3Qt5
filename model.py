from PyQt5.QtCore import QAbstractTableModel, Qt


class ResultTableModel(QAbstractTableModel):
    """
    Minimal and simple model for show to result SQL requests in QTableView
    """

    def __init__(self, parent, data_list=None, header=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.data_list = data_list if data_list is not None else [[]]
        self.header = header if header is not None else []
        self.parent = parent

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

    def setDataList(self, new_data, new_header=None):
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
