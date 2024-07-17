from pathlib import Path

import duckdb
from qtpy.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QWidget):
    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = data_dir
        for csv_path in self.data_dir.glob("*.csv"):
            duckdb.sql(
                f"create table {csv_path.stem} as select * from read_csv('{csv_path}')"
            )

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        query_layout = QHBoxLayout()
        self.query_line_edit = QLineEdit()
        query_layout.addWidget(self.query_line_edit)
        self.submit_query_button = QPushButton("Submit Query")
        self.submit_query_button.clicked.connect(self.run_query)
        query_layout.addWidget(self.submit_query_button)

        main_layout.addLayout(query_layout)

        self.results_table = QTableWidget()
        main_layout.addWidget(self.results_table)

    def run_query(self):
        query = self.query_line_edit.text()
        results = duckdb.sql(query).fetchall()

        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(results[0]))

        for i, row in enumerate(results):
            for j, value in enumerate(row):
                self.results_table.setItem(i, j, QTableWidgetItem(str(value)))

        self.results_table.resizeColumnsToContents()
        self.results_table.resizeRowsToContents()
        self.results_table.show()
