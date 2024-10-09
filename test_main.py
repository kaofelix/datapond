from unittest import mock

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


def test_plot_results(app_window_driver: "AppWindowDriver", datadir):
    app_window_driver.add_dir_data_source(datadir)

    app_window_driver.run_query("select * from people")
    with mock.patch("main.plot_result") as plot_result_mock:
        app_window_driver.plot_result()

    plot_result_mock.assert_called_with(app_window_driver.results.result)


def test_error_logging(app_window_driver: "AppWindowDriver"):
    app_window_driver.run_query("SELECT * FROM non_existent_table")

    app_window_driver.assert_log_contains(
        "Table with name non_existent_table does not exist"
    )


class AppWindowDriver:
    def __init__(self, app_window: MainWindow, monkeypatch):
        self.app_window = app_window
        self.monkeypatch = monkeypatch

    @property
    def results(self):
        return self.app_window.db.result_model

    @property
    def query_line_edit(self):
        return self.app_window.query_view.query_input.query

    @property
    def submit_query_button(self):
        return self.app_window.query_view.query_input.submit

    @property
    def log_panel(self):
        return self.app_window.query_view.log_panel

    def add_dir_data_source(self, path):
        self.monkeypatch.setattr(
            QFileDialog, "getExistingDirectory", classmethod(lambda *_: str(path))
        )

        self.app_window.add_dir_data_source_action.trigger()

    def run_query(self, query):
        self.query_line_edit.setPlainText(query)
        self.submit_query_button.click()

    def plot_result(self):
        self.app_window.plot_result_button.click()

    def assert_has_results(self, n):
        assert self.app_window.db.result_model.rowCount() == n

    def assert_has_tables(self, n):
        assert self.app_window.tables_tree.topLevelItemCount() >= n

    def assert_log_contains(self, text):
        assert text in self.log_panel.toPlainText()


@pytest.fixture
def app_window_driver(qtbot, monkeypatch):
    app_window = MainWindow()
    qtbot.addWidget(app_window)
    return AppWindowDriver(app_window, monkeypatch)
