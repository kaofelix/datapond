from db import DB
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QTableView,
    QWidget,
)

from gui.collapsiblesplitter import CollapsibleSplitter
from gui.common import HighlightTextEdit
from gui.logs import LogPanel


class QueryInput(QWidget):
    submitted = Signal(str)

    query: QPlainTextEdit
    submit: QPushButton
    _plot_result: QWidget

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.query = HighlightTextEdit()
        self.query.setPlaceholderText("Enter your SQL query here")

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


class QueryView(CollapsibleSplitter):
    query_input: QueryInput
    results_table: QTableView
    log_panel: LogPanel

    def __init__(self, db: DB):
        super().__init__()
        self._db = db

        self.query_input = QueryInput()
        self.query_input.submitted.connect(self._run_query)

        self.results_table = QTableView()
        self.results_table.setModel(self._db.result_model)

        self.log_panel = LogPanel()

        self.add(self.query_input, stretch=1, collapsible=False)
        self.add(self.results_table, stretch=2, collapsible=False)
        self.add(self.log_panel, stretch=1)

        self._db.error_occurred.connect(self.log_panel.append_exception)

    def toggle_log(self):
        self.toggle_collapsed(self.log_panel)

    def _run_query(self, query: str):
        self._db.sql(query)
