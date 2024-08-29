from db import DB, Table
from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem


class TableTree(QTreeWidget):
    def __init__(self, db: DB, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Table", "Type"])
        self.db = db
        self.db.table_added.connect(self.add_table)
        self.db.table_dropped.connect(self.remove_table)

    @Slot(Table)
    def add_table(self, table):
        self.addTopLevelItem(TableTreeItem(table))

    @Slot(Table)
    def remove_table(self, table):
        if match := self.findItems(table.name, Qt.MatchFlag.MatchExactly):
            assert (
                len(match) == 1
            ), f"Invariant violated: table name {table.name} is not unique"

            self.takeTopLevelItem(self.indexOfTopLevelItem(match[0]))


class TableTreeItem(QTreeWidgetItem):
    def __init__(self, table):
        super().__init__([table.name])
        for column, data_type in table.columns:
            self.addChild(QTreeWidgetItem([column, data_type]))
