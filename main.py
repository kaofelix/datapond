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
    QTableView,
    QTreeWidget,
    QWidget,
)

from db import DB, QueryResultModel
from gui.collapsiblesplitter import CollapsibleSplitter
from gui.logs import LogPanel
from gui.plotter import plot_result
from gui.tabletree import TableTree


class QueryInput(QWidget):
    submitted = Signal(str)

    query: QPlainTextEdit
    submit: QPushButton
    _plot_result: QWidget

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
    results_table: QTableView
    plot_result_button: QPushButton
    result_model: QueryResultModel

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
        self.query_input.submitted.connect(self._run_query)

        self.results_table = QTableView()
        self.result_model = QueryResultModel()
        self.results_table.setModel(self.result_model)

        self.log_panel = LogPanel()
        self.db.error_occurred.connect(self.log_panel.append_exception)

        splitter = CollapsibleSplitter()
        self.setCentralWidget(splitter)

        splitter.add(self.query_input, stretch=1, collapsible=False)
        splitter.add(self.results_table, stretch=2, collapsible=False)
        splitter.add(self.log_panel, stretch=1)

        status_bar = self.statusBar()

        self.plot_result_button = QPushButton("Plot Results")
        # self.plot_result_button.setEnabled(False)
        status_bar.addPermanentWidget(self.plot_result_button)

        self.plot_result_button.clicked.connect(self._plot_result)

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

    def _run_query(self, query: str):
        result = self.db.sql(query)
        if result is None:
            return

        self.result_model.set_result(result)

    def _plot_result(self):
        if self.result_model.result is None:
            return

        self._plot_window = plot_result(self.result_model)
        self._plot_window.show()

    def _add_to_dock(self, widget, title, area):
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Data Pond")
    parser.add_argument("--datadir", type=Path, help="Directory with CSV files")
    args = parser.parse_args()

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = MainWindow()
    if args.datadir:
        window.db.create_tables_from_data_dir(args.datadir)

    window.show()
    sys.exit(app.exec_())
