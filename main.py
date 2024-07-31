from pathlib import Path

from PySide6.QtGui import QAction
from qtpy.QtCore import Qt
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


class MainWindow(QMainWindow):
    tables_tree: QTreeWidget
    query_line_edit: QTextEdit
    submit_query_button: QPushButton

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

    def add_dir_data_source(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        self.db.create_tables_from_data_dir(Path(data_dir))

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
