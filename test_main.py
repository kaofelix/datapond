import pytest
from qtpy.QtWidgets import QFileDialog

from main import MainWindow


def test_adding_a_directory_data_source_and_selecting_data(
    app_window: MainWindow, datadir, monkeypatch
):
    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory", classmethod(lambda *_: str(datadir))
    )

    app_window.add_dir_data_source_action.trigger()

    app_window.query_line_edit.setText("select * from people")
    app_window.submit_query_button.click()

    assert app_window.results_table.rowCount() == 2
    assert app_window.results_table.columnCount() == 2
    assert app_window.results_table.item(0, 0).text() == "Alice"
    assert app_window.results_table.item(0, 1).text() == "25"

    assert app_window.tables_tree.topLevelItemCount() == 2


def test_create_and_remove_table(app_window: MainWindow):
    app_window.query_line_edit.setText("CREATE TABLE new_table (name TEXT, age INT)")
    app_window.submit_query_button.click()

    assert app_window.tables_tree.topLevelItemCount() == 1
    assert app_window.tables_tree.topLevelItem(0).text(0) == "new_table"

    app_window.query_line_edit.setText("DROP TABLE new_table")
    app_window.submit_query_button.click()

    assert app_window.tables_tree.topLevelItemCount() == 0


def test_error_logging(app_window: MainWindow):
    app_window.query_line_edit.setText("SELECT * FROM non_existent_table")
    app_window.submit_query_button.click()

    assert (
        "Table with name non_existent_table does not exist"
        in app_window.log_panel.toPlainText()
    )


@pytest.fixture
def app_window(qtbot):
    app_window = MainWindow()
    qtbot.addWidget(app_window)
    yield app_window
