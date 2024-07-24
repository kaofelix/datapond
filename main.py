from pathlib import Path

import duckdb
from qtpy.QtCore import QObject, Signal, Slot
from qtpy.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from table import Table, TableTreeItem


class DB(QObject):
    table_added = Signal(Table)

    def __init__(self):
        super().__init__()
        self.conn = duckdb.connect()
        self.tables = []

    def add_table_from_file(self, path):
        table = Table.from_file(self.conn, path)
        self.tables.append(table)
        self.table_added.emit(table)
        return table

    def sql(self, query):
        result = self.conn.sql(query)
        self._check_for_new_tables()
        return result

    def _check_for_new_tables(self):
        for table in self._table_names():
            if table not in (t.name for t in self.tables):
                table = Table(self.conn, table)
                self.tables.append(table)
                self.table_added.emit(table)

    def _table_names(self):
        return (
            i[0]
            for i in self.conn.sql(
                "SELECT table_name FROM information_schema.tables"
            ).fetchall()
        )


class MainWindow(QWidget):
    tables_tree: QTreeWidget
    query_line_edit: QTextEdit
    submit_query_button: QPushButton

    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = data_dir
        self.db = DB()

        self.tables_tree = QTreeWidget()
        self.db.table_added.connect(self.add_table)

        for csv_path in self.data_dir.glob("*.csv"):
            self.db.add_table_from_file(csv_path)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.tables_tree)
        self.setLayout(top_layout)

        main_layout = QVBoxLayout()
        top_layout.addLayout(main_layout)

        query_layout = QHBoxLayout()
        self.query_line_edit = QTextEdit()
        self.query_line_edit.setPlaceholderText("Enter your SQL query here")
        self.query_line_edit.setAcceptRichText(False)

        query_layout.addWidget(self.query_line_edit)
        self.submit_query_button = QPushButton("Submit Query")
        self.submit_query_button.clicked.connect(self.run_query)
        query_layout.addWidget(self.submit_query_button)

        main_layout.addLayout(query_layout)

        self.results_table = QTableWidget()
        main_layout.addWidget(self.results_table)

    @Slot(Table)
    def add_table(self, table):
        self.tables_tree.addTopLevelItem(TableTreeItem(table))

    def run_query(self):
        query = self.query_line_edit.toPlainText()
        result = self.db.sql(query)

        if result is None:
            return

        results = result.fetchall()
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(results[0]))

        for i, row in enumerate(results):
            for j, value in enumerate(row):
                self.results_table.setItem(i, j, QTableWidgetItem(str(value)))

        self.results_table.resizeColumnsToContents()
        self.results_table.resizeRowsToContents()
        self.results_table.show()


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow(data_dir=Path("data"))
    window.show()
    sys.exit(app.exec_())
