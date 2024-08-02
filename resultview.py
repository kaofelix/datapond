import itertools

from qtpy.QtWidgets import QTableWidget, QTableWidgetItem


class ResultTable(QTableWidget):
    MAX_ROWS = 1000

    def __init__(self):
        super().__init__()

    def show_result(self, result):
        if result is None:
            return

        self.setRowCount(min(result.n_rows, self.MAX_ROWS))
        self.setColumnCount(result.n_cols)

        for i, row in enumerate(itertools.islice(result, self.MAX_ROWS)):
            for j, value in enumerate(row):
                self.setItem(i, j, QTableWidgetItem(str(value)))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.show()
