from qtpy.QtCore import Slot
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem

from db import DB, Table


class TableTreeWidget(QTreeWidget):
    def __init__(self, db: DB, parent=None):
        super(TableTreeWidget, self).__init__(parent)
        self.db = db
        self.db.table_added.connect(self.add_table)

    @Slot(Table)
    def add_table(self, table):
        self.addTopLevelItem(TableTreeItem(table))


class TableTreeItem(QTreeWidgetItem):
    def __init__(self, table):
        super().__init__([table.name])
        for column, data_type in table.columns:
            self.addChild(QTreeWidgetItem([column, data_type]))
