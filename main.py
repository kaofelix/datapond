from pathlib import Path

from PySide6.QtGui import QAction
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QTreeWidget,
)

from db import DB
from gui.plotter import plot_result
from gui.query import QueryView
from gui.tabletree import TableTree


class MainWindow(QMainWindow):
    query_view: QueryView
    tables_tree: QTreeWidget
    plot_result_button: QPushButton

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Pond")
        self.resize(1280, 768)

        self.db = DB.from_connection()

        file_menu = self.menuBar().addMenu("File")

        self.load_files_action = QAction("Open Files...", self)
        self.load_files_action.triggered.connect(self.load_files)
        file_menu.addAction(self.load_files_action)

        self.add_dir_data_source_action = QAction("Add Directory...", self)
        self.add_dir_data_source_action.triggered.connect(self.add_dir_data_source)
        file_menu.addAction(self.add_dir_data_source_action)

        self.tables_tree = TableTree(self.db.schema_tracker)
        self._add_to_dock(
            self.tables_tree, "Tables", Qt.DockWidgetArea.LeftDockWidgetArea
        )

        self.query_view = QueryView(self.db)
        self.setCentralWidget(self.query_view)

        self.plot_result_button = QPushButton("Plot Results")
        self.plot_result_button.clicked.connect(self._plot_result)

        toggle_log_button = QPushButton("Toggle Log")
        toggle_log_button.clicked.connect(self.query_view.toggle_log)

        status_bar = self.statusBar()
        status_bar.addPermanentWidget(toggle_log_button)
        status_bar.addPermanentWidget(self.plot_result_button)

    def load_files(self):
        data_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select one or more files to open",
            "/home",
            "Data Files (*.csv)",
        )
        for data_file in data_files:
            self.db.create_table_from_file(Path(data_file))

    def add_dir_data_source(self):
        data_dir = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        self.db.create_tables_from_data_dir(Path(data_dir))

    def _plot_result(self):
        if self.db.result_model.result is None:
            return

        self._plot_window = plot_result(self.db.result_model.result)
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
