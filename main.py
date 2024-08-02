import itertools
from pathlib import Path

from PySide6.QtGui import QAction
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from db import DB
from tabletree import TableTreeWidget


class LogPanel(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def append_exception(self, e: Exception):
        default_color = self.textColor()
        self.setTextColor(Qt.GlobalColor.red)
        self.append(str(e))
        self.setTextColor(default_color)


class QueryInput(QWidget):
    submitted = Signal(str)

    query: QTextEdit
    submit: QPushButton

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.query = QTextEdit()
        self.query.setPlaceholderText("Enter your SQL query here")
        self.query.setAcceptRichText(False)
        layout.addWidget(self.query)

        self.submit = QPushButton("Submit Query")
        self.submit.clicked.connect(
            lambda: self.submitted.emit(self.query.toPlainText())
        )
        layout.addWidget(self.submit)

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.submitted.emit(self.query.toPlainText())
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    tables_tree: QTreeWidget
    query_input: QueryInput

    def __init__(self):
        super().__init__()
        self.db = DB()

        self.tables_tree = TableTreeWidget(self.db)
        dock = QDockWidget("Tables", self)
        dock.setWidget(self.tables_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        self.add_dir_data_source_action = QAction("Add Directory Data Source", self)
        self.add_dir_data_source_action.triggered.connect(self.add_dir_data_source)

        self.menuBar().addMenu("File").addAction(self.add_dir_data_source_action)

        main_layout = QVBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)

        self.query_input = QueryInput()
        main_layout.addWidget(self.query_input)
        self.query_input.submitted.connect(self.run_query)

        self.results_table = QTableWidget()
        main_layout.addWidget(self.results_table)

        self.log_panel = LogPanel()
        self.db.error_occurred.connect(self.log_panel.append_exception)
        main_layout.addWidget(self.log_panel)

    @property
    def query_line_edit(self):
        return self.query_input.query

    @property
    def submit_query_button(self):
        return self.query_input.submit

    def add_dir_data_source(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        self.db.create_tables_from_data_dir(Path(data_dir))

    def run_query(self, query: str):
        MAX_ROWS = 1000
        result = self.db.sql(query)

        if result is None:
            return

        self.results_table.setRowCount(min(result.n_rows, MAX_ROWS))
        self.results_table.setColumnCount(result.n_cols)

        for i, row in enumerate(itertools.islice(result, MAX_ROWS)):
            for j, value in enumerate(row):
                self.results_table.setItem(i, j, QTableWidgetItem(str(value)))

        self.results_table.resizeColumnsToContents()
        self.results_table.resizeRowsToContents()
        self.results_table.show()


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
