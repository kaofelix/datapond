import itertools
from typing import Optional

from db import QueryResult
from qtpy.QtWidgets import QTableWidget, QTableWidgetItem
from utils import SignalOnChange


class ResultTable(QTableWidget):
    MAX_ROWS = 1000
    result = SignalOnChange(QueryResult, default=None)

    def __init__(self):
        super().__init__()

    def show_result(self, result: Optional[QueryResult]):
        if result is None:
            return

        self.setRowCount(min(result.n_rows, self.MAX_ROWS))
        self.setColumnCount(result.n_cols)
        self.setHorizontalHeaderLabels(result.columns)

        for i, row in enumerate(itertools.islice(result, self.MAX_ROWS)):
            for j, value in enumerate(row):
                self.setItem(i, j, QTableWidgetItem(str(value)))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.result.value = result
