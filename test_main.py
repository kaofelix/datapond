import pytest
from qtpy.QtWidgets import QFileDialog

from main import MainWindow


def test_adding_a_directory_data_source_and_selecting_data(
    app_window_driver: "AppWindowDriver", datadir
):
    app_window_driver.add_dir_data_source(datadir)

    app_window_driver.run_query("select * from people")

    app_window_driver.assert_has_results(2)
    app_window_driver.assert_has_tables(2)


def test_create_and_remove_table(app_window_driver: "AppWindowDriver"):
    app_window_driver.run_query("CREATE TABLE new_table (name TEXT, age INT)")

    app_window_driver.assert_has_tables(1)

    app_window_driver.run_query("DROP TABLE new_table")

    app_window_driver.assert_has_tables(0)


def test_error_logging(app_window_driver: "AppWindowDriver"):
    app_window_driver.run_query("SELECT * FROM non_existent_table")

    app_window_driver.assert_log_contains(
        "Table with name non_existent_table does not exist"
    )


class AppWindowDriver:
    def __init__(self, app_window, monkeypatch):
        self.app_window = app_window
        self.monkeypatch = monkeypatch

    def add_dir_data_source(self, path):
        self.monkeypatch.setattr(
            QFileDialog, "getExistingDirectory", classmethod(lambda *_: str(path))
        )

        self.app_window.add_dir_data_source_action.trigger()

    def run_query(self, query):
        self.app_window.query_line_edit.setPlainText(query)
        self.app_window.submit_query_button.click()

    def assert_has_results(self, n):
        assert self.app_window.results_table.rowCount() == n

    def assert_has_tables(self, n):
        assert self.app_window.tables_tree.topLevelItemCount() == n

    def assert_log_contains(self, text):
        assert text in self.app_window.log_panel.toPlainText()


@pytest.fixture
def app_window_driver(qtbot, monkeypatch):
    app_window = MainWindow()
    qtbot.addWidget(app_window)
    return AppWindowDriver(app_window, monkeypatch)
