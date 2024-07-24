from pathlib import Path

import duckdb
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


class MainWindow(QWidget):
    tables_tree: QTreeWidget
    query_line_edit: QTextEdit
    submit_query_button: QPushButton

    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = data_dir
        self.conn = duckdb.connect()

        self.tables_tree = QTreeWidget()
        for csv_path in self.data_dir.glob("*.csv"):
            table = Table.from_file(self.conn, csv_path)
            self.tables_tree.addTopLevelItem(TableTreeItem(table))

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

    def run_query(self):
        query = self.query_line_edit.toPlainText()
        results = self.conn.sql(query).fetchall()

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
