from pathlib import Path

from PySide6.QtGui import QAction
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTreeWidget,
    QWidget,
)

from db import DB
from gui.collapsiblesplitter import CollapsibleSplitter
from gui.logs import LogPanel
from gui.resultview import ResultTable
from gui.tabletree import TableTree


class QueryInput(QWidget):
    submitted = Signal(str)

    query: QPlainTextEdit
    submit: QPushButton

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        font = QFont()
        font.setFamily("Courier New")
        font.setFixedPitch(True)

        self.query = QPlainTextEdit()
        self.query.setPlaceholderText("Enter your SQL query here")
        self.query.setFont(font)

        layout.addWidget(self.query)

        self.submit = QPushButton("Run Query")
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
        self.setWindowTitle("Data Pond")

        self.db = DB()

        file_menu = self.menuBar().addMenu("File")

        self.add_dir_data_source_action = QAction("Add Directory...", self)
        self.add_dir_data_source_action.triggered.connect(self.add_dir_data_source)
        file_menu.addAction(self.add_dir_data_source_action)

        self.tables_tree = TableTree(self.db)
        self._add_to_dock(
            self.tables_tree, "Tables", Qt.DockWidgetArea.LeftDockWidgetArea
        )

        self.query_input = QueryInput()
        self.query_input.submitted.connect(self.run_query)

        self.results_table = ResultTable()

        self.log_panel = LogPanel()
        self.db.error_occurred.connect(self.log_panel.append_exception)

        splitter = CollapsibleSplitter()
        self.setCentralWidget(splitter)

        splitter.add(self.query_input, stretch=1, collapsible=False)
        splitter.add(self.results_table, stretch=2, collapsible=False)
        splitter.add(self.log_panel, stretch=1)

        status_bar = self.statusBar()

        toggle_log_button = QPushButton("Toggle Log")
        status_bar.addPermanentWidget(toggle_log_button)

        toggle_log_button.clicked.connect(
            lambda: splitter.toggle_collapsed(self.log_panel)
        )

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

    def _add_to_dock(self, widget, title, area):
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
