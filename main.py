from pathlib import Path

from PySide6.QtGui import QAction
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QWidget,
)

from db import DB
from resultview import ResultTable
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

        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        self.setCentralWidget(splitter)

        self.query_input = QueryInput()
        self.query_input.submitted.connect(self.run_query)
        splitter.addWidget(self.query_input)

        self.results_table = ResultTable()
        splitter.addWidget(self.results_table)

        self.log_panel = LogPanel()
        self.db.error_occurred.connect(self.log_panel.append_exception)
        splitter.addWidget(self.log_panel)

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
        self.results_table.show_result(self.db.sql(query))


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
